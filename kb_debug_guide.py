#!/usr/bin/env python3
"""
Test and debugging guide for knowledge base integration in topic generation.
"""

print(
    """
🔧 KNOWLEDGE BASE INTEGRATION - DEBUGGING GUIDE
===============================================

ISSUE: "Full Document Scan with vector database doesn't use reference"

FIXES IMPLEMENTED:
✅ Fixed content_retrieval.py full_scan mode with proper error handling
✅ Added comprehensive logging throughout the pipeline  
✅ Fixed missing return statements in edge cases
✅ Enhanced frontend parameter passing

DEBUGGING STEPS:
1. Check Backend Logs
   - Look for "=== KNOWLEDGE BASE INTEGRATION START ==="
   - Verify KB ID and search mode are received
   - Check if content is successfully retrieved

2. Verify Knowledge Base Setup
   - Ensure KB exists and user has access
   - Check if sources exist in the KB
   - Verify source data can be extracted

3. Frontend Debug
   - Open browser developer tools
   - Look for "🔍 Topic Generation Debug:" in console
   - Verify correct parameters are being sent

4. Test Different Modes
   - Try both "vector" and "full_scan" modes
   - Compare results to see which mode works

EXPECTED LOG OUTPUT (Backend):
=== KNOWLEDGE BASE INTEGRATION START ===
Knowledge Base ID: abc-123
Search Mode: full_scan  
Query (description): Compare sustainability...
Full scan mode: Looking for sources in KB abc-123
Found 3 sources in knowledge base
Processing source: document1.pdf (ID: 456)
Found source data for document1.pdf, size: 12345 bytes
✅ Successfully retrieved KB content: 5000 characters
✅ Knowledge base content added to prompt variables
=== KNOWLEDGE BASE INTEGRATION END ===

TROUBLESHOOTING:
- If "No sources found": Check KB ownership/access rights
- If "No content extracted": Check source data integrity  
- If content retrieved but topics don't reflect it: Check LLM prompt integration
- If API call fails: Check parameter format and endpoint availability

NEXT STEPS:
1. Start backend server with: docker-compose up backend
2. Test in frontend with KB selection
3. Monitor backend logs for the debug output above
4. If issues persist, check database directly for KB/source data
"""
)
