"""Tests for employee management and user access control."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.organization.models import Company, Department, Employee

User = get_user_model()


class EmployeeManagementTestCase(TestCase):
    """Test employee CRUD and user access management."""

    def setUp(self):
        """Set up test data."""
        # Clear any existing data (in case of keepdb)
        Employee.objects.all().delete()
        Department.objects.all().delete()
        Company.objects.all().delete()
        User.objects.all().delete()

        # Create company
        self.company = Company.objects.create(
            name="Test Company",
            dba_name="Test DBA"
        )

        # Create department
        self.department = Department.objects.create(
            name="Test Department",
            code="TEST"
        )

        # Create admin user for API access
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )

        # Create test employee without user account
        self.employee = Employee.objects.create(
            employee_number='EMP001',
            first_name='John',
            last_name='Doe',
            email='john.doe@test.com',
            base_department=self.department,
            certifications=[
                {
                    'standard': 'ANSI/SAIA A92.2',
                    'cert_number': 'A92-12345',
                    'expiry': '2025-12-31'
                }
            ]
        )

        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

    def test_employee_list(self):
        """Test listing employees."""
        response = self.client.get('/api/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['employee_number'], 'EMP001')

    def test_employee_create(self):
        """Test creating an employee."""
        data = {
            'employee_number': 'EMP002',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@test.com',
            'base_department': str(self.department.id),
            'certifications': [
                {
                    'standard': 'ANSI/SAIA A92.5',
                    'cert_number': 'A92-67890',
                    'expiry': '2026-06-30'
                }
            ]
        }
        response = self.client.post('/api/employees/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 2)

        employee = Employee.objects.get(employee_number='EMP002')
        self.assertEqual(employee.full_name, 'Jane Smith')
        self.assertEqual(len(employee.certifications), 1)

    def test_employee_update(self):
        """Test updating an employee."""
        data = {
            'employee_number': 'EMP001',
            'first_name': 'John',
            'last_name': 'Doe Updated',
            'email': 'john.updated@test.com',
            'base_department': str(self.department.id),
        }
        response = self.client.put(f'/api/employees/{self.employee.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.employee.refresh_from_db()
        self.assertEqual(self.employee.last_name, 'Doe Updated')
        self.assertEqual(self.employee.email, 'john.updated@test.com')

    def test_has_user_account_false(self):
        """Test has_user_account is False when no user linked."""
        response = self.client.get(f'/api/employees/{self.employee.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_user_account'])
        self.assertIsNone(response.data['user_info'])

    def test_create_user_from_email(self):
        """Test creating user account from employee with email."""
        response = self.client.post(f'/api/employees/{self.employee.id}/create_user/', {})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('username', response.data)
        self.assertIn('temporary_password', response.data)
        self.assertEqual(response.data['username'], 'john.doe')

        # Verify employee is linked to user
        self.employee.refresh_from_db()
        self.assertIsNotNone(self.employee.user)
        self.assertEqual(self.employee.user.username, 'john.doe')
        self.assertEqual(self.employee.user.email, 'john.doe@test.com')
        self.assertEqual(self.employee.user.first_name, 'John')
        self.assertEqual(self.employee.user.last_name, 'Doe')

    def test_create_user_from_employee_number(self):
        """Test creating user account from employee without email."""
        self.employee.email = ''
        self.employee.save()

        response = self.client.post(f'/api/employees/{self.employee.id}/create_user/', {})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'emp_EMP001')

    def test_create_user_custom_username(self):
        """Test creating user account with custom username."""
        data = {
            'username': 'custom_user',
            'password': 'custom_pass123'
        }
        response = self.client.post(f'/api/employees/{self.employee.id}/create_user/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'custom_user')
        self.assertNotIn('temporary_password', response.data)  # Custom password provided

        # Verify user can log in with custom password
        user = User.objects.get(username='custom_user')
        self.assertTrue(user.check_password('custom_pass123'))

    def test_create_user_username_uniqueness(self):
        """Test username auto-increments for uniqueness."""
        # Create user with conflicting username
        User.objects.create_user(username='john.doe', password='pass123')

        response = self.client.post(f'/api/employees/{self.employee.id}/create_user/', {})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'john.doe1')

    def test_create_user_already_exists(self):
        """Test cannot create user when employee already has one."""
        # Create user first
        self.client.post(f'/api/employees/{self.employee.id}/create_user/', {})

        # Try to create again
        response = self.client.post(f'/api/employees/{self.employee.id}/create_user/', {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_create_user_duplicate_username(self):
        """Test error when custom username already exists."""
        User.objects.create_user(username='duplicate', password='pass123')

        data = {'username': 'duplicate'}
        response = self.client.post(f'/api/employees/{self.employee.id}/create_user/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_has_user_account_true(self):
        """Test has_user_account is True after user created."""
        self.client.post(f'/api/employees/{self.employee.id}/create_user/', {})

        response = self.client.get(f'/api/employees/{self.employee.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_user_account'])
        self.assertIsNotNone(response.data['user_info'])
        self.assertIn('username', response.data['user_info'])
        self.assertIn('is_active', response.data['user_info'])

    def test_revoke_user_deactivate(self):
        """Test revoking user account (deactivate and unlink)."""
        # Create user first
        self.client.post(f'/api/employees/{self.employee.id}/create_user/', {})

        # Refresh employee to get the user link
        self.employee.refresh_from_db()
        user = self.employee.user
        username = user.username

        # Revoke access
        response = self.client.post(f'/api/employees/{self.employee.id}/revoke_user/', {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

        # Verify employee no longer linked to user
        self.employee.refresh_from_db()
        self.assertIsNone(self.employee.user)

        # Verify user still exists but is inactive
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_revoke_user_delete(self):
        """Test deleting user account entirely."""
        # Create user first
        self.client.post(f'/api/employees/{self.employee.id}/create_user/', {})

        # Refresh employee to get the user link
        self.employee.refresh_from_db()
        user_id = self.employee.user.id

        # Delete user
        data = {'delete_user': True}
        response = self.client.post(f'/api/employees/{self.employee.id}/revoke_user/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify employee no longer linked
        self.employee.refresh_from_db()
        self.assertIsNone(self.employee.user)

        # Verify user is deleted
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_revoke_user_no_account(self):
        """Test error when revoking non-existent user account."""
        response = self.client.post(f'/api/employees/{self.employee.id}/revoke_user/', {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_employee_certifications(self):
        """Test employee certifications are stored and retrieved correctly."""
        response = self.client.get(f'/api/employees/{self.employee.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['certifications']), 1)
        cert = response.data['certifications'][0]
        self.assertEqual(cert['standard'], 'ANSI/SAIA A92.2')
        self.assertEqual(cert['cert_number'], 'A92-12345')
        self.assertEqual(cert['expiry'], '2025-12-31')

    def test_employee_filter_active(self):
        """Test filtering employees by active status."""
        # Mark existing employee as inactive
        self.employee.is_active = False
        self.employee.save()

        # Verify it was saved
        self.employee.refresh_from_db()
        self.assertFalse(self.employee.is_active)

        # Create new active employee with unique employee number
        active_emp = Employee.objects.create(
            employee_number='EMP_ACTIVE_TEST',
            first_name='Active',
            last_name='User',
            base_department=self.department,
            is_active=True
        )

        # Create inactive employee
        inactive_emp = Employee.objects.create(
            employee_number='EMP_INACTIVE_TEST',
            first_name='Inactive',
            last_name='User',
            base_department=self.department,
            is_active=False
        )

        # Test active filter
        response = self.client.get('/api/employees/?is_active=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        active_employee_numbers = [emp['employee_number'] for emp in response.data['results']]
        self.assertIn('EMP_ACTIVE_TEST', active_employee_numbers)

        # Test inactive filter
        response = self.client.get('/api/employees/?is_active=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        inactive_employee_numbers = [emp['employee_number'] for emp in response.data['results']]
        self.assertIn('EMP001', inactive_employee_numbers)
        self.assertIn('EMP_INACTIVE_TEST', inactive_employee_numbers)

    def test_employee_search(self):
        """Test searching employees by name and employee number."""
        # Create another employee to ensure searching works
        Employee.objects.create(
            employee_number='EMP999',
            first_name='Jane',
            last_name='Different',
            base_department=self.department,
        )

        # Search by first name (should match John)
        response = self.client.get('/api/employees/?search=John')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        names = [emp['first_name'] for emp in response.data['results']]
        self.assertIn('John', names)

        # Search by employee number (should match EMP001)
        response = self.client.get('/api/employees/?search=EMP001')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        employee_numbers = [emp['employee_number'] for emp in response.data['results']]
        self.assertIn('EMP001', employee_numbers)

        # Search by different employee number (should match EMP999)
        response = self.client.get('/api/employees/?search=999')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        employee_numbers = [emp['employee_number'] for emp in response.data['results']]
        self.assertIn('EMP999', employee_numbers)

        # Search by email (if employee has email, should match)
        response = self.client.get('/api/employees/?search=john.doe@test.com')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        emails = [emp.get('email') for emp in response.data['results'] if emp.get('email')]
        self.assertIn('john.doe@test.com', emails)
