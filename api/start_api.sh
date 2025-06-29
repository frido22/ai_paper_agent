#!/bin/bash

# Argument Graph Extraction API Startup Script

echo "🚀 Starting Argument Graph Extraction API..."
echo "=============================================="

# Check if virtual environment exists
if [ -d "../venv" ]; then
    echo "📦 Activating virtual environment..."
    source ../venv/bin/activate
else
    echo "⚠️  No virtual environment found. Using system Python."
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable is not set."
    echo "Please set your OpenAI API key:"
    echo "export OPENAI_API_KEY='your-api-key-here'"
    exit 1
fi

# Check if requirements are installed
echo "🔍 Checking dependencies..."
if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the API
echo "🌐 Starting API server on http://localhost:8000"
echo "📚 API documentation will be available at http://localhost:8000/docs"
echo "🔍 Health check available at http://localhost:8000/health/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py 