import uuid
from app.models import ReportGenieRequest, ReportGenieResponse, ReportGenieSection, ReportGenieOutline, Source, KnowledgeBase, EmbeddingModel
from pathlib import Path
import re
import tempfile
import zipfile
from io import BytesIO
from datetime import datetime

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.services.knowledgebases import get_embedding_model
from app.services.embeddings import load_embeddings_model
from app.services.llms import get_default_llm

from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma

router = APIRouter(prefix="/reportgenie", tags=["reportgenie"])

@router.post("/generate", response_model=ReportGenieResponse)
async def generate_report(
    session: SessionDep,
    current_user: CurrentUser,
    request: ReportGenieRequest = Depends(),
):
    """
    Generate a report based on sections outline and knowledge base search results.
    """
    try:
        # 1. Retrieve knowledge base from database
        kb = session.get(KnowledgeBase, request.knowledge_base_id)
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        if kb.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="You don't have access to this knowledge base")
        
        # 2. Create a temporary directory for ChromaDB
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the zipped ChromaDB into the temp directory
            if kb.data:
                with zipfile.ZipFile(BytesIO(kb.data), 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
            else:
                raise HTTPException(status_code=400, detail="Knowledge base has no vector database data")
            
            # 3. Load the vector database with the same model used to create the KB
            if kb.embedding_model_id:
                embedding_model = session.get(EmbeddingModel, kb.embedding_model_id)
                if embedding_model:
                    model_id = embedding_model.model_id
                    provider = embedding_model.provider
                    print(f"Using knowledge base's original embedding model: {model_id}")
                else:
                    embedding_info = get_embedding_model(session)
                    model_id = embedding_info["model_id"]
                    provider = embedding_info["provider"]
            else:
                embedding_info = get_embedding_model(session)
                model_id = embedding_info["model_id"]
                provider = embedding_info["provider"]
                
            print(f"Initializing embedding model: {model_id} ({provider})")
            embeddings = load_embeddings_model(
                provider=provider,
                model_id=model_id
            )
            chroma_db = Chroma(persist_directory=temp_dir, embedding_function=embeddings)
            retriever = chroma_db.as_retriever(search_kwargs={"k": 5})
            
            # 4. Initialize the LLM
            llm = get_default_llm(session)
            
            # 5. Parse the sections outline
            section_list = request.sections.strip().split('\n')
            
            # 6. Process each section
            sections = []
            
            for section_description in section_list:
                section_description = section_description.strip()
                if not section_description:
                    continue
                
                # Retrieve relevant context from the knowledge base
                docs = retriever.get_relevant_documents(section_description)
                context = "\n\n".join([doc.page_content for doc in docs])
                
                # Store source documents for citation
                source_citations = []
                for doc in docs:
                    metadata = doc.metadata.copy()
                    
                    if 'source' in metadata and isinstance(metadata['source'], str):
                        source_path = metadata['source']
                        raw_filename = Path(source_path).name
                        
                        # Extract the real filename after the underscore using regex
                        match = re.search(r'^[^_]*_(.+)$', raw_filename)
                        if match:
                            filename = match.group(1)
                        else:
                            filename = raw_filename
                        
                        source_entry = session.exec(
                            select(Source)
                            .where(Source.name == filename)
                        ).first()
                        
                        if source_entry:
                            metadata['source_data_id'] = str(source_entry.source_data_id)
                    
                    source = {
                        "content": doc.page_content,
                        "metadata": metadata
                    }
                    source_citations.append(source)
                
                # Generate section content using the template
                is_replicate_model = hasattr(llm, '__class__') and 'ReplicateWrapper' in llm.__class__.__name__
                
                # Use the template from config
                prompt_template = settings.REPORT_GENIE_PROMPT_TEMPLATE
                
                if is_replicate_model:
                    formatted_prompt = prompt_template.format(
                        context=context,
                        question=section_description
                    )
                    section_content = llm.invoke(formatted_prompt)
                else:
                    # Standard LangChain approach
                    section_prompt = ChatPromptTemplate.from_template(prompt_template)
                    section_chain = section_prompt | llm
                    section_response = section_chain.invoke({
                        "context": context, 
                        "question": section_description
                    })
                    section_content = section_response.content
                
                # Store the section with its content and sources
                sections.append({
                    "title": section_description,
                    "content": section_content,
                    "source_citations": source_citations
                })
            
            # 7. Compile the final report
            full_report = "\n\n".join([
                f"# {section['title']}\n\n{section['content']}"
                for section in sections
            ])
            
            result = {
                "full_report": full_report,
                "sections": sections
            }
            
            return ReportGenieResponse(results=result)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
    
# Functions related to Outlines
@router.post("/outlines", response_model=ReportGenieOutline)
def create_outline(outline: ReportGenieOutline, session: SessionDep, current_user: CurrentUser):
    """
    Save a new outline to the database.
    """
    existing_outline = session.exec(select(ReportGenieOutline).where(ReportGenieOutline.name == outline.name)).first()
    if existing_outline:
        raise HTTPException(status_code=400, detail="An outline with this name already exists.")
    
    outline.owner_id = current_user.id
    session.add(outline)
    session.commit()
    session.refresh(outline)
    return outline


@router.get("/outlines", response_model=List[ReportGenieOutline])
def get_outlines(session: SessionDep, current_user: CurrentUser):
    """
    Retrieve all outlines from the database for this user.
    """
    print(f"Retrieving outlines for user {current_user.id}")
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    
    try:
        outlines = session.exec(
            select(ReportGenieOutline).where(ReportGenieOutline.owner_id == current_user.id)
        ).all()
        
        # Print the retrieved outlines for debugging
        print(f"Found {len(outlines)} outlines for user {current_user.id}:")
        for i, outline in enumerate(outlines):
            try:
                section_count = len(outline.sections.split('\n')) if outline.sections else 0
                print(f"  {i+1}. ID: {outline.id}, Name: {outline.name}, Sections: {section_count} sections")
            except Exception as e:
                print(f"  {i+1}. ID: {outline.id}, Error processing outline: {str(e)}")
        
        return outlines
    except Exception as e:
        print(f"Error retrieving outlines: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving outlines: {str(e)}")


@router.get("/outlines/{outline_id}", response_model=ReportGenieOutline)
def get_outline(outline_id: uuid.UUID, session: SessionDep):
    """
    Retrieve a specific outline by ID.
    """
    outline = session.get(ReportGenieOutline, outline_id)
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found.")
    return outline

@router.put("/outlines/{outline_id}", response_model=ReportGenieOutline)
def update_outline(outline_id: uuid.UUID, updated_outline: ReportGenieOutline, session: SessionDep, current_user: CurrentUser):
    """
    Update an existing outline.
    """
    outline = session.get(ReportGenieOutline, outline_id)
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found.")
    
    # Ensure the current user is the owner of the outline
    if outline.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this outline.")
    
    outline.name = updated_outline.name
    outline.description = updated_outline.description
    outline.sections = updated_outline.sections
    outline.date_modified = datetime.utcnow()
    
    session.add(outline)
    session.commit()
    session.refresh(outline)
    return outline


@router.delete("/outlines/{outline_id}")
def delete_outline(outline_id: uuid.UUID, session: SessionDep, current_user: CurrentUser):
    """
    Delete an outline by ID.
    """
    outline = session.get(ReportGenieOutline, outline_id)
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found.")
    
    # Ensure the current user is the owner of the outline
    if outline.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this outline.")
    
    session.delete(outline)
    session.commit()
    return {"message": "Outline deleted successfully."}