#!/usr/bin/env python
"""
NEW_BUILD_STARTER Setup Script

Comprehensive setup, update, and wipe utilities for development and deployment.
Handles database creation, migrations, dependencies, and environment configuration.

Usage:
    python setup.py setup      # Initial setup (first time)
    python setup.py update     # Update existing installation
    python setup.py wipe       # Wipe database and start fresh
    python setup.py reset      # Wipe + Setup (full reset)
    python setup.py status     # Check current status

Requirements:
    - Python 3.14+
    - PostgreSQL 18+ installed and running
    - Virtual environment recommended
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
from typing import Optional, Tuple


# Configuration
PROJECT_ROOT = Path(__file__).parent
DEFAULT_DB_NAME = "service_provider_new"
DEFAULT_DB_USER = "postgres"
DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT = "5432"
DJANGO_PORT = "8100"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(message: str):
    """Print formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")


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


def run_command(command: str, capture_output: bool = False, check: bool = True) -> Optional[subprocess.CompletedProcess]:
    """
    Run shell command with error handling.

    Args:
        command: Command to run
        capture_output: Capture stdout/stderr
        check: Raise exception on non-zero exit

    Returns:
        CompletedProcess if capture_output=True, else None
    """
    print_info(f"Running: {command}")

    try:
        if capture_output:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=check
            )
            return result
        else:
            subprocess.run(command, shell=True, check=check)
            return None
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        if capture_output and e.stderr:
            print_error(f"Error: {e.stderr}")
        raise


def check_python_version():
    """Check if Python version meets requirements."""
    print_info("Checking Python version...")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 14):
        print_error(f"Python 3.14+ required, found {version.major}.{version.minor}")
        return False

    print_success(f"Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_postgresql():
    """Check if PostgreSQL is installed and accessible."""
    print_info("Checking PostgreSQL...")

    try:
        result = run_command("psql --version", capture_output=True, check=True)
        version = result.stdout.strip()
        print_success(f"PostgreSQL found: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("PostgreSQL not found or not in PATH")
        print_warning("Please install PostgreSQL 18+ and ensure psql is in your PATH")
        return False


def check_virtual_environment():
    """Check if running in virtual environment."""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    if in_venv:
        print_success("Running in virtual environment")
    else:
        print_warning("Not running in virtual environment")
        print_warning("Recommended: Create and activate a virtual environment first")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False

    return True


def create_env_file():
    """Create .env file from .env.example if it doesn't exist."""
    print_info("Checking .env file...")

    env_file = PROJECT_ROOT / ".env"
    env_example = PROJECT_ROOT / ".env.example"

    if env_file.exists():
        print_success(".env file already exists")
        return True

    if not env_example.exists():
        print_error(".env.example not found!")
        return False

    # Copy example file
    shutil.copy(env_example, env_file)
    print_success("Created .env from .env.example")

    # Update with correct database name
    content = env_file.read_text()
    content = content.replace("DB_NAME=service_provider", f"DB_NAME={DEFAULT_DB_NAME}")
    content = content.replace("# Database (PostgreSQL)", f"# Database (PostgreSQL)\nDJANGO_PORT={DJANGO_PORT}")
    env_file.write_text(content)
    print_success(f"Updated .env with DB_NAME={DEFAULT_DB_NAME}")

    return True


def load_env_vars() -> dict:
    """Load environment variables from .env file."""
    env_file = PROJECT_ROOT / ".env"
    env_vars = {}

    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value

    # Set defaults
    env_vars.setdefault('DB_NAME', DEFAULT_DB_NAME)
    env_vars.setdefault('DB_USER', DEFAULT_DB_USER)
    env_vars.setdefault('DB_HOST', DEFAULT_DB_HOST)
    env_vars.setdefault('DB_PORT', DEFAULT_DB_PORT)

    return env_vars


def check_database_exists(db_name: str, db_user: str) -> bool:
    """Check if database exists."""
    try:
        result = run_command(
            f'psql -U {db_user} -lqt',
            capture_output=True,
            check=True
        )
        databases = [line.split('|')[0].strip() for line in result.stdout.split('\n')]
        return db_name in databases
    except subprocess.CalledProcessError:
        return False


def create_database(db_name: str, db_user: str):
    """Create PostgreSQL database."""
    print_info(f"Creating database '{db_name}'...")

    if check_database_exists(db_name, db_user):
        print_success(f"Database '{db_name}' already exists")
        return True

    try:
        run_command(
            f'psql -U {db_user} -c "CREATE DATABASE {db_name};"',
            capture_output=True,
            check=True
        )
        print_success(f"Database '{db_name}' created")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create database: {e}")
        print_warning("You may need to run this command manually:")
        print_warning(f'  psql -U {db_user} -c "CREATE DATABASE {db_name};"')
        return False


def drop_database(db_name: str, db_user: str):
    """Drop PostgreSQL database."""
    print_info(f"Dropping database '{db_name}'...")

    if not check_database_exists(db_name, db_user):
        print_warning(f"Database '{db_name}' does not exist")
        return True

    try:
        # Terminate existing connections
        run_command(
            f'''psql -U {db_user} -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}';"''',
            capture_output=True,
            check=False
        )

        # Drop database
        run_command(
            f'psql -U {db_user} -c "DROP DATABASE {db_name};"',
            capture_output=True,
            check=True
        )
        print_success(f"Database '{db_name}' dropped")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to drop database: {e}")
        return False


def install_dependencies():
    """Install Python dependencies from requirements.txt."""
    print_info("Installing dependencies...")

    requirements_file = PROJECT_ROOT / "requirements.txt"
    if not requirements_file.exists():
        print_error("requirements.txt not found!")
        return False

    try:
        run_command(f"{sys.executable} -m pip install --upgrade pip")
        run_command(f"{sys.executable} -m pip install -r requirements.txt")
        print_success("Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install dependencies")
        return False


def run_migrations():
    """Run Django migrations."""
    print_info("Running migrations...")

    try:
        run_command(f"{sys.executable} manage.py migrate")
        print_success("Migrations applied")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to run migrations")
        return False


def create_superuser(interactive: bool = True):
    """Create Django superuser."""
    print_info("Creating superuser...")

    if interactive:
        try:
            run_command(f"{sys.executable} manage.py createsuperuser")
            print_success("Superuser created")
            return True
        except subprocess.CalledProcessError:
            print_warning("Superuser creation skipped or failed")
            return False
    else:
        print_warning("Skipping superuser creation (non-interactive mode)")
        print_info("Run manually: python manage.py createsuperuser")
        return True


def collect_static():
    """Collect static files."""
    print_info("Collecting static files...")

    try:
        run_command(f"{sys.executable} manage.py collectstatic --noinput")
        print_success("Static files collected")
        return True
    except subprocess.CalledProcessError:
        print_warning("Failed to collect static files (may not be configured yet)")
        return True


def clean_migrations():
    """Remove all migration files (except __init__.py)."""
    print_info("Cleaning migration files...")

    apps_dir = PROJECT_ROOT / "apps"
    count = 0

    for app_dir in apps_dir.iterdir():
        if app_dir.is_dir():
            migrations_dir = app_dir / "migrations"
            if migrations_dir.exists():
                for file in migrations_dir.iterdir():
                    if file.name != "__init__.py" and file.suffix == ".py":
                        file.unlink()
                        count += 1

    print_success(f"Removed {count} migration files")
    return True


def clean_pycache():
    """Remove all __pycache__ directories."""
    print_info("Cleaning __pycache__ directories...")

    count = 0
    for pycache_dir in PROJECT_ROOT.rglob("__pycache__"):
        shutil.rmtree(pycache_dir)
        count += 1

    print_success(f"Removed {count} __pycache__ directories")
    return True


def show_status():
    """Show current system status."""
    print_header("System Status")

    # Python
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")

    # Virtual Environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    print(f"Virtual Environment: {'Yes' if in_venv else 'No'}")

    # PostgreSQL
    try:
        result = run_command("psql --version", capture_output=True, check=True)
        print(f"PostgreSQL: {result.stdout.strip()}")
    except:
        print("PostgreSQL: Not found")

    # .env file
    env_file = PROJECT_ROOT / ".env"
    print(f".env file: {'Exists' if env_file.exists() else 'Missing'}")

    # Database
    env_vars = load_env_vars()
    db_exists = check_database_exists(env_vars['DB_NAME'], env_vars['DB_USER'])
    print(f"Database ({env_vars['DB_NAME']}): {'Exists' if db_exists else 'Not found'}")

    # Django
    try:
        result = run_command(
            f"{sys.executable} manage.py showmigrations --list",
            capture_output=True,
            check=False
        )
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            applied = sum(1 for line in lines if '[X]' in line)
            unapplied = sum(1 for line in lines if '[ ]' in line)
            print(f"Migrations: {applied} applied, {unapplied} unapplied")
        else:
            print("Migrations: Unable to check")
    except:
        print("Migrations: Unable to check")

    print()


def setup():
    """Run initial setup."""
    print_header("NEW_BUILD_STARTER - Initial Setup")

    # Pre-flight checks
    if not check_python_version():
        return False

    if not check_postgresql():
        return False

    if not check_virtual_environment():
        return False

    # Create .env file
    if not create_env_file():
        return False

    # Load environment variables
    env_vars = load_env_vars()

    # Install dependencies
    if not install_dependencies():
        return False

    # Create database
    if not create_database(env_vars['DB_NAME'], env_vars['DB_USER']):
        print_warning("Database creation failed, but continuing...")
        print_warning("Please create the database manually before running migrations")

    # Run migrations
    if not run_migrations():
        return False

    # Create superuser
    create_superuser(interactive=True)

    # Collect static files
    collect_static()

    # Success
    print_header("Setup Complete!")
    print_success("NEW_BUILD_STARTER is ready to use")
    print_info(f"Start server: python manage.py runserver {DJANGO_PORT}")
    print_info(f"Admin interface: http://localhost:{DJANGO_PORT}/admin")
    print_info(f"API root: http://localhost:{DJANGO_PORT}/api/")
    print()

    return True


def update():
    """Update existing installation."""
    print_header("NEW_BUILD_STARTER - Update")

    # Install/update dependencies
    if not install_dependencies():
        return False

    # Run migrations
    if not run_migrations():
        return False

    # Collect static files
    collect_static()

    # Clean cache
    clean_pycache()

    print_header("Update Complete!")
    print_success("NEW_BUILD_STARTER is up to date")
    print()

    return True


def wipe():
    """Wipe database and migrations."""
    print_header("NEW_BUILD_STARTER - Wipe Database")

    print_warning("This will:")
    print_warning("  1. Drop the database (all data will be lost)")
    print_warning("  2. Recreate empty database")
    print_warning("  3. Remove all migration files")
    print_warning("  4. Clean __pycache__ directories")
    print()

    response = input(f"{Colors.BOLD}Are you sure? Type 'yes' to confirm: {Colors.ENDC}")
    if response.lower() != 'yes':
        print_info("Wipe cancelled")
        return False

    # Load environment variables
    env_vars = load_env_vars()

    # Drop database
    if not drop_database(env_vars['DB_NAME'], env_vars['DB_USER']):
        print_error("Failed to drop database")
        return False

    # Recreate database
    if not create_database(env_vars['DB_NAME'], env_vars['DB_USER']):
        print_warning("Failed to recreate database")
        print_warning("You may need to create it manually before running setup")

    # Clean migrations
    clean_migrations()

    # Clean cache
    clean_pycache()

    print_header("Wipe Complete!")
    print_success("Database wiped and recreated (empty)")
    print_success("Migration files removed")
    print_info("Run 'python setup.py setup' to rebuild migrations and apply them")
    print()

    return True


def reset():
    """Wipe and setup (full reset)."""
    print_header("NEW_BUILD_STARTER - Full Reset")

    if wipe():
        return setup()
    return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_header("NEW_BUILD_STARTER Setup Script")
        print("Usage:")
        print("  python setup.py setup      # Initial setup (first time)")
        print("  python setup.py update     # Update existing installation")
        print("  python setup.py wipe       # Wipe database and migrations")
        print("  python setup.py reset      # Wipe + Setup (full reset)")
        print("  python setup.py status     # Check current status")
        print()
        return 1

    command = sys.argv[1].lower()

    # Change to project directory
    os.chdir(PROJECT_ROOT)

    if command == "setup":
        success = setup()
    elif command == "update":
        success = update()
    elif command == "wipe":
        success = wipe()
    elif command == "reset":
        success = reset()
    elif command == "status":
        show_status()
        success = True
    else:
        print_error(f"Unknown command: {command}")
        print_info("Valid commands: setup, update, wipe, reset, status")
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
