#!/bin/bash

echo "Testing Work Log API endpoints..."
echo ""

# Test 1: GET /api/worklogs (should work now)
echo "1. Testing GET /api/worklogs..."
curl -s -X GET "http://localhost:8000/api/worklogs" \
  -H "Content-Type: application/json" | jq -r '.error // "✅ Success"'
echo ""

# Test 2: POST /api/worklogs (create work log)
echo "2. Testing POST /api/worklogs (create)..."
curl -s -X POST "http://localhost:8000/api/worklogs" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Today I fixed CORS issues and improved API endpoints for the work log feature.",
    "user_id": "test_user"
  }' | jq -r '.error // "✅ Success - Created work log"'
echo ""

# Test 3: POST /api/skills (get skills breakdown)
echo "3. Testing POST /api/skills..."
curl -s -X POST "http://localhost:8000/api/skills" \
  -H "Content-Type: application/json" \
  -d '{}' | jq -r '.error // "✅ Success - Retrieved skills"'
echo ""

echo "API tests complete!"
