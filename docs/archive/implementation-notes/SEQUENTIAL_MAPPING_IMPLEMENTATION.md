# Sequential Ground-Truth Mapping Implementation

## Overview

Completely redesigned the `optimize_outline()` function to use sequential mapping instead of retrieval-based comparison. This provides a more structured and logical approach to comparing generated content with ground-truth documents.

## Key Changes

### 1. **Removed Retriever-Based Approach**

**Before:**

- Used `retriever.get_relevant_documents(section_description)` to find relevant snippets
- Searched for keywords and used vector similarity
- Could miss sequential structure and context

**After:**

- Process ground-truth document sequentially in chunks
- Use AI to intelligently map each chunk to appropriate outline sections
- Preserves document structure and logical flow

### 2. **New Sequential Mapping Process**

#### **Step 1: Chunk the Ground-Truth Document**

```python
chunk_size = 2000  # Characters per chunk
ground_truth_chunks = []
for i in range(0, len(ground_truth_text), chunk_size):
    chunk = ground_truth_text[i:i + chunk_size]
    if chunk.strip():
        ground_truth_chunks.append(chunk.strip())
```

#### **Step 2: AI-Powered Chunk Mapping**

For each chunk, use an LLM to determine which outline section(s) it belongs to:

- Considers content relevance
- Takes sequential position into account
- Can map to multiple sections if content spans topics
- Includes confidence scoring

#### **Step 3: Intelligent Fallback**

If AI mapping fails, uses positional mapping:

```python
chunk_position = chunk_idx / len(ground_truth_chunks)
section_index = min(int(chunk_position * len(section_descriptions)), len(section_descriptions) - 1)
```

### 3. **Enhanced Mapping Prompt**

The new mapping prompt includes:

- Clear task description
- Sequential context awareness
- Confidence assessment
- Structured response format

### 4. **Improved Data Structure**

Each mapped chunk now includes metadata:

```python
{
    "content": chunk,
    "chunk_index": chunk_idx,
    "confidence": confidence,
    "reasoning": reasoning
}
```

### 5. **Better Analytics**

The analysis summary now includes:

- Chunk processing statistics
- Mapping success rates
- Explanation of sequential mapping methodology

## Benefits

### **1. Preserves Document Structure**

- Maintains the logical flow of the ground-truth document
- Ensures early content maps to early sections, late content to late sections
- Better represents how documents are actually organized

### **2. More Accurate Mapping**

- AI considers both content and position when mapping
- Can handle content that spans multiple sections
- Reduces mismatched comparisons from keyword-based retrieval

### **3. Comprehensive Coverage**

- Every part of the ground-truth document is processed
- No content is missed due to poor keyword matching
- Ensures all sections get relevant comparison material

### **4. Intelligent Handling of Edge Cases**

- Confidence scoring helps identify uncertain mappings
- Positional fallback ensures all chunks are assigned
- Graceful handling of documents that don't match outline structure

## Example Workflow

1. **Ground-truth document:** "Clinical Trial Protocol.pdf" (20,000 characters)
2. **Split into chunks:** 10 chunks of ~2,000 characters each
3. **Outline sections:**

   - "Background and Rationale"
   - "Study Objectives"
   - "Methodology"
   - "Data Analysis Plan"

4. **Mapping process:**

   - Chunk 1-2: Mapped to "Background and Rationale"
   - Chunk 3: Mapped to "Study Objectives"
   - Chunk 4-7: Mapped to "Methodology"
   - Chunk 8-10: Mapped to "Data Analysis Plan"

5. **Optimization:** Each section's generated content is compared against its specifically mapped ground-truth chunks

## Technical Implementation Details

### **Prompt Engineering**

- Context-aware prompts that consider document position
- Structured response parsing with error handling
- Confidence assessment for mapping quality

### **Error Handling**

- Robust parsing of LLM responses
- Fallback mechanisms for failed mappings
- Comprehensive logging and debugging information

### **Performance Considerations**

- Efficient chunking to avoid token limits
- Batch processing with cancellation support
- Progress tracking and status updates

This approach provides a much more logical and comprehensive basis for outline optimization by ensuring that comparisons are made between structurally equivalent parts of documents rather than just keyword-matched snippets.
