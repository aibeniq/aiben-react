#!/bin/bash
# Simple test script for rate limiting

echo "🧪 Testing Rate Limiting Implementation"
echo "========================================"
echo ""

API_URL="http://localhost:8000/api/v1/login/access-token"
TEST_EMAIL="test@example.com"
WRONG_PASSWORD="wrongpassword"

echo "Test 1: Making 6 rapid login attempts with wrong password"
echo "Expected: First 5 should fail with 400, 6th should fail with 429"
echo ""

for i in {1..6}; do
  echo -n "Attempt $i: "
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$TEST_EMAIL&password=$WRONG_PASSWORD")
  
  if [ $i -le 5 ]; then
    if [ "$HTTP_CODE" = "400" ]; then
      echo "✅ $HTTP_CODE (Expected - Invalid credentials)"
    else
      echo "❌ $HTTP_CODE (Expected 400)"
    fi
  else
    if [ "$HTTP_CODE" = "429" ]; then
      echo "✅ $HTTP_CODE (Expected - Rate limited)"
    else
      echo "❌ $HTTP_CODE (Expected 429)"
    fi
  fi
  sleep 1
done

echo ""
echo "Test 2: Checking if user account is locked"
echo ""

docker-compose exec -T backend python manage_lockouts.py --check "$TEST_EMAIL" 2>/dev/null || echo "Account check utility not available yet"

echo ""
echo "✅ Rate limiting test complete!"
echo ""
echo "To unlock the test account, run:"
echo "docker-compose exec backend python manage_lockouts.py --unlock $TEST_EMAIL"
