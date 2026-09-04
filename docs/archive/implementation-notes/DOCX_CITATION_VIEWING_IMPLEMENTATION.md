# DOCX Citation Viewing Implementation

## Problem Solved

Previously, when users clicked on DOCX document citations, they couldn't view the documents because the citation viewing functionality was built around PDF display. DOCX files couldn't be displayed directly in the browser's PDF viewer.

## Solution Implemented

### Server-Side DOCX to PDF Conversion

Implemented a robust server-side conversion that maintains the existing PDF-based citation viewing infrastructure.

## Backend Changes

### 1. New Dependencies Added (`backend/pyproject.toml`)

```toml
"mammoth>=1.6.0,<2.0.0",    # DOCX to HTML conversion
"weasyprint>=61.0,<62.0",   # HTML to PDF conversion
```

### 2. New API Endpoint (`backend/app/api/routes/sourceretrieval.py`)

**Endpoint**: `GET /api/v1/files/source/{source_id}/pdf`

**Features**:

- ✅ Converts DOCX files to PDF on-demand
- ✅ Maintains existing security and permission checks
- ✅ Uses mammoth for DOCX → HTML conversion
- ✅ Uses weasyprint for HTML → PDF conversion
- ✅ Professional PDF formatting with CSS styling
- ✅ Proper error handling and cleanup
- ✅ Returns PDF as binary response for direct browser viewing

**Conversion Process**:

1. Validates user access to the source document
2. Checks that the file is actually a DOCX document
3. Extracts DOCX content from ZIP storage
4. Converts DOCX to HTML using mammoth
5. Applies professional CSS styling
6. Converts HTML to PDF using weasyprint
7. Returns PDF with proper headers for browser display

## Frontend Changes

### 1. Enhanced FilesService (`frontend/src/client/sdk.gen.ts`)

**New Method**: `FilesService.convertDocxToPdf()`

- ✅ Returns PDF as Blob for direct browser viewing
- ✅ Proper error handling for conversion failures
- ✅ Same security model as existing file access

### 2. Updated SourceLink Component (`frontend/src/components/Common/SourceLink.tsx`)

**Enhanced Logic**:

- ✅ Automatically detects DOCX files by extension
- ✅ Uses conversion endpoint for DOCX files
- ✅ Falls back to normal viewing for non-DOCX files
- ✅ Handles conversion errors gracefully with fallback
- ✅ Opens converted PDFs in new browser tab
- ✅ Maintains existing functionality for PDF files

## Benefits

### 1. **Seamless User Experience**

- Users can now click on DOCX citations and view them immediately
- No change in user workflow - clicking still opens documents
- Consistent experience across PDF and DOCX citations

### 2. **Maintains Existing Infrastructure**

- No changes needed to PDF viewing components
- Existing modal and tab viewing still works
- Security and permission system unchanged

### 3. **Professional PDF Output**

- High-quality conversion preserves formatting
- Responsive design with proper margins and typography
- Standardized A4 layout for consistent viewing

### 4. **Robust Error Handling**

- Graceful fallback if conversion fails
- Comprehensive logging for debugging
- Proper cleanup of temporary files

### 5. **Performance Optimized**

- Server-side conversion (no client-side processing)
- Efficient binary streaming to browser
- Temporary file cleanup prevents disk bloat

## Usage

### For Users

1. Click any DOCX citation link (same as before)
2. System automatically detects DOCX format
3. Converts to PDF on-demand
4. Opens PDF in browser for viewing
5. Falls back to original method if conversion fails

### For Developers

```typescript
// DOCX files are handled automatically
<SourceLink
  sourceId="123-456-789"
  fileName="document.docx"  // Automatically detects and converts
  useModal={true}
/>

// PDF files work as before
<SourceLink
  sourceId="123-456-789"
  fileName="document.pdf"   // Uses existing PDF viewer
  useModal={true}
/>
```

## Technical Advantages

### 1. **Docker-Compatible Solution**

- Uses pure Python libraries (no external dependencies)
- Works in containerized environments
- No need for Microsoft Word or LibreOffice

### 2. **Scalable Architecture**

- Server-side processing prevents client overload
- Efficient memory usage with temporary files
- Can handle large DOCX documents

### 3. **Future-Proof Design**

- Easy to extend for other document formats
- CSS styling can be customized per requirements
- Conversion pipeline can be enhanced with additional features

## Testing Completed

### ✅ Backend Testing

- DOCX to PDF conversion endpoint working
- Proper permission checks maintained
- Error handling for invalid files
- Temporary file cleanup verified

### ✅ Frontend Testing

- DOCX citation links now clickable and functional
- PDF citations continue to work normally
- Fallback mechanism tested and working
- Loading states and error handling verified

## Future Enhancements

### Potential Improvements

1. **Modal Support**: Enhance modal viewing for converted PDFs
2. **Caching**: Cache converted PDFs to improve performance
3. **Format Support**: Extend to other formats (PPTX, XLSX)
4. **Custom Styling**: Allow per-organization PDF styling
5. **Batch Conversion**: Pre-convert DOCX files during upload

## Deployment Notes

### Dependencies Installed

- `mammoth==1.10.0` - DOCX parsing and HTML conversion
- `weasyprint==61.2` - HTML to PDF conversion with CSS support
- Additional supporting libraries for font rendering and CSS processing

### Configuration

- No additional configuration required
- Uses existing security and permission system
- Inherits all existing logging and monitoring

## Impact

### ✅ Problem Resolved

- DOCX citations are now fully functional and viewable
- Users can access all document types through citations
- Improved document accessibility across the platform

### ✅ Zero Breaking Changes

- Existing PDF functionality unchanged
- All other features continue to work normally
- Backward compatible with existing citations

This implementation provides a complete solution for DOCX citation viewing while maintaining the existing user experience and technical architecture.
