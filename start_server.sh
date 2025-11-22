#!/bin/bash
# Quick start script for the investment analysis server

echo "🚀 Starting Investment Deal Analysis Server..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found"
    echo "   Create a .env file with: OPENAI_API_KEY=your_key_here"
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d "env" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the server
echo "🌐 Starting Flask server on http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""
python app.py

