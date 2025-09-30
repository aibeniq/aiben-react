# Full Document Scan Mode - Minimal Text Detection Enhancement

## Implementation Summary

### What Was Changed

Extended the Full Document Scan mode to intelligently choose between text processing and image processing based on document content, similar to Vector Search mode but with different criteria.

### Processing Logic

#### Vector Search Mode (Existing)

- **Text Processing**: For documents with sufficient text content
- **Image Processing**: When either:
  a. Tables are identified (for table extraction)
  b. Very little embedded text is detected (< 500 characters per page)

#### Full Document Scan Mode (Enhanced)

- **Text Processing**: For documents with sufficient text content
- **Image Processing**: When:
  a. Very little embedded text is detected (< 500 characters per page)

Note: NO table detection in Full Document Scan mode since full document context prevents table truncation issues.

### Technical Implementation

#### File Modified

- `backend/app/api/routes/chatbot.py` - Function `_handle_full_text_document_query`

#### Key Changes

1. **Minimal Text Detection Logic** (Lines ~390-430)

   ```python
   # Determine processing strategy: check for minimal text content
   has_minimal_text = False
   total_text_length = sum(len(doc.page_content.strip()) for doc in documents)

   if vision_enabled and file_images:
       # Check if any page has minimal text (< 500 chars) indicating image-heavy content
       for i, doc in enumerate(documents):
           text_length = len(doc.page_content.strip())
           # Check for minimal text OR URL-heavy content that indicates image pages
           if text_length < 500 or is_url_heavy:
               has_minimal_text = True
               break
   ```

2. **Processing Strategy Selection** (Lines ~430-450)

   ```python
   # Choose processing strategy based on text content
   if has_minimal_text:
       # Use image-based processing for minimal text documents
       print(f"📸 Using image processing for {file.filename} due to minimal text content")
       chunks = []  # Skip text chunking
   else:
       # Use traditional text chunking for documents with sufficient text
       print(f"📝 Using text processing for {file.filename} with sufficient embedded text")
       chunks = chunk_text(full_text, max_tokens=settings.FULL_SCAN_DOCUMENT_CHUNK_SIZE)
   ```

3. **Image-Only Processing Branch** (Lines ~570-650)
   ```python
   elif has_minimal_text and vision_enabled and file_images:
       # Use image-only processing for minimal text documents
       print(f"📸 Processing {file.filename} using image-only analysis due to minimal text")

       # Prepare images for processing and use vision analysis as primary method
       vision_analysis = await VisionService.process_images_with_prompt(...)
   ```

### Detection Criteria

The system detects minimal text using the same logic as Vector Search mode:

- **Text Length Threshold**: < 500 characters per page
- **URL-Heavy Content Detection**: Pages with metadata URLs like "https://apastyle.apa.org/..."
- **Content Patterns**: Specific patterns indicating image pages with minimal metadata

### Benefits

1. **Consistent Processing**: OCR-heavy documents now get the same intelligent processing in both modes
2. **Optimal Resource Usage**:
   - Text processing for text-rich documents (faster, more accurate for text)
   - Image processing for image-heavy documents (captures visual content)
3. **Mode-Specific Optimization**:
   - Vector Search: Includes table detection for chunk-level accuracy
   - Full Document Scan: Skips table detection since full context prevents truncation

### Example Use Cases

#### Vector Search Mode

- **Fee schedule PDFs**: Text + table detection → Images for table extraction
- **APA table examples**: Minimal text → Images for visual content
- **Regular documents**: Sufficient text → Text processing

#### Full Document Scan Mode (Enhanced)

- **APA table examples**: Minimal text → Images for visual content
- **Scanned documents**: Minimal embedded text → Images for OCR
- **Regular documents**: Sufficient text → Text processing
- **Table-heavy PDFs**: Sufficient text → Text processing (no table detection needed)

### Testing

To test the new functionality:

1. **Upload APA table example PDF** to chatbot
2. **Select "Full Document Scan" mode**
3. **Ask question**: "How many participants were in the High School/Some College category?"
4. **Expected behavior**:
   - System detects minimal text (< 500 chars per page)
   - Switches to image processing
   - Uses vision analysis to read table content
   - Provides accurate answer from visual table data

### Comparison: Before vs After

#### Before

- Full Document Scan always used text chunking
- Image processing was supplemental (always in addition to text)
- No intelligence about document content type

#### After

- Full Document Scan intelligently chooses processing method
- Image processing can be primary method for minimal text documents
- Smart content detection similar to Vector Search but optimized for full document context

This enhancement ensures that both Vector Search and Full Document Scan modes handle OCR-heavy and image-heavy documents optimally while maintaining their distinct purposes and strengths.
