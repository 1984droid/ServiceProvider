#!/bin/bash
# Reset development database (DESTRUCTIVE - dev only!)

set -e

echo "=================================="
echo "⚠️  DATABASE RESET (DEVELOPMENT ONLY)"
echo "=================================="
echo ""
echo "This will:"
echo "  - Drop and recreate the database"
echo "  - Run all migrations from scratch"
echo "  - Delete all data"
echo ""
read -p "Are you sure? (type 'yes' to continue): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "🔧 Loading environment..."
source .env

echo "🗑️  Dropping database: $DB_NAME"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"

echo "🗄️  Creating database: $DB_NAME"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"

echo "🔄 Running migrations..."
python manage.py migrate

echo "👥 Creating roles and groups..."
python manage.py create_roles

echo "🌱 Seeding test data..."
python manage.py seed_data

echo ""
echo "✅ Database reset complete!"
echo ""
echo "You can now log in with:"
echo "  Username: inspector1, inspector2, service1, service2, or support1"
echo "  Password: password123"
echo ""
