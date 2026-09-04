# Archive Tab Internal Server Error Fix

## Issue Summary

When viewing previously generated reports through the Archive tab, users encountered an Internal Server Error with the following validation error:

```
fastapi.exceptions.ResponseValidationError: 1 validation errors:
{'type': 'string_type', 'loc': ('response', 'sections'), 'msg': 'Input should be a valid string', 'input': [{'title': '# INFORMATION ABOUT THE STUDY', 'content': '# INFORMATION ABOUT THE STUDY', 'source_citations': [], 'consult_documents': False}, ...]}
```

## Root Cause Analysis

The error occurred because:

1. **Model Definition**: In `ReportGenieDetailResponse`, the `sections` field is defined as `str`
2. **Data Storage**: In the database, sections are stored as JSON strings
3. **Runtime Issue**: The backend code was sometimes retrieving sections data as a list/array instead of a string, causing a validation error when FastAPI tried to serialize the response

The specific problematic code was in two endpoints:

- `get_report_history()` - Line ~1012
- `get_report_detail()` - Line ~1129

Both were using:

```python
"sections": input_data.get("sections", "")
```

But `input_data.get("sections")` could return either a string or a list, depending on how the data was originally stored.

## ✅ Fix Applied

### 1. Updated `get_report_detail()` endpoint

**File**: `backend/app/api/routes/reportgenie.py` (around line 1129)

**Before**:

```python
"sections": input_data.get("sections", ""),
```

**After**:

```python
"sections": input_data.get("sections", "") if isinstance(input_data.get("sections", ""), str) else json.dumps(input_data.get("sections", [])),
```

### 2. Updated `get_report_history()` endpoint

**File**: `backend/app/api/routes/reportgenie.py` (around line 1012)

**Before**:

```python
"sections": input_data.get("sections", ""),
```

**After**:

```python
"sections": input_data.get("sections", "") if isinstance(input_data.get("sections", ""), str) else json.dumps(input_data.get("sections", [])),
```

### 3. Added Debugging

Added debug logging to help identify the data types being processed:

- In `get_report_detail()`: Logs the type and value of sections data
- In `get_report_history()`: Logs the type of sections data

### 4. Fixed Fallback Case

Updated the JSON decode error fallback in `get_report_detail()` to include all required fields:

- Added missing `kb_name`, `kb_id`, and `sections` fields to match the response model

## 🔧 How the Fix Works

The fix uses a type check to ensure the `sections` field is always a string:

1. **If sections is already a string**: Use it as-is
2. **If sections is a list/array**: Convert it to a JSON string using `json.dumps()`
3. **If sections is missing**: Use empty string as default

This ensures compatibility with both old and new data formats while maintaining the expected string type for the API response model.

## 🧪 Testing

To verify the fix:

1. **Navigate to Archive tab**: Should load without internal server error
2. **View report details**: Click on any previously generated report
3. **Check console logs**: Backend should show debug information about sections data types
4. **Verify functionality**: Both history list and detail views should work correctly

## 📋 Related Files Modified

- `backend/app/api/routes/reportgenie.py`
  - `get_report_history()` function
  - `get_report_detail()` function

## 🔍 Future Prevention

This issue highlights the importance of:

1. **Consistent data types**: Ensure stored data matches the expected API response types
2. **Type validation**: Add runtime type checks when dealing with dynamic/stored data
3. **Migration handling**: Consider data format changes when updating storage structures

The fix maintains backward compatibility while ensuring forward compatibility with the defined API response models.
