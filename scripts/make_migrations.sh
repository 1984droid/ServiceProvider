#!/bin/bash
# Create and apply migrations after model changes

set -e

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate || source .venv/Scripts/activate
else
    echo "❌ Virtual environment not found. Run ./setup_dev.sh first"
    exit 1
fi

echo "🔍 Checking for model changes..."
python manage.py makemigrations

echo ""
read -p "Apply migrations now? (y/n): " apply

if [ "$apply" = "y" ] || [ "$apply" = "Y" ]; then
    echo ""
    echo "🔄 Applying migrations..."
    python manage.py migrate
    echo "✅ Migrations applied!"
else
    echo "Skipped. Run 'python manage.py migrate' when ready."
fi

echo ""
echo "💡 TIP: Review migration files before committing:"
echo "   git diff apps/*/migrations/"
echo ""
