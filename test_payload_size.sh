#!/bin/bash

TOKEN=$(curl -s -X POST -d "username=admin@example.com&password=yourmomgoestocollege" -H "Content-Type: application/x-www-form-urlencoded" http://localhost:8000/api/v1/login/access-token | python3 -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))")

echo "Testing Veradoc endpoint payload sizes:"
echo "========================================="

# Test with include_qa_pairs=false (summary)
SIZE_SUMMARY=$(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/veradoc/history/f439be53-0a84-4afa-b93b-2cb8571468cd?include_qa_pairs=false" | wc -c)
echo "Summary (include_qa_pairs=false): $SIZE_SUMMARY bytes"

# Test with include_qa_pairs=true (full)
SIZE_FULL=$(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/veradoc/history/f439be53-0a84-4afa-b93b-2cb8571468cd?include_qa_pairs=true" | wc -c)
echo "Full (include_qa_pairs=true): $SIZE_FULL bytes"

# Calculate reduction
REDUCTION=$((SIZE_FULL - SIZE_SUMMARY))
echo "Reduction: $REDUCTION bytes ($((REDUCTION / 1024 / 1024)) MB saved)"
