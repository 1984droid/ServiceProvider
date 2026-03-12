"""
Test authentication endpoints.

Quick script to verify JWT auth is working correctly.
"""
import os
import sys
import django
import requests
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organization.models import Department, Employee

BASE_URL = 'http://localhost:8100/api'


def create_test_user():
    """Create a test user with Inspector role."""
    # Create department
    dept, _ = Department.objects.get_or_create(
        code='INSP',
        defaults={'name': 'Inspection Department'}
    )

    # Create employee
    employee, _ = Employee.objects.get_or_create(
        employee_number='TEST001',
        defaults={
            'first_name': 'John',
            'last_name': 'Tester',
            'email': 'john.tester@example.com',
            'base_department': dept,
        }
    )

    # Create user
    user, created = User.objects.get_or_create(
        username='test.inspector',
        defaults={
            'email': 'john.tester@example.com',
            'first_name': 'John',
            'last_name': 'Tester',
        }
    )

    if created:
        user.set_password('TestPass123!')
        user.save()
        print(f'Created user: {user.username}')
    else:
        # Update password in case it changed
        user.set_password('TestPass123!')
        user.save()
        print(f'User exists: {user.username}')

    # Link employee to user
    if not employee.user:
        employee.user = user
        employee.save()
        print(f'Linked employee to user')

    # Assign INSPECTOR role
    from django.contrib.auth.models import Group
    inspector_group = Group.objects.get(name='INSPECTOR')
    user.groups.add(inspector_group)
    print(f'Assigned INSPECTOR role')

    return user


def test_login():
    """Test login endpoint."""
    print('\n' + '='*60)
    print('TEST: Login')
    print('='*60)

    response = requests.post(
        f'{BASE_URL}/auth/login/',
        json={
            'username': 'test.inspector',
            'password': 'TestPass123!'
        }
    )

    print(f'Status: {response.status_code}')

    if response.status_code == 200:
        data = response.json()
        print(f'[OK] Login successful')
        print(f'  Access Token: {data["access"][:50]}...')
        print(f'  Refresh Token: {data["refresh"][:50]}...')
        print(f'  User: {data["user"]["username"]}')
        print(f'  Roles: {data["user"]["roles"]}')
        print(f'  Permissions: {len(data["user"]["permissions"])} permissions')
        return data['access'], data['refresh']
    else:
        print(f'[FAIL] Login failed: {response.text}')
        return None, None


def test_me(access_token):
    """Test /me endpoint."""
    print('\n' + '='*60)
    print('TEST: Get Current User Profile')
    print('='*60)

    response = requests.get(
        f'{BASE_URL}/auth/me/',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    print(f'Status: {response.status_code}')

    if response.status_code == 200:
        data = response.json()
        print(f'[OK] Profile retrieved')
        print(f'  Username: {data["username"]}')
        print(f'  Email: {data["email"]}')
        print(f'  Roles: {data["roles"]}')
        print(f'  Employee: {data["employee"]["full_name"] if data["employee"] else "None"}')
        print(f'  Department: {data["employee"]["department"] if data["employee"] else "None"}')
    else:
        print(f'[FAIL] Failed: {response.text}')


def test_refresh(refresh_token):
    """Test token refresh."""
    print('\n' + '='*60)
    print('TEST: Refresh Token')
    print('='*60)

    response = requests.post(
        f'{BASE_URL}/auth/refresh/',
        json={'refresh': refresh_token}
    )

    print(f'Status: {response.status_code}')

    if response.status_code == 200:
        data = response.json()
        print(f'[OK] Token refreshed')
        print(f'  New Access Token: {data["access"][:50]}...')
        if 'refresh' in data:
            print(f'  New Refresh Token: {data["refresh"][:50]}...')
        return data['access'], data.get('refresh')
    else:
        print(f'[FAIL] Failed: {response.text}')
        return None, None


def test_logout(refresh_token):
    """Test logout."""
    print('\n' + '='*60)
    print('TEST: Logout')
    print('='*60)

    response = requests.post(
        f'{BASE_URL}/auth/logout/',
        json={'refresh': refresh_token},
        headers={'Authorization': f'Bearer {access_token}'}
    )

    print(f'Status: {response.status_code}')

    if response.status_code == 200:
        print(f'[OK] Logout successful')
    else:
        print(f'[FAIL] Failed: {response.text}')


def test_protected_endpoint(access_token):
    """Test accessing protected endpoint."""
    print('\n' + '='*60)
    print('TEST: Access Protected Endpoint (Inspections List)')
    print('='*60)

    response = requests.get(
        f'{BASE_URL}/inspections/',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    print(f'Status: {response.status_code}')

    if response.status_code == 200:
        print(f'[OK] Access granted')
        data = response.json()
        print(f'  Found {data.get("count", 0)} inspections')
    else:
        print(f'[FAIL] Failed: {response.text}')


if __name__ == '__main__':
    print('\nAuthentication System Test')
    print('='*60)

    # Create test user
    user = create_test_user()

    # Run tests
    access_token, refresh_token = test_login()

    if access_token:
        test_me(access_token)
        test_protected_endpoint(access_token)

        new_access, new_refresh = test_refresh(refresh_token)
        if new_access:
            access_token = new_access
            if new_refresh:
                refresh_token = new_refresh

        test_logout(refresh_token)

    print('\n' + '='*60)
    print('Test Complete')
    print('='*60 + '\n')
