"""
Reset Database Script

WARNING: This will completely destroy all data and recreate the database from scratch.

Usage:
    python scripts/reset_database.py [--yes]

Options:
    --yes    Skip confirmation prompt
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def reset_database(skip_confirm=False):
    """Completely reset the database."""
    print("=" * 80)
    print("DATABASE RESET SCRIPT")
    print("=" * 80)
    print("\nWARNING: This will PERMANENTLY DELETE ALL DATA in the database!")
    print("\nThis script will:")
    print("  1. Drop all tables")
    print("  2. Run migrations from scratch")
    print("  3. Create default groups/roles")
    print("  4. Seed test data")
    print("  5. Grant superuser to admin employee")
    print("\n" + "=" * 80)

    if not skip_confirm:
        response = input("\nType 'YES' to continue: ")
        if response != 'YES':
            print("Aborted.")
            return

    print("\n[1/5] Dropping all tables...")
    with connection.cursor() as cursor:
        # Get all table names
        cursor.execute("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
        """)
        tables = cursor.fetchall()

        # Drop all tables
        for table in tables:
            print(f"  Dropping table: {table[0]}")
            cursor.execute(f'DROP TABLE IF EXISTS "{table[0]}" CASCADE')

    print("[OK] All tables dropped")

    print("\n[2/5] Running migrations...")
    call_command('migrate', verbosity=1)
    print("[OK] Migrations complete")

    print("\n[3/5] Creating groups and roles...")
    call_command('create_roles')
    print("[OK] Groups created")

    print("\n[4/5] Seeding realistic test data...")
    call_command('seed_data_realistic', '--clear')
    print("[OK] Realistic test data seeded")

    print("\n[5/5] Granting superuser privileges to admin employee...")
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # The seed_data creates David Anderson (EMP001) with username 'admin'
    # Make him a superuser
    try:
        admin = User.objects.get(username='admin')
        admin.is_superuser = True
        admin.is_staff = True
        admin.save()
        print(f"[OK] David Anderson (admin) granted superuser privileges")
    except User.DoesNotExist:
        print("[ERROR] Admin user not found - seed_data may have failed")

    print("\n" + "=" * 80)
    print("DATABASE RESET COMPLETE!")
    print("=" * 80)
    print("\nYou can now log in with:")
    print("  Username: admin")
    print("  Password: admin")
    print("  Employee: David Anderson (EMP006)")
    print("\n" + "=" * 80)

if __name__ == '__main__':
    skip_confirm = '--yes' in sys.argv or '-y' in sys.argv
    reset_database(skip_confirm=skip_confirm)
