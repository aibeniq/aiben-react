#!/bin/bash
set -e

echo "🚀 Starting Comprehensive Functionality Tests"
echo "=============================================="

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2
    if curl -s -f "http://localhost:${port}" > /dev/null 2>&1; then
        echo "✅ ${service_name} is running on port ${port}"
        return 0
    else
        echo "❌ ${service_name} is not running on port ${port}"
        return 1
    fi
}

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Start services if not running
echo "📦 Checking and starting services..."
if ! check_service "Backend" "8000"; then
    echo "Starting backend services..."
    docker compose up -d --wait backend
    sleep 10
    
    # Check again
    if ! check_service "Backend" "8000"; then
        echo "❌ Failed to start backend service"
        exit 1
    fi
fi

if ! check_service "Frontend" "5173"; then
    echo "Starting frontend development server..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    sleep 15
    
    # Check if frontend started
    if ! check_service "Frontend" "5173"; then
        echo "❌ Failed to start frontend service"
        kill $FRONTEND_PID 2>/dev/null || true
        exit 1
    fi
fi

echo ""
echo "🔧 Running Backend Comprehensive Tests..."
echo "=========================================="

# Run backend tests
docker compose exec -T backend bash -c "python -m pytest app/tests/test_comprehensive_functionality.py -v --tb=short -x" || {
    echo "❌ Backend tests failed"
    BACKEND_FAILED=true
}

echo ""
echo "🌐 Running Frontend Comprehensive Tests..."
echo "==========================================="

# Run frontend tests
cd frontend

# Install playwright if not installed
if ! npx playwright --version > /dev/null 2>&1; then
    echo "Installing Playwright..."
    npx playwright install chromium
fi

# Run the comprehensive functionality tests
npx playwright test comprehensive-functionality.spec.ts --reporter=line --timeout=30000 || {
    echo "❌ Frontend tests failed"
    FRONTEND_FAILED=true
}

cd ..

echo ""
echo "📊 Test Summary"
echo "==============="

if [ "$BACKEND_FAILED" = true ]; then
    echo "❌ Backend comprehensive tests: FAILED"
else
    echo "✅ Backend comprehensive tests: PASSED"
fi

if [ "$FRONTEND_FAILED" = true ]; then
    echo "❌ Frontend comprehensive tests: FAILED"
else
    echo "✅ Frontend comprehensive tests: PASSED"
fi

echo ""
if [ "$BACKEND_FAILED" = true ] || [ "$FRONTEND_FAILED" = true ]; then
    echo "❌ Some tests failed. Check the output above for details."
    echo ""
    echo "To debug:"
    echo "  Backend: docker compose exec backend bash -c 'python -m pytest app/tests/test_comprehensive_functionality.py -v -s'"
    echo "  Frontend: cd frontend && npx playwright test comprehensive-functionality.spec.ts --ui"
    exit 1
else
    echo "🎉 All comprehensive functionality tests passed!"
    echo ""
    echo "Your application successfully handles:"
    echo "  ✅ Ask functionality (vector & full scan)"
    echo "  ✅ Review functionality (upload & knowledge base)"
    echo "  ✅ Generate functionality (sections & outlines)" 
    echo "  ✅ Compare functionality (document comparison)"
    echo "  ✅ Match functionality (form field extraction)"
    echo "  ✅ UI navigation and modal workflows"
    echo "  ✅ Copy button functionality"
fi

# Cleanup frontend process if we started it
if [ ! -z "$FRONTEND_PID" ]; then
    kill $FRONTEND_PID 2>/dev/null || true
fi

echo ""
echo "✨ Comprehensive testing completed!"
