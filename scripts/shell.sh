#!/bin/bash
# Open Django shell with virtual environment

if [ -d ".venv" ]; then
    source .venv/bin/activate || source .venv/Scripts/activate
else
    echo "❌ Virtual environment not found. Run ./setup_dev.sh first"
    exit 1
fi

echo "🐍 Opening Django shell..."
echo ""
python manage.py shell
