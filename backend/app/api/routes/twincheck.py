import uuid
import difflib
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import traceback

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from sqlmodel import Session, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    TwinCheckRequest,
    TwinCheckResponse,
    TwinCheckTopicList,
    LlmInteraction,
    TwinCheckRequest,
)
from app.core.config import settings
from app.services.llms import get_default_llm, invoke_llm, record_llm_interaction

router = APIRouter(prefix="/twincheck", tags=["twincheck"])


# Process documents for comparison
@router.post("/compare", response_model=TwinCheckResponse)
async def compare_documents(
    session: SessionDep,
    current_user: CurrentUser,
    request: TwinCheckRequest = Depends(),
    document1: UploadFile = File(...),
    document2: UploadFile = File(...),
):
    """
    Compare two documents based on the provided comparison topics.
    """
    try:
        # Read the file contents
        doc1_content = await document1.read()
        doc2_content = await document2.read()

        # Try to decode as text files
        try:
            doc1_text = doc1_content.decode("utf-8")
            doc2_text = doc2_content.decode("utf-8")
        except UnicodeDecodeError:
            # For binary files like PDFs, you might need to extract text
            # This is a placeholder - implement actual text extraction for your file types
            raise HTTPException(
                status_code=400, detail="Only text files are supported at this time"
            )

        # Split files into lines for diffing
        doc1_lines = doc1_text.splitlines()
        doc2_lines = doc2_text.splitlines()

        # Generate diff using difflib
        differ = difflib.Differ()
        diff_result = list(differ.compare(doc1_lines, doc2_lines))
        diff_text = "\n".join(diff_result)

        # Load the LLM model
        llm = get_default_llm(session, current_user)

        # Parse comparison topics
        topic_list = request.comparison_topics.strip().split("\n")
        topic_analysis = []

        # Process each topic with the LLM
        for topic in topic_list:
            if not topic.strip():
                continue

            # Define prompt template for topic analysis
            prompt_template = settings.TWINCHECK_ANALYSIS_PROMPT_TEMPLATE

            # Generate analysis for this topic
            try:
                topic_result = invoke_llm(
                    llm,
                    prompt_template,
                    {
                        "diff_text": diff_text,
                        "topic": topic,
                        "doc1_name": document1.filename,
                        "doc2_name": document2.filename,
                    },
                )

                # Add to results
                topic_analysis.append({"topic": topic, "analysis": topic_result})

            except Exception as e:
                topic_analysis.append(
                    {
                        "topic": topic,
                        "analysis": f"Error analyzing this topic: {str(e)}",
                    }
                )

        # Create a comprehensive summary
        summary_prompt_template = settings.TWINCHECK_SUMMARY_PROMPT_TEMPLATE
        summary = invoke_llm(
            llm,
            summary_prompt_template,
            {
                "diff_text": diff_text,
                "doc1_name": document1.filename,
                "doc2_name": document2.filename,
                "topics": request.comparison_topics,
            },
        )

        # Record this interaction for history
        interaction_id = record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="twincheck",
            input_data={
                "comparison_topics": request.comparison_topics,
                "document1_name": document1.filename,
                "document2_name": document2.filename,
            },
            output_data={"summary": summary, "topic_count": len(topic_analysis)},
            metadata={
                "topic_analysis": topic_analysis,  # Store detailed analysis for retrieval
                "diff_stats": {
                    "additions": diff_text.count("\n+ "),
                    "deletions": diff_text.count("\n- "),
                    "changes": diff_text.count("\n? "),
                },
            },
        )

        # Return the results
        result = {
            "summary": summary,
            "topic_analysis": topic_analysis,
            "interaction_id": str(interaction_id) if interaction_id else None,
        }

        return TwinCheckResponse(results=result)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error comparing documents: {str(e)}"
        )


# Get history of comparison operations
@router.get("/history", response_model=List[Dict[str, Any]])
async def get_comparison_history(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 20,
):
    """Retrieve past document comparison history for the current user."""
    try:
        comparisons = session.exec(
            select(LlmInteraction)
            .where(
                LlmInteraction.user_id == current_user.id,
                LlmInteraction.functionality == "twincheck",
            )
            .order_by(LlmInteraction.date_created.desc())
            .offset(skip)
            .limit(limit)
        ).all()

        result = []
        for comparison in comparisons:
            try:
                input_data = (
                    json.loads(comparison.input_data) if comparison.input_data else {}
                )
                output_data = (
                    json.loads(comparison.output_data) if comparison.output_data else {}
                )

                result.append(
                    {
                        "id": str(comparison.id),
                        "date_created": comparison.date_created,
                        "document1_name": input_data.get(
                            "document1_name", "Unknown Document 1"
                        ),
                        "document2_name": input_data.get(
                            "document2_name", "Unknown Document 2"
                        ),
                        "comparison_topics": input_data.get("comparison_topics", ""),
                        "topic_count": output_data.get("topic_count", 0),
                        "has_feedback": comparison.feedback is not None,
                    }
                )
            except json.JSONDecodeError:
                # If JSON parsing fails, use minimal information
                result.append(
                    {
                        "id": str(comparison.id),
                        "date_created": comparison.date_created,
                        "document1_name": "Unknown Document 1",
                        "document2_name": "Unknown Document 2",
                        "topic_count": 0,
                        "has_feedback": comparison.feedback is not None,
                    }
                )

        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving comparison history: {str(e)}"
        )


# Get details of a specific comparison
@router.get("/history/{comparison_id}")
async def get_comparison_detail(
    comparison_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Retrieve a specific comparison's full content by ID."""
    try:
        comparison = session.get(LlmInteraction, comparison_id)
        if not comparison:
            raise HTTPException(status_code=404, detail="Comparison not found")

        if comparison.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You don't have access to this comparison"
            )

        if comparison.functionality != "twincheck":
            raise HTTPException(
                status_code=400, detail="This is not a TwinCheck comparison"
            )

        try:
            input_data = (
                json.loads(comparison.input_data) if comparison.input_data else {}
            )
            output_data = (
                json.loads(comparison.output_data) if comparison.output_data else {}
            )
            extra_data = comparison.extra_data or {}

            # Create a response that matches the structure expected by the frontend
            result = {
                "id": str(comparison.id),
                "date_created": comparison.date_created,
                "document1_name": input_data.get(
                    "document1_name", "Unknown Document 1"
                ),
                "document2_name": input_data.get(
                    "document2_name", "Unknown Document 2"
                ),
                "comparison_topics": input_data.get("comparison_topics", ""),
                "results": {
                    "summary": output_data.get("summary", ""),
                    "topic_analysis": extra_data.get("topic_analysis", []),
                    "interaction_id": str(comparison.id),
                },
                # Add feedback information
                "feedback": {
                    "feedback": comparison.feedback,
                    "feedbackText": comparison.feedback_text,
                    "feedbackDate": (
                        comparison.feedback_date.isoformat()
                        if comparison.feedback_date
                        else None
                    ),
                },
            }

            return result

        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "id": str(comparison.id),
                "date_created": comparison.date_created,
                "document1_name": "Unknown Document 1",
                "document2_name": "Unknown Document 2",
                "results": {
                    "summary": "Unable to reconstruct comparison from this record. This might be due to an older format or incomplete data.",
                    "topic_analysis": [],
                },
                # Add empty feedback object for consistency
                "feedback": {
                    "feedback": None,
                    "feedbackText": None,
                    "feedbackDate": None,
                },
            }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving comparison details: {str(e)}"
        )


# Functions related to Comparisons (saved comparison topics)
@router.post("/comparisons", response_model=TwinCheckTopicList)
def create_comparison(
    comparison: TwinCheckTopicList, session: SessionDep, current_user: CurrentUser
):
    """
    Save a new comparison topic set to the database.
    """
    existing_comparison = session.exec(
        select(TwinCheckTopicList).where(TwinCheckTopicList.name == comparison.name)
    ).first()

    if existing_comparison:
        raise HTTPException(
            status_code=400, detail="A comparison with this name already exists."
        )

    comparison.owner_id = current_user.id
    session.add(comparison)
    session.commit()
    session.refresh(comparison)
    return comparison


@router.get("/comparisons", response_model=List[TwinCheckTopicList])
def get_comparisons(session: SessionDep, current_user: CurrentUser):
    """
    Retrieve all saved comparison topic sets from the database for this user.
    """
    return session.exec(
        select(TwinCheckTopicList).where(TwinCheckTopicList.owner_id == current_user.id)
    ).all()


@router.get("/comparisons/{comparison_id}", response_model=TwinCheckTopicList)
def get_comparison(comparison_id: uuid.UUID, session: SessionDep):
    """
    Retrieve a specific comparison topic set by ID.
    """
    comparison = session.get(TwinCheckTopicList, comparison_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found.")
    return comparison


@router.put("/comparisons/{comparison_id}", response_model=TwinCheckTopicList)
def update_comparison(
    comparison_id: uuid.UUID,
    updated_comparison: TwinCheckTopicList,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Update an existing comparison topic set.
    """
    comparison = session.get(TwinCheckTopicList, comparison_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found.")

    # Ensure the current user is the owner of the comparison
    if comparison.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this comparison."
        )

    comparison.name = updated_comparison.name
    comparison.description = updated_comparison.description
    comparison.topics = updated_comparison.topics
    comparison.date_modified = datetime.utcnow()

    session.add(comparison)
    session.commit()
    session.refresh(comparison)
    return comparison


@router.delete("/comparisons/{comparison_id}")
def delete_comparison(
    comparison_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
):
    """
    Delete a comparison topic set by ID.
    """
    comparison = session.get(TwinCheckTopicList, comparison_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found.")

    # Ensure the current user is the owner of the comparison
    if comparison.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this comparison."
        )

    session.delete(comparison)
    session.commit()
    return {"message": "Comparison deleted successfully."}
