# Multiple Document Chatbot Implementation

## Overview

The chatbot has been successfully updated to support uploading and querying multiple documents simultaneously. This enhancement works with both Vector Search and Full Text Scan modes.

## Backend Changes

### 1. API Endpoint Updates (`backend/app/api/routes/chatbot.py`)

#### Modified `query_document` endpoint:

- **Changed parameter**: `file: UploadFile = File(None)` → `files: List[UploadFile] = File(None)`
- **Updated validation**: Now requires at least one file for initial questions (not follow-ups)
- **Enhanced error handling**: Better error messages for multiple file scenarios

#### Vector Search Mode:

- **Combined processing**: All uploaded files are processed together into a single ChromaDB instance
- **Metadata tracking**: Each document chunk retains its source filename in metadata
- **Unified retrieval**: Single retriever searches across all documents simultaneously
- **Session caching**: Maintains session state for follow-up questions

#### Full Text Scan Mode (`_handle_full_text_document_query`):

- **Independent processing**: Each document is analyzed separately using the chunking method
- **Document-level synthesis**: Individual document analyses are created first
- **Multi-document compilation**: If multiple documents have relevant information, an additional synthesis step combines insights across documents
- **Smart handling**: Single document responses bypass the compilation step for efficiency

### 2. Enhanced Features:

- **File source tracking**: Better metadata handling for source citations
- **Error handling**: Comprehensive cleanup of temporary files
- **Logging**: Improved debug information for multi-document processing

## Frontend Changes

### 1. State Management Updates (`frontend/src/components/Chatbot/ChatbotMain.tsx`)

- **Changed state**: `uploadedFile: File | null` → `uploadedFiles: File[]`
- **Updated tracking**: `currentFileName: string | null` → `currentFileNames: string[]`
- **API integration**: Updated to use the new multiple files API endpoint

### 2. User Interface Enhancements

#### ChatbotPanel (`frontend/src/components/Chatbot/ChatbotPanel.tsx`)

- **Status display**: Shows count and names of uploaded documents
- **Smart messaging**: "Using 3 documents: file1.pdf, file2.txt, file3.docx"
- **Cleanup actions**: Properly clears all files when switching to knowledge base mode

#### InputArea (`frontend/src/components/Chatbot/InputArea.tsx`)

- **Multiple selection**: File input now accepts multiple files with `multiple` attribute
- **File type restrictions**: Limited to `.pdf,.txt,.docx,.doc,.rtf` for better UX
- **Size validation**: 10MB limit per file with user feedback
- **Success feedback**: Toast notifications when files are selected
- **Error handling**: Alerts for oversized files

#### ChatMessages (`frontend/src/components/Chatbot/ChatMessages.tsx`)

- **Multiple file awareness**: Updated placeholder text to handle multiple documents
- **Source display**: Properly handles sources from multiple documents

### 3. API Integration

- **Updated client calls**: Uses new `{ files: uploadedFiles }` format
- **Backward compatibility**: Maintains support for follow-up questions without re-uploading files

## User Experience Flow

### Uploading Documents:

1. User clicks the file attachment icon in the chat input
2. Can select multiple documents (PDF, TXT, DOCX, DOC, RTF)
3. Files are validated for size (10MB limit each)
4. Success toast shows number of files selected
5. Status bar shows document count and names

### Vector Search Mode:

1. All documents are combined into a single searchable index
2. User asks questions that search across all documents
3. Results include sources from any relevant document
4. Follow-up questions use cached index for speed

### Full Text Scan Mode:

1. Each document is analyzed independently
2. Question is asked against each document's chunks
3. Individual document analyses are created
4. If multiple documents have relevant info, they're synthesized
5. Single document results skip synthesis for efficiency

### Session Management:

- Session IDs maintained for follow-up questions
- Changing documents clears session and creates new one
- Cached resources improve response times for follow-ups

## Technical Benefits

1. **Scalability**: Handles 1-N documents with the same interface
2. **Performance**: Vector search benefits from combined indexing
3. **Accuracy**: Full text scan provides comprehensive analysis across documents
4. **User Experience**: Seamless multi-document workflow
5. **Backward Compatibility**: Existing single-document workflows unchanged

## File Format Support

- **PDF**: Full text extraction and chunking
- **TXT**: Direct text processing
- **DOCX/DOC**: Document text extraction
- **RTF**: Rich text format support

## Configuration

- **Max files**: No hard limit (reasonable UX limits apply)
- **File size**: 10MB per file
- **Chunk size**: Configurable via settings (FULL_SCAN_DOCUMENT_CHUNK_SIZE)
- **Vector chunks**: 1000 characters with 200 overlap
- **Full text chunks**: Configurable large chunks for comprehensive analysis

## Error Handling

- File size validation with user feedback
- Temporary file cleanup on errors
- Session state recovery for follow-ups
- Graceful degradation for unsupported files

This implementation provides a robust, scalable solution for multi-document AI chatbot queries while maintaining excellent user experience and performance.
