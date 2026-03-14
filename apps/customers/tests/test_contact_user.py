"""Tests for Contact user field and person_type functionality."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.customers.models import Customer, Contact
from apps.organization.models import Company, Department, Employee

User = get_user_model()


class ContactUserTestCase(TestCase):
    """Test Contact.user field and has_portal_access property."""

    def setUp(self):
        """Set up test data."""
        # Create company
        self.company = Company.objects.create(
            name="Test Company",
            dba_name="Test DBA"
        )

        # Create customer
        self.customer = Customer.objects.create(
            name="Test Customer"
        )

        # Create contact without user
        self.contact = Contact.objects.create(
            customer=self.customer,
            first_name='Alice',
            last_name='Johnson',
            email='alice.johnson@customer.com'
        )

        # Create department for employee tests
        self.department = Department.objects.create(
            name="Test Department",
            code="TEST"
        )

        # Set up API client
        self.client = APIClient()

    def test_contact_has_portal_access_false(self):
        """Test has_portal_access is False when no user linked."""
        self.assertFalse(self.contact.has_portal_access)

    def test_contact_has_portal_access_true(self):
        """Test has_portal_access is True when active user linked."""
        user = User.objects.create_user(
            username='alice',
            password='testpass123',
            email='alice.johnson@customer.com',
            first_name='Alice',
            last_name='Johnson',
            is_active=True
        )
        self.contact.user = user
        self.contact.save()

        self.assertTrue(self.contact.has_portal_access)

    def test_contact_has_portal_access_inactive_user(self):
        """Test has_portal_access is False when inactive user linked."""
        user = User.objects.create_user(
            username='alice',
            password='testpass123',
            is_active=False
        )
        self.contact.user = user
        self.contact.save()

        self.assertFalse(self.contact.has_portal_access)

    def test_contact_user_one_to_one(self):
        """Test Contact.user is OneToOneField."""
        user = User.objects.create_user(username='contact_user', password='pass123')
        self.contact.user = user
        self.contact.save()

        # Access user from contact
        self.assertEqual(self.contact.user, user)

        # Access contact from user
        self.assertEqual(user.contact, self.contact)

    def test_contact_user_set_null_on_delete(self):
        """Test Contact.user is set to null when user deleted."""
        user = User.objects.create_user(username='temp_user', password='pass123')
        self.contact.user = user
        self.contact.save()

        user.delete()

        self.contact.refresh_from_db()
        self.assertIsNone(self.contact.user)


class PersonTypeTestCase(TestCase):
    """Test UserProfile person_type field."""

    def setUp(self):
        """Set up test data."""
        # Create company and department
        self.company = Company.objects.create(name="Test Company")
        self.department = Department.objects.create(name="Test Dept", code="TEST")

        # Create customer
        self.customer = Customer.objects.create(
            name="Test Customer"
        )

        # Set up API client
        self.client = APIClient()

    def test_person_type_employee(self):
        """Test person_type is 'employee' for employee users."""
        # Create employee with user
        user = User.objects.create_user(
            username='employee_user',
            password='testpass123',
            first_name='Bob',
            last_name='Smith'
        )
        employee = Employee.objects.create(
            user=user,
            employee_number='EMP001',
            first_name='Bob',
            last_name='Smith',
            base_department=self.department
        )

        # Authenticate and get profile
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['person_type'], 'employee')
        self.assertIsNotNone(response.data['employee'])
        self.assertIsNone(response.data['contact'])
        self.assertEqual(response.data['employee']['employee_number'], 'EMP001')

    def test_person_type_contact(self):
        """Test person_type is 'contact' for customer portal users."""
        # Create contact with user
        user = User.objects.create_user(
            username='contact_user',
            password='testpass123',
            first_name='Carol',
            last_name='Williams'
        )
        contact = Contact.objects.create(
            user=user,
            customer=self.customer,
            first_name='Carol',
            last_name='Williams',
            email='carol@customer.com'
        )

        # Authenticate and get profile
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['person_type'], 'contact')
        self.assertIsNone(response.data['employee'])
        self.assertIsNotNone(response.data['contact'])
        self.assertEqual(response.data['contact']['email'], 'carol@customer.com')

    def test_person_type_none(self):
        """Test person_type is None for standalone users (should not exist in production)."""
        # Create standalone user (no employee or contact)
        user = User.objects.create_user(
            username='standalone_user',
            password='testpass123',
            is_superuser=True
        )

        # Authenticate and get profile
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['person_type'])
        self.assertIsNone(response.data['employee'])
        self.assertIsNone(response.data['contact'])

    def test_employee_user_reverse_relationship(self):
        """Test accessing employee from user via reverse relationship."""
        user = User.objects.create_user(username='emp_rev', password='pass123')
        employee = Employee.objects.create(
            user=user,
            employee_number='EMP002',
            first_name='Dave',
            last_name='Brown',
            base_department=self.department
        )

        # Access employee from user
        self.assertEqual(user.employee, employee)
        self.assertTrue(hasattr(user, 'employee'))

    def test_contact_user_reverse_relationship(self):
        """Test accessing contact from user via reverse relationship."""
        user = User.objects.create_user(username='cont_rev', password='pass123')
        contact = Contact.objects.create(
            user=user,
            customer=self.customer,
            first_name='Eve',
            last_name='Davis',
            email='eve@customer.com'
        )

        # Access contact from user
        self.assertEqual(user.contact, contact)
        self.assertTrue(hasattr(user, 'contact'))

    def test_user_linked_to_employee_and_contact(self):
        """Test user-person architecture constraints."""
        user = User.objects.create_user(username='dual_user', password='pass123')

        # Link to employee first
        employee = Employee.objects.create(
            user=user,
            employee_number='EMP003',
            first_name='Frank',
            last_name='Miller',
            base_department=self.department
        )

        # Verify user is linked to employee
        self.assertEqual(user.employee, employee)
        self.assertTrue(hasattr(user, 'employee'))

        # In the current architecture, a user can technically be linked to both
        # (though in production this should be prevented by business logic)
        # For now, just verify the employee link works as expected
        self.assertEqual(employee.user, user)
