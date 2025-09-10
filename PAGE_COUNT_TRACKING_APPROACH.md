# Page Count Tracking Implementation Approach

## Overview

This document outlines a comprehensive approach for implementing page counting functionality in the AiBeniq application. The system currently stores sources and knowledge bases in separate PostgreSQL tables, and we need to add page counting capabilities that work across multiple document formats (PDF, DOCX, TXT).

## Current Architecture Analysis

### Database Structure
- **KnowledgeBase Table** (`knowledge-bases`): Stores KB metadata and compressed vector database
- **Source Table** (`sources`): Stores source metadata with references to knowledge bases
- **SourceData Table** (`source-data`): Stores actual file content as compressed ZIP data

### Document Processing Flow
1. Files uploaded through knowledge base creation/update endpoints
2. Text extracted using unified document processing (`document_utils.py`)
3. Documents split into chunks and stored in ChromaDB vector database
4. File content compressed and stored in `SourceData` table
5. Metadata stored in `Source` table with foreign key to `SourceData`

## Implementation Strategy

### 1. Database Schema Changes

#### 1.1 Add Page Count Columns

**Alembic Migration**: `add_page_count_columns_to_sources_and_kb.py`

```sql
-- Add page_count column to sources table
ALTER TABLE sources ADD COLUMN page_count INTEGER DEFAULT 0;

-- Add total_pages column to knowledge-bases table  
ALTER TABLE "knowledge-bases" ADD COLUMN total_pages INTEGER DEFAULT 0;

-- Add index for performance
CREATE INDEX idx_sources_page_count ON sources(page_count);
CREATE INDEX idx_knowledge_bases_total_pages ON "knowledge-bases"(total_pages);
```

#### 1.2 Migration Script Structure

```python
"""Add page count columns to sources and knowledge bases

Revision ID: <new_uuid>
Revises: <latest_revision>
Create Date: <timestamp>
"""

def upgrade():
    # Add page_count to sources table
    op.add_column('sources', sa.Column('page_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Add total_pages to knowledge-bases table
    op.add_column('knowledge-bases', sa.Column('total_pages', sa.Integer(), nullable=False, server_default='0'))
    
    # Add indexes for performance
    op.create_index('idx_sources_page_count', 'sources', ['page_count'])
    op.create_index('idx_knowledge_bases_total_pages', 'knowledge-bases', ['total_pages'])

def downgrade():
    op.drop_index('idx_knowledge_bases_total_pages', 'knowledge-bases')
    op.drop_index('idx_sources_page_count', 'sources')
    op.drop_column('knowledge-bases', 'total_pages')
    op.drop_column('sources', 'page_count')
```

### 2. Page Counting Logic Implementation

#### 2.1 Create Page Counting Service

**New File**: `backend/app/services/page_counter.py`

```python
"""
Page counting utilities for different document types.
"""
import tempfile
import os
from pathlib import Path
from typing import Tuple
import pypdf
from docx import Document as DocxDocument
from io import BytesIO


class PageCounter:
    @staticmethod
    def count_pages_from_bytes(file_content: bytes, filename: str) -> int:
        """
        Count pages in a document from its byte content.
        
        Args:
            file_content: Raw bytes of the document
            filename: Original filename to determine document type
            
        Returns:
            Number of pages in the document
        """
        file_ext = Path(filename).suffix.lower()
        
        if file_ext == ".pdf":
            return PageCounter._count_pdf_pages(file_content, filename)
        elif file_ext in [".docx"]:
            return PageCounter._count_docx_pages(file_content, filename)
        elif file_ext in [".txt", ".md"]:
            return PageCounter._count_text_pages(file_content, filename)
        else:
            # For unknown file types, default to 1 page
            return 1
    
    @staticmethod
    def _count_pdf_pages(file_content: bytes, filename: str) -> int:
        """Count pages in a PDF document."""
        try:
            pdf_reader = pypdf.PdfReader(BytesIO(file_content))
            return len(pdf_reader.pages)
        except Exception as e:
            print(f"Error counting PDF pages for {filename}: {e}")
            return 1  # Default fallback
    
    @staticmethod
    def _count_docx_pages(file_content: bytes, filename: str) -> int:
        """
        Count pages in a DOCX document.
        Note: DOCX doesn't have explicit page breaks, so we estimate based on content.
        """
        try:
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                doc = DocxDocument(temp_file_path)
                
                # Method 1: Use page break elements (most accurate)
                page_breaks = 0
                for paragraph in doc.paragraphs:
                    for run in paragraph.runs:
                        if 'w:br' in run._element.xml and 'type="page"' in run._element.xml:
                            page_breaks += 1
                
                # If explicit page breaks found, use them (+1 for first page)
                if page_breaks > 0:
                    return page_breaks + 1
                
                # Method 2: Estimate based on content length
                total_chars = sum(len(p.text) for p in doc.paragraphs)
                
                # Rough estimation: ~2000 characters per page (adjustable)
                estimated_pages = max(1, (total_chars + 1999) // 2000)
                
                return estimated_pages
                
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            print(f"Error counting DOCX pages for {filename}: {e}")
            return 1  # Default fallback
    
    @staticmethod
    def _count_text_pages(file_content: bytes, filename: str) -> int:
        """Count pages in a text document based on content length."""
        try:
            # Try UTF-8 first, fallback to latin-1
            try:
                text = file_content.decode('utf-8')
            except UnicodeDecodeError:
                text = file_content.decode('latin-1')
            
            # Count explicit page breaks (form feed characters)
            explicit_breaks = text.count('\f')
            if explicit_breaks > 0:
                return explicit_breaks + 1
            
            # Estimate based on line count (rough: ~50 lines per page)
            lines = text.count('\n') + 1
            estimated_pages = max(1, (lines + 49) // 50)
            
            return estimated_pages
            
        except Exception as e:
            print(f"Error counting text pages for {filename}: {e}")
            return 1  # Default fallback
```

#### 2.2 Update Models

**File**: `backend/app/models.py`

```python
# Update Source model
class Source(SQLModel, table=True):
    __tablename__ = "sources"
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    source_data_id: uuid.UUID = Field(foreign_key="source-data.id", nullable=False)
    knowledge_base_id: uuid.UUID = Field(
        foreign_key="knowledge-bases.id",
        nullable=False,
        ondelete="CASCADE",
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    name: str = Field(max_length=255)
    page_count: int = Field(default=0)  # NEW FIELD
    date_created: datetime = Field(default_factory=datetime.utcnow)

# Update KnowledgeBase model
class KnowledgeBase(KnowledgeBaseBase, table=True):
    # ... existing fields ...
    total_pages: int = Field(default=0)  # NEW FIELD
    
# Update KnowledgeBasePublic model
class KnowledgeBasePublic(KnowledgeBaseBase):
    # ... existing fields ...
    total_pages: int = Field(default=0)  # NEW FIELD
```

### 3. Integration Points

#### 3.1 Update Source Creation Service

**File**: `backend/app/services/knowledgebases.py`

```python
class KnowledgeBaseService:
    @staticmethod
    def create_source_entries(
        *,
        session: Session,
        current_user: CurrentUser,
        knowledge_base_id: uuid.UUID,
        file: UploadFile,
    ) -> None:
        """Create source and source_data entries with page counting."""
        from app.services.page_counter import PageCounter
        
        file_content = file.file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # COUNT PAGES FOR THIS FILE
        page_count = PageCounter.count_pages_from_bytes(file_content, file.filename)
        
        # Check if this file hash already exists
        existing_source_data = session.exec(
            select(SourceData).where(SourceData.file_hash == file_hash)
        ).first()

        if existing_source_data:
            # Create only a new source entry using existing source_data
            source = Source(
                source_data_id=existing_source_data.id,
                owner_id=current_user.id,
                name=file.filename,
                knowledge_base_id=knowledge_base_id,
                page_count=page_count,  # NEW FIELD
            )
            session.add(source)
        else:
            # Create new source_data and source entries
            # ... existing code ...
            source = Source(
                source_data_id=source_data_id,
                owner_id=current_user.id,
                name=file.filename,
                knowledge_base_id=knowledge_base_id,
                page_count=page_count,  # NEW FIELD
            )
            session.add(source)
        
        # Update knowledge base total pages
        KnowledgeBaseService.recalculate_total_pages(session, knowledge_base_id)
        
        file.file.seek(0)
        
    @staticmethod
    def recalculate_total_pages(session: Session, knowledge_base_id: uuid.UUID) -> None:
        """Recalculate total pages for a knowledge base."""
        total_pages = session.exec(
            select(func.sum(Source.page_count)).where(
                Source.knowledge_base_id == knowledge_base_id
            )
        ).one() or 0
        
        kb = session.get(KnowledgeBase, knowledge_base_id)
        if kb:
            kb.total_pages = total_pages
            session.add(kb)
```

#### 3.2 Update Knowledge Base Creation/Update Endpoints

**File**: `backend/app/api/routes/knowledgebases.py`

```python
# In create_knowledge_base function
@router.post("/", response_model=KnowledgeBasePublic)
def create_knowledge_base(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    knowledge_base_in: KnowledgeBaseCreate = Depends(),
    files: List[UploadFile] = File(...),
) -> Any:
    # ... existing code ...
    
    # After creating sources, recalculate total pages
    KnowledgeBaseService.recalculate_total_pages(session, knowledge_base.id)
    
    # ... rest of function ...

# In update_knowledge_base function  
@router.put("/{id}", response_model=KnowledgeBasePublic)
def update_knowledge_base(
    # ... parameters ...
) -> Any:
    # ... existing code ...
    
    # After adding/removing sources, recalculate total pages
    if files or knowledge_base_in.removed_file_ids:
        KnowledgeBaseService.recalculate_total_pages(session, knowledge_base.id)
    
    # ... rest of function ...
```

### 4. Frontend Integration

#### 4.1 Update Knowledge Base Display Table

**File**: `frontend/src/components/Common/KnowledgeBaseTable.tsx`

```tsx
const TableHeader = ({ hasSelection }: TableHeaderProps) => {
  const { t } = useTranslation()

  return (
    <Table.Header position="sticky" top="0" bg="transparent" zIndex="1">
      <Table.Row>
        <Table.ColumnHeader w="6">
          <span style={{ fontSize: "0.875rem", fontWeight: "medium" }}>
            {hasSelection ? <FiCheck /> : ""}
          </span>
        </Table.ColumnHeader>
        <Table.ColumnHeader style={{ fontSize: "0.875rem", fontWeight: "bold" }}>
          {t("chatbot.knowledgeBaseTableName")}
        </Table.ColumnHeader>
        <Table.ColumnHeader style={{ fontSize: "0.875rem", fontWeight: "bold" }}>
          {t("chatbot.knowledgeBaseTableDescription")}
        </Table.ColumnHeader>
        <Table.ColumnHeader style={{ fontSize: "0.875rem", fontWeight: "bold" }}>
          {t("chatbot.knowledgeBaseTableSources")}
        </Table.ColumnHeader>
        {/* NEW COLUMN */}
        <Table.ColumnHeader style={{ fontSize: "0.875rem", fontWeight: "bold" }}>
          {t("chatbot.knowledgeBaseTablePages")}
        </Table.ColumnHeader>
      </Table.Row>
    </Table.Header>
  )
}

const TableBody = ({ knowledgeBases, selectedId, onRowSelection }: TableBodyProps) => {
  const rows = knowledgeBases.map((kb) => (
    <Table.Row key={kb.id} data-selected={selectedId === kb.id ? "" : undefined}>
      <Table.Cell>
        <Checkbox.Root
          size="sm"
          top="0.5"
          aria-label="Select row"
          checked={selectedId === kb.id}
          onCheckedChange={(changes) => {
            onRowSelection(kb, !!changes.checked)
          }}
        >
          <Checkbox.HiddenInput />
          <Checkbox.Control />
        </Checkbox.Root>
      </Table.Cell>
      <Table.Cell>{kb.title}</Table.Cell>
      <Table.Cell>{kb.description || "No description"}</Table.Cell>
      <Table.Cell>{kb.number_of_sources || 0} sources</Table.Cell>
      {/* NEW CELL */}
      <Table.Cell>{kb.total_pages || 0} pages</Table.Cell>
    </Table.Row>
  ))

  return <Table.Body>{rows}</Table.Body>
}
```

#### 4.2 Update TypeScript Types

**File**: `frontend/src/client/models.ts` (or wherever types are defined)

```typescript
export interface KnowledgeBasePublic {
  // ... existing fields ...
  total_pages?: number;
}
```

#### 4.3 Add Translation Keys

**File**: `frontend/src/translations/*.ts`

```typescript
// Add to translation files
chatbot: {
  // ... existing keys ...
  knowledgeBaseTablePages: "Pages",
  // ... 
}
```

### 5. Data Migration and Backfill Strategy

#### 5.1 Create Data Migration Script

**File**: `backend/app/scripts/backfill_page_counts.py`

```python
"""
Script to backfill page counts for existing sources and knowledge bases.
Run this after the schema migration to populate page counts for existing data.
"""

import asyncio
from sqlmodel import Session, select
from app.core.db import engine
from app.models import Source, SourceData, KnowledgeBase
from app.services.page_counter import PageCounter
from app.services.knowledgebases import KnowledgeBaseService
import zipfile
from io import BytesIO

async def backfill_page_counts():
    """Backfill page counts for all existing sources."""
    
    with Session(engine) as session:
        # Get all sources that need page count updates
        sources = session.exec(
            select(Source).where(Source.page_count == 0)
        ).all()
        
        print(f"Found {len(sources)} sources to update...")
        
        for i, source in enumerate(sources):
            try:
                print(f"Processing {i+1}/{len(sources)}: {source.name}")
                
                # Get the source data
                source_data = session.get(SourceData, source.source_data_id)
                if not source_data:
                    print(f"  ⚠️ No source data found for {source.name}")
                    continue
                
                # Extract file from ZIP
                with zipfile.ZipFile(BytesIO(source_data.data), 'r') as zip_file:
                    file_names = zip_file.namelist()
                    if not file_names:
                        print(f"  ⚠️ Empty ZIP for {source.name}")
                        continue
                    
                    # Get the first (and usually only) file in the ZIP
                    file_content = zip_file.read(file_names[0])
                
                # Count pages
                page_count = PageCounter.count_pages_from_bytes(file_content, source.name)
                
                # Update source
                source.page_count = page_count
                session.add(source)
                
                print(f"  ✅ Updated {source.name}: {page_count} pages")
                
            except Exception as e:
                print(f"  ❌ Error processing {source.name}: {e}")
                continue
        
        # Commit source updates
        session.commit()
        
        # Now recalculate knowledge base totals
        knowledge_bases = session.exec(select(KnowledgeBase)).all()
        
        print(f"\nRecalculating totals for {len(knowledge_bases)} knowledge bases...")
        
        for kb in knowledge_bases:
            try:
                KnowledgeBaseService.recalculate_total_pages(session, kb.id)
                print(f"  ✅ Updated KB: {kb.title}")
            except Exception as e:
                print(f"  ❌ Error updating KB {kb.title}: {e}")
        
        session.commit()
        print("\n🎉 Page count backfill completed!")

if __name__ == "__main__":
    asyncio.run(backfill_page_counts())
```

### 6. Deployment Strategy

#### 6.1 Deployment Steps

1. **Deploy Schema Migration**
   ```bash
   cd backend
   uv run alembic upgrade head
   ```

2. **Run Backfill Script**
   ```bash
   cd backend
   uv run python app/scripts/backfill_page_counts.py
   ```

3. **Deploy Application Code**
   - Backend API changes
   - Frontend UI changes

#### 6.2 Rollback Plan

If issues occur, rollback using the Alembic downgrade:

```bash
cd backend
uv run alembic downgrade -1  # Go back one migration
```

### 7. Testing Strategy

#### 7.1 Unit Tests

**File**: `backend/tests/test_page_counter.py`

```python
import pytest
from app.services.page_counter import PageCounter

def test_pdf_page_counting():
    # Test with sample PDF bytes
    pass

def test_docx_page_counting():
    # Test with sample DOCX bytes  
    pass

def test_text_page_counting():
    # Test with sample text content
    pass
```

#### 7.2 Integration Tests

**File**: `backend/tests/test_knowledge_base_pages.py`

```python
def test_knowledge_base_page_calculation():
    # Test that KB total pages = sum of source pages
    pass

def test_source_page_count_on_upload():
    # Test that uploading a file correctly sets page count
    pass
```

### 8. Performance Considerations

#### 8.1 Database Indexing

- Add indexes on page count columns for efficient sorting/filtering
- Consider composite indexes if filtering by multiple criteria

#### 8.2 Caching Strategy

- Page counts rarely change, good candidates for caching
- Cache at the knowledge base level to avoid recalculation

#### 8.3 Async Processing

- For large files, consider async page counting
- Implement progress tracking for bulk operations

### 9. Monitoring and Observability

#### 9.1 Metrics to Track

- Average page count per knowledge base
- Page counting performance (time taken)
- Page count accuracy (manual verification)

#### 9.2 Error Handling

- Log page counting failures with file details
- Provide fallback values for failed counts
- Alert on high failure rates

### 10. Future Enhancements

#### 10.1 Advanced Page Counting

- More accurate DOCX page estimation using document properties
- Support for additional file formats
- Page break detection in text files

#### 10.2 UI/UX Improvements

- Sort knowledge bases by page count
- Filter by page count ranges
- Progress indicators during upload

#### 10.3 Analytics

- Track page count trends over time
- Knowledge base size analytics
- User upload patterns by document size

## Summary

This comprehensive approach provides:

1. **Robust page counting** across PDF, DOCX, and text files
2. **Efficient database schema** with proper indexing
3. **Automated recalculation** when sources are added/removed
4. **User-friendly display** in the frontend interface
5. **Migration strategy** for existing data
6. **Testing and monitoring** capabilities

The implementation follows the existing codebase patterns and architecture while adding minimal complexity to the system.
