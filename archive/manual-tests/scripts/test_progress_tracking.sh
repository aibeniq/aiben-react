#!/bin/bash

echo "🔍 Testing Progress Tracking End-to-End"
echo "======================================="

echo ""
echo "1. Testing basic connectivity to backend..."
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8000/health || echo "❌ Backend not accessible"

echo ""
echo "2. Testing authentication..."
# First get a token
echo "Getting authentication token..."
response=$(curl -s -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "accept: application/json" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin%40example.com&password=cYJtxvYubNF40sx7sSlu1LFD9zhPaS7Ld75O")

token=$(echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$token" ]; then
    echo "❌ Could not get authentication token"
    echo "Response: $response"
    exit 1
fi

echo "✅ Got authentication token"

echo ""
echo "3. Testing progress endpoint with dummy task ID..."
progress_response=$(curl -s -X GET "http://localhost:8000/api/v1/knowledge-bases/progress/dummy-task-id" \
  -H "accept: application/json" \
  -H "Authorization: Bearer $token")

echo "Progress endpoint response: $progress_response"

echo ""
echo "4. Testing Redis connection and progress tracker..."
echo "Checking if Redis is available..."
docker exec aiben-react-redis-1 redis-cli ping || echo "❌ Redis not accessible"

echo ""
echo "5. Testing a real knowledge base creation to see task_id..."
echo "Creating a minimal knowledge base to trace the response..."

# Create a simple text file for testing
echo "This is a test document for progress tracking verification." > /tmp/test_doc.txt

# Attempt to create a knowledge base and capture the response
kb_response=$(curl -s -X POST "http://localhost:8000/api/v1/knowledge-bases/?title=Progress%20Test%20KB&description=Testing%20progress%20tracking&embedding_model_id=26213c49-bbb7-42f5-85c7-dbc6eb3dcf06" \
  -H "accept: application/json" \
  -H "Authorization: Bearer $token" \
  -F "files=@/tmp/test_doc.txt")

echo ""
echo "Knowledge base creation response:"
echo "$kb_response" | jq . 2>/dev/null || echo "$kb_response"

# Clean up
rm -f /tmp/test_doc.txt

echo ""
echo "🔍 End-to-end test completed!"