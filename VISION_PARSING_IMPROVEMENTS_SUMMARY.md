# Vision Table Parsing Improvements Summary

## Problem Addressed

**Original Issue**: "Your solution is imperfect: Some rows match. Others are mismatched or misaligned in the JSON. JSON often uses a 'category header' as if it were a data row, shifting the actual numbers. I need you to improve visual parsing of data -- perhaps an improved prompt, or sending fewer images at a time in the batch?"

**Root Cause**: Vision parsing was treating category headers (like "Marital status", "Employment", "Education") as regular data rows, causing misalignment of actual data values.

## Changes Implemented

### 1. Enhanced Vision Prompt (`backend/app/services/vision_service.py`)

#### New Category-Aware Structure

- **Before**: Single flat `rows` array that mixed headers and data
- **After**: Structured format with `category_sections` and `standalone_rows`

```json
{
  "table_id": "table_1",
  "headers": ["Characteristic", "N", "Percentage"],
  "category_sections": [
    {
      "category": "Education",
      "rows": [
        ["High School/Some College", "25", "33%"],
        ["College Graduate", "35", "47%"]
      ]
    }
  ],
  "standalone_rows": [...],
  "metadata": {"has_categories": true}
}
```

#### Improved Instructions

- **CRITICAL**: Distinguish between category headers and data rows
- Step-by-step process for identifying table structure
- Explicit handling of hierarchical demographic tables
- Better examples showing proper category organization

### 2. Reduced Batch Size for Higher Accuracy

- **Before**: `BATCH_SIZE = 5` images per batch
- **After**: `BATCH_SIZE = 2` images per batch
- **Benefit**: More focused processing, better accuracy on complex tables

### 3. Enhanced Data Processing (`backend/app/services/document_utils.py`)

#### Category-Aware Processing

- Handles new `category_sections` structure
- Adds `_category` metadata to categorized rows
- Maintains backward compatibility with legacy `rows` format
- Processes standalone rows separately

#### Fallback Compatibility

- Supports both new structured and legacy formats
- Graceful degradation if new format not available
- Preserves existing functionality

### 4. Normalization Layer (`backend/app/services/vision_service.py`)

#### Format Standardization

- Creates flattened `rows` field for backward compatibility
- Calculates accurate row counts from different structures
- Ensures consistent data format downstream

## Expected Improvements

### 1. Accuracy

- **Category Headers**: No longer treated as data rows
- **Data Alignment**: Proper matching of values to columns
- **Hierarchical Structure**: Better handling of demographic/category tables

### 2. Processing Quality

- **Smaller Batches**: More focused analysis per batch
- **Better Instructions**: Clearer guidance for complex tables
- **Structured Output**: Organized data with category information

### 3. Specific Issue Resolution

- ✅ **Gender, Employment, Previous treatment**: Should continue matching correctly
- ✅ **Marital status, Children, Cohabitating, Education**: Should no longer be misaligned
- ✅ **Category Headers**: Will be properly identified and separated from data

## Technical Details

### Files Modified

1. `backend/app/services/vision_service.py`

   - Line 335: Reduced batch size to 2
   - Lines 372-443: Complete prompt rewrite with category awareness
   - Lines 540-580: Added normalization layer

2. `backend/app/services/document_utils.py`
   - Lines 1275-1320: Enhanced table processing for category sections

### Backward Compatibility

- All existing code continues to work
- Legacy `rows` format still supported
- New features add value without breaking changes

## Testing Recommendations

1. **Upload APA Demographics Table**: Test the specific problematic table mentioned
2. **Verify Category Separation**: Ensure headers like "Marital status" aren't treated as data
3. **Check Data Alignment**: Confirm percentages match correct demographic categories
4. **Compare Before/After**: Validate improvements in JSON structure accuracy

## Expected User Experience

**Before**:

```json
"rows": [
  ["Marital status", "", ""],  // ❌ Header treated as data
  ["Single", "45", "60%"],     // ❌ Values shifted
  ["Education", "", ""],        // ❌ Another header as data
  ["College", "30", "40%"]     // ❌ More misalignment
]
```

**After**:

```json
"category_sections": [
  {
    "category": "Marital status",  // ✅ Proper category identification
    "rows": [
      ["Single", "45", "60%"],     // ✅ Correct alignment
      ["Married", "30", "40%"]     // ✅ Proper data rows
    ]
  },
  {
    "category": "Education",       // ✅ Another category
    "rows": [
      ["College", "50", "67%"],    // ✅ Aligned correctly
      ["Graduate", "25", "33%"]    // ✅ Proper structure
    ]
  }
]
```

The improvements should significantly reduce the category header misalignment issues while providing more structured, accurate table data extraction.
