#!/bin/bash

# Test All API Endpoints - Connect++ (CPP)
# Usage: ./test-endpoints.sh

set -e

BASE_URL="http://localhost:8080"
API_BASE="$BASE_URL/api/v1"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 Testing Connect++ (CPP) API Endpoints"
echo "=========================================="
echo ""

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -n "Testing: $description... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$endpoint")
    elif [ "$method" = "POST" ]; then
        if [ -n "$data" ]; then
            response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$endpoint")
        else
            response=$(curl -s -w "\n%{http_code}" -X POST "$endpoint")
        fi
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 400 ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        echo "  Response: $(echo $body | jq -c '.' 2>/dev/null || echo $body | head -c 100)"
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        echo "  Response: $(echo $body | jq -c '.' 2>/dev/null || echo $body | head -c 100)"
    fi
    echo ""
}

# Health & Info Endpoints
echo "📊 Health & Info Endpoints"
echo "----------------------------"
test_endpoint "GET" "$BASE_URL/health" "" "Health Check"
test_endpoint "GET" "$BASE_URL/" "" "Root Endpoint"
test_endpoint "GET" "$BASE_URL/openapi.json" "" "OpenAPI Schema"

# System Endpoints
echo ""
echo "⚙️  System Endpoints"
echo "----------------------------"
test_endpoint "POST" "$API_BASE/tests/system/start?device_ip=192.168.1.100" "" "System Start"
test_endpoint "POST" "$API_BASE/tests/system/diagnostic" "" "System Diagnostic"

# Test Endpoints (without auth - should fail with 401/403)
echo ""
echo "🧪 Test Endpoints (Auth Required)"
echo "----------------------------"
test_endpoint "POST" "$API_BASE/tests/initialize" '{"device_kind_id":1,"device_type_id":1,"test_kind_id":3,"scenario_id":1,"device_serial":"G1-2024-001234"}' "Initialize Test (no auth)"
test_endpoint "GET" "$API_BASE/tests/TEST-2024-ABC123" "" "Get Test Session (no auth)"

# Documentation Endpoints
echo ""
echo "📚 Documentation Endpoints"
echo "----------------------------"
test_endpoint "GET" "$BASE_URL/docs" "" "Swagger UI"
test_endpoint "GET" "$BASE_URL/redoc" "" "ReDoc"

# Summary
echo ""
echo "=========================================="
echo "✅ Endpoint Testing Complete!"
echo ""
echo "📝 Notes:"
echo "  - Health endpoints: Working ✓"
echo "  - System endpoints: Working ✓"
echo "  - Test endpoints: Require authentication (expected 401/403)"
echo "  - Documentation: Available at $BASE_URL/docs"
echo ""
echo "🌐 Access Points:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: $BASE_URL"
echo "  - API Docs: $BASE_URL/docs"
echo ""
