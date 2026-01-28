#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🚗 Smart Parking Allocation & Zone Management System     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if dependencies are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask not found. Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Run tests
echo "🧪 Running test suite..."
python3 test_parking_system.py
echo ""

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
    echo ""
    echo "🚀 Starting Smart Parking System..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🌐 Web Interface: http://localhost:5000"
    echo "📡 API Endpoint:  http://localhost:5000/api"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Start the Flask server
    python3 app.py
else
    echo "❌ Tests failed. Please check the errors above."
    exit 1
fi