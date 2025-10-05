#!/bin/bash
# Test script to verify dashboard components and API endpoints

echo "🧪 Testing Dashboard Implementation"
echo "=================================="

# Start services in background
echo "🚀 Starting services..."
cd /Users/rafaelcastillo/pactoc
./start_dev.sh &
SERVICES_PID=$!

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

echo "🔍 Testing backend endpoints..."

# Test API endpoints
echo "Testing public catalogs endpoint..."
curl -s http://localhost:8000/api/public/catalogs | head -c 100
echo ""

echo "Testing dashboard endpoint (requires auth)..."
curl -s http://localhost:8000/api/meal-plan-workflow/dashboard | head -c 200
echo ""

echo "📱 Dashboard should be available at: http://localhost:3000/dashboard"
echo "🔧 Backend API available at: http://localhost:8000"

# Keep services running
echo "⚡ Services are running. Press Ctrl+C to stop."
wait $SERVICES_PID
