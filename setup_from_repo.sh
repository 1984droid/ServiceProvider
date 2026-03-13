#!/bin/bash
# Complete dev environment setup script from fresh git clone
# This sets up ServiceProvider application from scratch

set -e  # Exit on error

echo "======================================="
echo "ServiceProvider - Dev Setup from Repo"
echo "======================================="
echo ""
echo "This script will:"
echo "  1. Check prerequisites"
echo "  2. Set up Python virtual environment"
echo "  3. Install dependencies (Python + Node)"
echo "  4. Configure environment (.env)"
echo "  5. Set up PostgreSQL database"
echo "  6. Run migrations"
echo "  7. Seed initial data"
echo "  8. Set up frontend"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 1
fi
echo ""

# ============================================================================
# 1. CHECK PREREQUISITES
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Checking Prerequisites"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Are you in the project root?"
    exit 1
fi
echo "✓ Found project root"

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.11+"
    exit 1
fi
PYTHON_CMD=$(command -v python3 || command -v python)
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION found"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
NODE_VERSION=$(node --version)
echo "✓ Node.js $NODE_VERSION found"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm"
    exit 1
fi
NPM_VERSION=$(npm --version)
echo "✓ npm $NPM_VERSION found"

# Check PostgreSQL client
if ! command -v psql &> /dev/null; then
    echo "⚠️  psql client not found - PostgreSQL setup will be manual"
    HAVE_PSQL=false
else
    PSQL_VERSION=$(psql --version | cut -d' ' -f3 | cut -d'.' -f1)
    echo "✓ PostgreSQL client $PSQL_VERSION found"
    HAVE_PSQL=true
fi

echo ""
echo "All prerequisites met! 🎉"
echo ""

# ============================================================================
# 2. SET UP PYTHON VIRTUAL ENVIRONMENT
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Setting Up Python Virtual Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d ".venv" ]; then
    echo "⚠️  .venv already exists"
    read -p "Delete and recreate? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf .venv
        echo "✓ Removed existing .venv"
    else
        echo "→ Using existing .venv"
    fi
fi

if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
else
    echo "❌ Could not find activation script"
    exit 1
fi
echo "✓ Virtual environment activated"
echo ""

# ============================================================================
# 3. INSTALL DEPENDENCIES
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Installing Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📥 Upgrading pip..."
pip install --upgrade pip -q
echo "✓ pip upgraded"

echo "📥 Installing Python dependencies..."
pip install -r requirements.txt -q
echo "✓ Python dependencies installed"

echo "📥 Installing Node.js dependencies..."
cd frontend
npm install --silent
cd ..
echo "✓ Node.js dependencies installed"
echo ""

# ============================================================================
# 4. CONFIGURE ENVIRONMENT
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Configuring Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f ".env" ]; then
    echo "⚠️  .env file already exists"
    read -p "Overwrite with .env.dev? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.dev .env
        echo "✓ .env copied from .env.dev"
    else
        echo "→ Using existing .env"
    fi
else
    if [ -f ".env.dev" ]; then
        cp .env.dev .env
        echo "✓ .env copied from .env.dev"
    else
        echo "❌ .env.dev not found. Creating minimal .env..."
        cat > .env << 'EOF'
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=service_provider_new
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DJANGO_PORT=8100
EOF
        echo "⚠️  Created minimal .env - please update database credentials!"
    fi
fi

# Load environment variables
set -a
source .env
set +a
echo "✓ Environment variables loaded"
echo ""

# ============================================================================
# 5. SET UP POSTGRESQL DATABASE
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Setting Up PostgreSQL Database"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$HAVE_PSQL" = true ]; then
    echo "🔍 Checking PostgreSQL connection..."
    if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c '\q' 2>/dev/null; then
        echo "✓ PostgreSQL connection successful"

        # Check if database exists
        DB_EXISTS=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | tr -d '[:space:]')

        if [ "$DB_EXISTS" = "1" ]; then
            echo "⚠️  Database '$DB_NAME' already exists"
            read -p "Drop and recreate? (y/n) " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "🗑️  Dropping database..."
                PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME"
                echo "✓ Database dropped"
            else
                echo "→ Using existing database"
            fi
        fi

        # Create database if needed
        DB_EXISTS=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | tr -d '[:space:]')
        if [ "$DB_EXISTS" != "1" ]; then
            echo "📊 Creating database '$DB_NAME'..."
            PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME"
            echo "✓ Database created"
        fi
    else
        echo "❌ Cannot connect to PostgreSQL"
        echo "   Host: $DB_HOST:$DB_PORT"
        echo "   User: $DB_USER"
        echo ""
        echo "Please ensure PostgreSQL is running and credentials in .env are correct."
        echo "Then manually create database: CREATE DATABASE $DB_NAME;"
        exit 1
    fi
else
    echo "⚠️  PostgreSQL client not available"
    echo "Please manually:"
    echo "  1. Start PostgreSQL server"
    echo "  2. Create database: CREATE DATABASE $DB_NAME;"
    echo ""
    read -p "Press Enter when database is ready..."
fi
echo ""

# ============================================================================
# 6. RUN MIGRATIONS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  Running Database Migrations"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🔄 Running migrations..."
python manage.py migrate
echo "✓ Migrations complete"
echo ""

# ============================================================================
# 7. SEED INITIAL DATA
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  Seeding Initial Data"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🌱 Seeding development data..."
python manage.py seed_data
echo "✓ Sample data created"
echo ""

# ============================================================================
# 8. SET UP FRONTEND
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8️⃣  Setting Up Frontend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "⚛️  Frontend dependencies already installed"
echo "✓ Frontend ready"
echo ""

# ============================================================================
# 9. CREATE LOGS DIRECTORY
# ============================================================================
echo "📁 Creating logs directory..."
mkdir -p logs
echo "✓ Logs directory created"
echo ""

# ============================================================================
# SETUP COMPLETE
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Summary:"
echo "   • Virtual environment: .venv/"
echo "   • Database: $DB_NAME"
echo "   • Django port: ${DJANGO_PORT:-8100}"
echo "   • Sample data loaded"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "   1. Start the backend:"
echo "      python manage.py runserver ${DJANGO_PORT:-8100}"
echo ""
echo "   2. In another terminal, start the frontend:"
echo "      cd frontend && npm run dev"
echo ""
echo "   3. Access the application:"
echo "      • Frontend: http://localhost:5173"
echo "      • Backend API: http://localhost:${DJANGO_PORT:-8100}"
echo "      • Admin: http://localhost:${DJANGO_PORT:-8100}/admin"
echo ""
echo "   4. Login credentials (from seed data):"
echo "      • Admin: admin@example.com / admin123"
echo "      • Inspector: inspector@example.com / inspector123"
echo ""
echo "💡 Useful commands:"
echo "   • Run tests: pytest"
echo "   • Django shell: python manage.py shell"
echo "   • Reset database: ./scripts/reset_dev.sh"
echo ""
echo "Your virtual environment is active."
echo "To deactivate: deactivate"
echo ""
