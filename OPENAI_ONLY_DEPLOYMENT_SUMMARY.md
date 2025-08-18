# OpenAI-Only Deployment Configuration - Implementation Summary

## Overview

This implementation adds configuration-driven toggles to create an OpenAI-only deployment where users cannot change LLM or embedding models. The solution uses environment variables to control model selection visibility and enforce specific default models.

## Backend Changes

### 1. Configuration Settings (`backend/app/core/config.py`)

Added three new configuration options:

```python
ENABLE_MODEL_SELECTION: bool = True  # Controls if users can change models
FORCE_DEFAULT_LLM: str = "gpt-4o-mini"  # Default LLM when selection disabled
FORCE_DEFAULT_EMBEDDING: str = "text-embedding-3-small"  # Default embedding when selection disabled
```

### 2. Model Selection Logic (`backend/app/api/routes/modelselection.py`)

Updated `get_default_embedding_model` function:

- When `ENABLE_MODEL_SELECTION=False`, forces `FORCE_DEFAULT_EMBEDDING`
- Maintains backward compatibility with existing logic

### 3. LLM Selection Logic (`backend/app/api/routes/llms.py`)

Updated `get_default_llm_model` function:

- When `ENABLE_MODEL_SELECTION=False`, forces `FORCE_DEFAULT_LLM`
- Maintains backward compatibility with existing logic

### 4. System Configuration API (`backend/app/api/routes/utils.py`)

Added new endpoint `/api/v1/utils/system-config`:

- Returns configuration flags to frontend
- Enables conditional UI rendering

### 5. User Creation Logic (`backend/app/crud.py`)

Updated `create_user` function:

- Respects forced defaults when `ENABLE_MODEL_SELECTION=False`
- Ensures new users get gpt-4o-mini and text-embedding-3-small
- Falls back to normal logic when model selection is enabled

## Frontend Changes

### 1. Navigation Filtering (`frontend/src/components/Common/SidebarItems.tsx`)

- Added system configuration query using TanStack Query
- Implemented conditional filtering to hide "Model Selection" menu item
- Added error handling with retry logic and stale time caching
- Fail-safe behavior: shows model selection if config unavailable

## Environment Configuration

To enable OpenAI-only deployment, set these environment variables:

```bash
ENABLE_MODEL_SELECTION=false
FORCE_DEFAULT_LLM=gpt-4o-mini
FORCE_DEFAULT_EMBEDDING=text-embedding-3-small
```

## Features

### ✅ Completed Features

1. **Configuration-driven model selection control**

   - Environment variable toggles
   - Backward compatibility maintained

2. **Forced model defaults**

   - API endpoints respect forced defaults
   - New users automatically get correct models
   - Fallback mechanisms for missing models

3. **UI hiding**

   - Model Selection tab hidden when disabled
   - Graceful degradation on API errors

4. **Minimal code changes**
   - All changes are additive
   - Easy to enable/disable via environment variables
   - No breaking changes to existing functionality

### 🔄 Future Considerations

1. **SDK Regeneration** (Optional)

   - Current implementation uses direct fetch calls
   - Can be improved with proper TypeScript types

2. **Additional UI Safeguards** (Optional)
   - Could add guards to model selection pages
   - Redirect users if they navigate directly to disabled routes

## Testing

To test the implementation:

1. **Enable OpenAI-only mode:**

   ```bash
   ENABLE_MODEL_SELECTION=false
   FORCE_DEFAULT_LLM=gpt-4o-mini
   FORCE_DEFAULT_EMBEDDING=text-embedding-3-small
   ```

2. **Verify behaviors:**

   - Model Selection tab disappears from navigation
   - New users get gpt-4o-mini and text-embedding-3-small
   - API endpoints return forced defaults
   - System config endpoint returns correct flags

3. **Test backward compatibility:**
   ```bash
   ENABLE_MODEL_SELECTION=true
   ```
   - All functionality should work as before
   - Model Selection tab appears in navigation
   - Users can change models normally

## Rollback Instructions

To revert to normal operation:

1. Set `ENABLE_MODEL_SELECTION=true` (or remove the variable)
2. Restart the application
3. All changes will be inactive but preserved for future use

## Notes

- All changes are designed to be non-breaking
- Configuration is centralized in `config.py`
- Frontend gracefully handles missing configuration
- User creation logic maintains compatibility with existing users
- Implementation preserves all existing functionality when disabled
