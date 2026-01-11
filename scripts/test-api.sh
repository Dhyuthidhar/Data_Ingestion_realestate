#!/bin/bash

echo ""
echo "🧪 Testing API Endpoints"
echo "========================================"

API_URL="http://localhost:5001"

# Test 1: Health check
echo ""
echo "Test 1: Health Check"
curl -s "$API_URL/health" | python3 -m json.tool
echo ""

# Test 2: System status
echo "Test 2: System Status"
curl -s "$API_URL/api/status" | python3 -m json.tool
echo ""

# Test 3: Statistics
echo "Test 3: Statistics"
curl -s "$API_URL/api/stats" | python3 -m json.tool
echo ""

echo "========================================"
echo "✅ API tests complete"
echo ""
