#!/usr/bin/env python
"""
Generate .env file with secure random values.

This script creates a new .env file from .env.example and:
- Generates a cryptographically secure SECRET_KEY
- Generates a strong random database password
- Sets secure defaults for development

Usage:
    python generate_env.py
"""

import os
import secrets
import string
from pathlib import Path


def generate_secret_key(length=50):
    """Generate a Django SECRET_KEY using cryptographically secure random."""
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_db_password(length=32):
    """Generate a strong database password."""
    # Avoid special chars that might cause issues in connection strings
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_env_file():
    """Generate .env file from .env.example with secure random values."""

    env_example = Path('.env.example')
    env_file = Path('.env')

    # Check if .env already exists
    if env_file.exists():
        response = input('.env file already exists. Overwrite? (yes/no): ')
        if response.lower() != 'yes':
            print('Aborted. Existing .env file preserved.')
            return False

    # Check if .env.example exists
    if not env_example.exists():
        print('Error: .env.example not found!')
        return False

    # Read .env.example
    with open(env_example, 'r') as f:
        content = f.read()

    # Generate secure values
    secret_key = generate_secret_key()
    db_password = generate_db_password()

    # Replace placeholders
    replacements = {
        'your-secret-key-here-change-in-production': secret_key,
        'postgres': db_password,  # Replace default password
    }

    new_content = content
    for old, new in replacements.items():
        # Only replace in DB_PASSWORD line
        lines = []
        for line in new_content.split('\n'):
            if line.startswith('SECRET_KEY=') and 'your-secret-key-here' in line:
                lines.append(f'SECRET_KEY={secret_key}')
            elif line.startswith('DB_PASSWORD=') and old in line:
                lines.append(f'DB_PASSWORD={db_password}')
            else:
                lines.append(line)
        new_content = '\n'.join(lines)

    # Write new .env file
    with open(env_file, 'w') as f:
        f.write(new_content)

    print('✅ .env file created successfully!')
    print()
    print('Generated values:')
    print(f'  SECRET_KEY: {secret_key[:20]}... (length: {len(secret_key)})')
    print(f'  DB_PASSWORD: {db_password[:10]}... (length: {len(db_password)})')
    print()
    print('⚠️  IMPORTANT:')
    print('  1. Review .env and adjust DB_NAME, DB_USER, DB_HOST if needed')
    print('  2. Keep .env secure - it is in .gitignore')
    print('  3. Never commit .env to version control')
    print()
    print('Next steps:')
    print('  1. Create PostgreSQL user and database:')
    print(f'     createuser postgres')
    print(f'     psql -U postgres -c "ALTER USER postgres PASSWORD \'{db_password}\';"')
    print('     createdb -U postgres service_provider')
    print()
    print('  2. Run setup:')
    print('     ./setup_dev.sh  (or setup_dev.bat on Windows)')
    print()

    return True


if __name__ == '__main__':
    print('=' * 50)
    print('Generate .env with Secure Random Values')
    print('=' * 50)
    print()

    success = generate_env_file()

    if not success:
        exit(1)
