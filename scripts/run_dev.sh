#!/bin/bash
# Quick dev server launcher

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate || source .venv/Scripts/activate
else
    echo "❌ Virtual environment not found. Run ./setup_dev.sh first"
    exit 1
fi

echo "🚀 Starting development server..."
echo "Press Ctrl+C to stop"
echo ""

python manage.py runserver
