#!/usr/bin/env python
"""
Production Deployment Script for Service Provider Application

Handles production deployment with security best practices, environment configuration,
and deployment verification.

Usage:
    python deploy.py setup      # Initial production setup
    python deploy.py update     # Update existing production installation
    python deploy.py check      # Check production readiness
    python deploy.py backup     # Backup database
    python deploy.py restore    # Restore from backup

Requirements:
    - Python 3.14+
    - PostgreSQL 18+ installed and running
    - gunicorn for production server
    - nginx for reverse proxy (recommended)
"""

import os
import sys
import subprocess
import secrets
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional


# Configuration
PROJECT_ROOT = Path(__file__).parent
BACKUP_DIR = PROJECT_ROOT / "backups"


# Colors for terminal output
class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    OKCYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_success(message: str):
    """Print success message."""
    try:
        print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")
    except UnicodeEncodeError:
        print(f"{Colors.OKGREEN}[OK] {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message."""
    try:
        print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")
    except UnicodeEncodeError:
        print(f"{Colors.FAIL}[ERROR] {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print warning message."""
    try:
        print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")
    except UnicodeEncodeError:
        print(f"{Colors.WARNING}[WARNING] {message}{Colors.ENDC}")


def print_info(message: str):
    """Print info message."""
    try:
        print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")
    except UnicodeEncodeError:
        print(f"{Colors.OKCYAN}[INFO] {message}{Colors.ENDC}")


def run_command(command: str, capture_output: bool = False) -> Optional[subprocess.CompletedProcess]:
    """Run shell command with error handling."""
    print_info(f"Running: {command}")
    try:
        if capture_output:
            return subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        else:
            subprocess.run(command, shell=True, check=True)
            return None
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        if capture_output and e.stderr:
            print_error(f"Error: {e.stderr}")
        raise


def generate_secret_key() -> str:
    """Generate a secure Django secret key."""
    return secrets.token_urlsafe(50)


def create_production_env():
    """Create production .env file with secure defaults."""
    print_info("Creating production .env file...")

    env_file = PROJECT_ROOT / ".env.production"

    if env_file.exists():
        response = input("Production .env exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print_info("Skipping .env creation")
            return

    secret_key = generate_secret_key()

    # Get configuration from user
    db_name = input("Database name [service_provider_prod]: ").strip() or "service_provider_prod"
    db_user = input("Database user [postgres]: ").strip() or "postgres"
    db_password = input("Database password: ").strip()
    db_host = input("Database host [localhost]: ").strip() or "localhost"
    db_port = input("Database port [8101]: ").strip() or "8101"
    allowed_hosts = input("Allowed hosts (comma-separated) [yourdomain.com]: ").strip() or "yourdomain.com"

    env_content = f"""# Production Django Settings
SECRET_KEY={secret_key}
DEBUG=False
ALLOWED_HOSTS={allowed_hosts}

# Database (PostgreSQL 18+)
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_HOST={db_host}
DB_PORT={db_port}

# Server
DJANGO_PORT=8100

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# CORS (adjust for your frontend)
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=INFO
"""

    env_file.write_text(env_content)
    print_success(f"Created {env_file}")
    print_warning("IMPORTANT: Review and update .env.production with your actual values!")


def install_production_dependencies():
    """Install production dependencies."""
    print_info("Installing production dependencies...")

    # Create requirements-prod.txt if it doesn't exist
    requirements_prod = PROJECT_ROOT / "requirements-prod.txt"
    if not requirements_prod.exists():
        prod_deps = """# Production dependencies
-r requirements.txt

# Production server
gunicorn>=21.0.0
whitenoise>=6.6.0

# Monitoring
sentry-sdk>=1.40.0

# Performance
django-redis>=5.4.0
"""
        requirements_prod.write_text(prod_deps)
        print_success("Created requirements-prod.txt")

    run_command(f"{sys.executable} -m pip install --upgrade pip")
    run_command(f"{sys.executable} -m pip install -r requirements-prod.txt")
    print_success("Production dependencies installed")


def create_database():
    """Create production database."""
    print_info("Creating production database...")

    # Load env vars
    env_file = PROJECT_ROOT / ".env.production"
    if not env_file.exists():
        print_error(".env.production not found! Run 'python deploy.py setup' first.")
        sys.exit(1)

    env_vars = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value

    db_name = env_vars.get('DB_NAME', 'service_provider_prod')
    db_user = env_vars.get('DB_USER', 'postgres')
    db_password = env_vars.get('DB_PASSWORD', '')
    db_host = env_vars.get('DB_HOST', 'localhost')
    db_port = env_vars.get('DB_PORT', '8101')

    # Create database using Python
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

        conn = psycopg2.connect(
            dbname='postgres',
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f'CREATE DATABASE {db_name};')
            print_success(f"Database '{db_name}' created")
        else:
            print_info(f"Database '{db_name}' already exists")

        cursor.close()
        conn.close()
    except Exception as e:
        print_error(f"Failed to create database: {e}")
        sys.exit(1)


def run_migrations():
    """Run Django migrations."""
    print_info("Running migrations...")
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

    # Load production env
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env.production")

    run_command(f"{sys.executable} manage.py migrate --noinput")
    print_success("Migrations completed")


def collect_static():
    """Collect static files."""
    print_info("Collecting static files...")
    run_command(f"{sys.executable} manage.py collectstatic --noinput")
    print_success("Static files collected")


def create_superuser_script():
    """Create a script to create superuser in production."""
    script_content = """#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = input("Superuser username: ")
email = input("Email: ")
password = input("Password: ")

if User.objects.filter(username=username).exists():
    print(f"User '{username}' already exists!")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created successfully!")
"""

    script_file = PROJECT_ROOT / "create_superuser.py"
    script_file.write_text(script_content)
    print_success("Created create_superuser.py script")


def backup_database():
    """Backup production database."""
    print_info("Backing up database...")

    # Create backup directory
    BACKUP_DIR.mkdir(exist_ok=True)

    # Load env vars
    env_file = PROJECT_ROOT / ".env.production"
    env_vars = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value

    db_name = env_vars.get('DB_NAME', 'service_provider_prod')
    db_user = env_vars.get('DB_USER', 'postgres')
    db_host = env_vars.get('DB_HOST', 'localhost')
    db_port = env_vars.get('DB_PORT', '8101')

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f"{db_name}_{timestamp}.sql"

    # Set password env var for pg_dump
    os.environ['PGPASSWORD'] = env_vars.get('DB_PASSWORD', '')

    try:
        run_command(f'pg_dump -h {db_host} -p {db_port} -U {db_user} {db_name} > {backup_file}')
        print_success(f"Backup created: {backup_file}")
    except Exception as e:
        print_error(f"Backup failed: {e}")
        sys.exit(1)


def check_production_ready():
    """Check if application is production ready."""
    print_info("Checking production readiness...")

    checks_passed = True

    # Check .env.production
    if not (PROJECT_ROOT / ".env.production").exists():
        print_error(".env.production not found")
        checks_passed = False
    else:
        print_success(".env.production exists")

    # Check DEBUG is False
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env.production")

    if os.getenv('DEBUG', 'False') == 'True':
        print_error("DEBUG is True in .env.production - should be False!")
        checks_passed = False
    else:
        print_success("DEBUG is False")

    # Check SECRET_KEY is set and not default
    secret_key = os.getenv('SECRET_KEY', '')
    if not secret_key or 'change-me' in secret_key.lower():
        print_error("SECRET_KEY is not set or using default value")
        checks_passed = False
    else:
        print_success("SECRET_KEY is set")

    # Check ALLOWED_HOSTS
    allowed_hosts = os.getenv('ALLOWED_HOSTS', '')
    if not allowed_hosts or 'localhost' in allowed_hosts:
        print_warning("ALLOWED_HOSTS should be set to your production domain")
    else:
        print_success(f"ALLOWED_HOSTS: {allowed_hosts}")

    # Check database connection
    try:
        run_command(f"{sys.executable} manage.py check --database default", capture_output=True)
        print_success("Database connection OK")
    except:
        print_error("Database connection failed")
        checks_passed = False

    # Check static files
    if (PROJECT_ROOT / "staticfiles").exists():
        print_success("Static files collected")
    else:
        print_warning("Static files not collected - run collectstatic")

    if checks_passed:
        print_success("\n✓ Production readiness check PASSED")
    else:
        print_error("\n✗ Production readiness check FAILED - fix errors above")
        sys.exit(1)


def production_setup():
    """Full production setup."""
    print(f"\n{Colors.BOLD}=== Production Setup ==={Colors.ENDC}\n")

    create_production_env()
    install_production_dependencies()
    create_database()
    run_migrations()
    collect_static()
    create_superuser_script()

    print_success("\n✓ Production setup complete!")
    print_info("\nNext steps:")
    print("  1. Review and update .env.production with your actual values")
    print("  2. Run: python create_superuser.py")
    print("  3. Configure nginx as reverse proxy")
    print("  4. Start with: gunicorn config.wsgi:application --bind 0.0.0.0:8100")


def production_update():
    """Update production installation."""
    print(f"\n{Colors.BOLD}=== Production Update ==={Colors.ENDC}\n")

    # Backup first
    backup_database()

    install_production_dependencies()
    run_migrations()
    collect_static()

    print_success("\n✓ Production update complete!")
    print_info("Restart your gunicorn server to apply changes")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python deploy.py [setup|update|check|backup|restore]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'setup':
        production_setup()
    elif command == 'update':
        production_update()
    elif command == 'check':
        check_production_ready()
    elif command == 'backup':
        backup_database()
    elif command == 'restore':
        print_error("Restore not implemented yet")
        sys.exit(1)
    else:
        print_error(f"Unknown command: {command}")
        print("Usage: python deploy.py [setup|update|check|backup|restore]")
        sys.exit(1)


if __name__ == '__main__':
    main()
