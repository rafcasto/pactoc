#!/bin/bash

echo "🧪 TESTING INVITATION ENDPOINTS"
echo "================================"

# Base URL for testing
BASE_URL="http://localhost:8000"

# You'll need to get a real auth token
# For now, we'll test without auth to see the error behavior
TOKEN=""

echo "1. Testing database health..."
curl -s $BASE_URL/api/health/db | jq '.' 2>/dev/null || echo "No jq installed, raw response:"
curl -s $BASE_URL/api/health/db

echo -e "\n2. Testing GET /api/invitations without auth (should fail)..."
curl -s $BASE_URL/api/invitations | jq '.' 2>/dev/null || echo "Raw response:"
curl -s $BASE_URL/api/invitations

echo -e "\n3. Testing GET /api/invitations with invalid auth..."
curl -s -H "Authorization: Bearer invalid-token" \
     $BASE_URL/api/invitations | jq '.' 2>/dev/null || echo "Raw response:"
curl -s -H "Authorization: Bearer invalid-token" $BASE_URL/api/invitations

if [ ! -z "$TOKEN" ]; then
    echo -e "\n4. Testing GET /api/invitations with valid auth..."
    curl -s -H "Authorization: Bearer $TOKEN" \
         $BASE_URL/api/invitations | jq '.' 2>/dev/null || echo "Raw response:"
    curl -s -H "Authorization: Bearer $TOKEN" $BASE_URL/api/invitations

    echo -e "\n5. Testing POST /api/invitations with valid auth..."
    curl -s -X POST \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $TOKEN" \
         -d '{"email":"test-endpoint@example.com","first_name":"Test","last_name":"User"}' \
         $BASE_URL/api/invitations | jq '.' 2>/dev/null || echo "Raw response:"
    curl -s -X POST \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $TOKEN" \
         -d '{"email":"test-endpoint@example.com","first_name":"Test","last_name":"User"}' \
         $BASE_URL/api/invitations
else
    echo -e "\n4-5. Skipping authenticated tests (no TOKEN provided)"
    echo "To test with authentication, get a token from the frontend and run:"
    echo "TOKEN='your-token-here' ./test_endpoints.sh"
fi

echo -e "\n📊 Test Summary:"
echo "- Database health endpoint should work ✓"
echo "- Unauthenticated requests should fail with 401/403 ✓"
echo "- Invalid auth should fail with 401/403 ✓"
echo "- Valid auth should work (if TOKEN provided) ?"
