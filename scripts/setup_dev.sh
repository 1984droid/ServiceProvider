#!/bin/bash
# Development environment setup script for ServiceProvider application
# Run this after copying NEW_BUILD_STARTER to new location

set -e  # Exit on error

echo "=================================="
echo "ServiceProvider Dev Setup"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Are you in the project root?"
    exit 1
fi

echo "✓ Found project root"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "⚠️  .venv already exists, skipping..."
else
    python -m venv .venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate || source .venv/Scripts/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check for .env file
echo "⚙️  Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found, generating with secure random values..."
    python scripts/generate_env.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed to generate .env file"
        exit 1
    fi
    echo ""
    echo "⚠️  IMPORTANT: Review .env and adjust database settings if needed!"
    echo ""
else
    echo "✓ .env file exists"
    echo ""
fi

# Check PostgreSQL connection
echo "🔍 Checking PostgreSQL connection..."
source .env
if command -v psql &> /dev/null; then
    if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -c '\q' 2>/dev/null; then
        echo "✓ PostgreSQL connection successful"
    else
        echo "⚠️  Cannot connect to PostgreSQL. Check your credentials in .env"
        echo "   Host: $DB_HOST"
        echo "   User: $DB_USER"
        echo "   Database: $DB_NAME"
    fi
else
    echo "⚠️  psql not found, skipping connection check"
fi
echo ""

# Create database if it doesn't exist
echo "🗄️  Setting up database..."
if command -v psql &> /dev/null; then
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME"
    echo "✓ Database ready: $DB_NAME"
else
    echo "⚠️  Please create database manually: $DB_NAME"
fi
echo ""

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate
echo "✓ Migrations complete"
echo ""

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs
echo "✓ Logs directory created"
echo ""

# Create superuser prompt
echo "=================================="
echo "Setup Complete! 🎉"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Create a superuser:"
echo "   python manage.py createsuperuser"
echo ""
echo "2. Run the development server:"
echo "   python manage.py runserver"
echo ""
echo "3. Visit: http://localhost:8000/admin"
echo ""
echo "Your virtual environment is activated."
echo "To deactivate: deactivate"
echo ""
