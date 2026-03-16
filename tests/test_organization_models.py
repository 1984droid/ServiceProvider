"""
Tests for organization models (Company, Department, Employee).

All test data comes from tests.config - NO HARDCODED VALUES!
"""
import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth.models import User

from apps.organization.models import Company, Department, Employee
from tests.factories import CompanyFactory, DepartmentFactory, EmployeeFactory
from tests.config import get_test_data


@pytest.mark.django_db
class TestCompanyModel:
    """Tests for Company model."""

    def test_company_creation_default(self):
        """Test creating company with default data."""
        company = CompanyFactory()
        default_data = get_test_data('company', 'default')

        assert company.name == default_data['name']
        assert company.dba_name == default_data['dba_name']
        # Phone/email are on the primary contact, not company model
        assert str(company) == default_data['dba_name']

    def test_company_creation_minimal(self):
        """Test creating company with minimal fields."""
        company = CompanyFactory.minimal()
        minimal_data = get_test_data('company', 'minimal')

        assert company.name == minimal_data['name']
        assert str(company) == minimal_data['name']  # Falls back to name when no dba

    def test_company_str_uses_dba_name(self):
        """Test string representation uses DBA name."""
        company = CompanyFactory()
        assert str(company) == company.dba_name

    def test_company_str_falls_back_to_name(self):
        """Test string representation falls back to name when no DBA."""
        company = CompanyFactory(dba_name='')
        assert str(company) == company.name

    def test_company_name_required(self):
        """Test company name is required."""
        with pytest.raises(ValidationError):
            company = CompanyFactory(name='')
            company.full_clean()

    def test_company_settings_default_dict(self):
        """Test settings field defaults to empty dict."""
        company = CompanyFactory()
        assert isinstance(company.settings, dict)
        assert company.settings == {}


@pytest.mark.django_db
class TestDepartmentModel:
    """Tests for Department model."""

    def test_department_creation_default(self):
        """Test creating department with default data."""
        department = DepartmentFactory()
        default_data = get_test_data('department', 'default')

        # Name has sequence appended, so check it starts with the base name
        assert department.name.startswith(default_data['name'])
        assert department.description == default_data.get('description', '')
        assert department.is_active == default_data.get('is_active', True)
        assert department.allows_floating == default_data.get('allows_floating', True)

    def test_department_creation_variants(self):
        """Test creating department variants."""
        inspection = DepartmentFactory.inspection()
        parts = DepartmentFactory.parts()

        inspection_data = get_test_data('department', 'inspection')
        parts_data = get_test_data('department', 'parts')

        assert inspection.name == inspection_data['name']
        assert parts.name == parts_data['name']
        assert parts.allows_floating == False

    def test_department_str_representation(self):
        """Test string representation."""
        department = DepartmentFactory()
        assert str(department) == f"{department.code} - {department.name}"

    def test_department_name_unique(self):
        """Test department name must be unique."""
        dept1 = DepartmentFactory(name='Service')

        with pytest.raises(IntegrityError):
            DepartmentFactory(name='Service')

    def test_department_code_unique(self):
        """Test department code must be unique."""
        dept1 = DepartmentFactory(code='SRV')

        with pytest.raises(IntegrityError):
            DepartmentFactory(code='SRV')

    def test_department_employee_count(self):
        """Test employee_count property."""
        department = DepartmentFactory()

        # Create employees
        EmployeeFactory(base_department=department)
        EmployeeFactory(base_department=department)
        EmployeeFactory(base_department=department, is_active=False)  # Inactive

        assert department.employee_count == 2  # Only active

    def test_department_total_employee_count(self):
        """Test total_employee_count includes floating employees."""
        dept1 = DepartmentFactory()
        dept2 = DepartmentFactory()

        # Base employee
        emp1 = EmployeeFactory(base_department=dept1)

        # Floating employee from dept2
        emp2 = EmployeeFactory(base_department=dept2)
        emp2.floating_departments.add(dept1)

        assert dept1.employee_count == 1  # Base only
        assert dept1.total_employee_count == 2  # Base + floating

    def test_department_manager_relationship(self):
        """Test department can have manager."""
        department = DepartmentFactory()
        manager = EmployeeFactory(base_department=department)

        department.manager = manager
        department.save()

        assert department.manager == manager
        assert manager.managed_departments.first() == department


@pytest.mark.django_db
class TestEmployeeModel:
    """Tests for Employee model."""

    def test_employee_creation_default(self):
        """Test creating employee with default data."""
        employee = EmployeeFactory()
        default_data = get_test_data('employee', 'default')

        assert employee.first_name == default_data['first_name']
        assert employee.last_name == default_data['last_name']
        assert employee.email == default_data['email']
        assert employee.title == default_data['title']
        assert employee.is_active == default_data['is_active']

    def test_employee_creation_variants(self):
        """Test creating employee variants."""
        inspector = EmployeeFactory.inspector()
        inspector_data = get_test_data('employee', 'inspector')

        assert inspector.first_name == inspector_data['first_name']
        assert inspector.title == inspector_data['title']

    def test_employee_str_representation(self):
        """Test string representation."""
        employee = EmployeeFactory()
        expected = f"{employee.employee_number} - {employee.full_name}"
        assert str(employee) == expected

    def test_employee_full_name_property(self):
        """Test full_name property."""
        employee = EmployeeFactory()
        assert employee.full_name == f"{employee.first_name} {employee.last_name}"

    def test_employee_number_unique(self):
        """Test employee_number must be unique."""
        emp1 = EmployeeFactory(employee_number='E001')

        with pytest.raises(ValidationError):
            EmployeeFactory(employee_number='E001')

    def test_employee_base_department_required(self):
        """Test base_department is required."""
        with pytest.raises(ValidationError):
            Employee.objects.create(
                employee_number='E999',
                first_name='Test',
                last_name='User',
                base_department=None
            )

    def test_employee_floating_departments(self):
        """Test employee can have multiple floating departments."""
        dept1 = DepartmentFactory()
        dept2 = DepartmentFactory()
        dept3 = DepartmentFactory()

        employee = EmployeeFactory(base_department=dept1)
        employee.floating_departments.add(dept2, dept3)

        assert employee.floating_departments.count() == 2
        assert dept2 in employee.floating_departments.all()
        assert dept3 in employee.floating_departments.all()

    def test_employee_all_departments_property(self):
        """Test all_departments property includes base and floating."""
        dept1 = DepartmentFactory()
        dept2 = DepartmentFactory()
        dept3 = DepartmentFactory()

        employee = EmployeeFactory(base_department=dept1)
        employee.floating_departments.add(dept2, dept3)

        all_depts = employee.all_departments
        assert len(all_depts) == 3
        assert dept1 in all_depts
        assert dept2 in all_depts
        assert dept3 in all_depts

    def test_employee_can_work_in_department_base(self):
        """Test employee can work in their base department."""
        department = DepartmentFactory()
        employee = EmployeeFactory(base_department=department)

        assert employee.can_work_in_department(department) is True

    def test_employee_can_work_in_department_floating(self):
        """Test employee can work in floating departments."""
        dept1 = DepartmentFactory()
        dept2 = DepartmentFactory()

        employee = EmployeeFactory(base_department=dept1)
        employee.floating_departments.add(dept2)

        assert employee.can_work_in_department(dept2) is True

    def test_employee_cannot_work_in_department_not_assigned(self):
        """Test employee cannot work in unassigned departments."""
        dept1 = DepartmentFactory()
        dept2 = DepartmentFactory()

        employee = EmployeeFactory(base_department=dept1)

        assert employee.can_work_in_department(dept2) is False

    def test_employee_termination_date_validation(self):
        """Test termination_date cannot be before hire_date."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        with pytest.raises(ValidationError) as exc_info:
            EmployeeFactory(
                hire_date=today,
                termination_date=yesterday
            )

        assert 'termination_date' in str(exc_info.value)

    def test_employee_terminated_must_be_inactive(self):
        """Test terminated employees must be marked inactive."""
        with pytest.raises(ValidationError) as exc_info:
            EmployeeFactory(
                termination_date=date.today(),
                is_active=True
            )

        assert 'is_active' in str(exc_info.value)

    def test_employee_user_relationship(self):
        """Test employee can be linked to Django user."""
        user = User.objects.create_user('testuser', 'test@example.com', 'password')
        employee = EmployeeFactory(user=user)

        assert employee.user == user
        assert user.employee == employee

    def test_employee_certifications_json(self):
        """Test certifications stored as JSON list."""
        employee = EmployeeFactory()
        default_data = get_test_data('employee', 'default')

        assert isinstance(employee.certifications, list)
        assert employee.certifications == default_data['certifications']

    def test_employee_skills_json(self):
        """Test skills stored as JSON list."""
        employee = EmployeeFactory()
        default_data = get_test_data('employee', 'default')

        assert isinstance(employee.skills, list)
        assert employee.skills == default_data['skills']


@pytest.mark.django_db
class TestOrganizationIntegration:
    """Integration tests for organization models."""

    def test_department_hierarchy(self):
        """Test complete department hierarchy with manager."""
        dept = DepartmentFactory()
        manager = EmployeeFactory(base_department=dept, title='Manager')
        tech1 = EmployeeFactory(base_department=dept)
        tech2 = EmployeeFactory(base_department=dept)

        dept.manager = manager
        dept.save()

        assert dept.manager == manager
        assert dept.employee_count == 3

    def test_employee_department_transfer(self):
        """Test employee can be transferred between departments."""
        dept1 = DepartmentFactory()
        dept2 = DepartmentFactory()

        employee = EmployeeFactory(base_department=dept1)
        assert dept1.employee_count == 1
        assert dept2.employee_count == 0

        # Transfer
        employee.base_department = dept2
        employee.save()

        assert dept1.employee_count == 0
        assert dept2.employee_count == 1

    def test_multi_department_employee(self):
        """Test employee working in multiple departments."""
        service = DepartmentFactory()
        inspection = DepartmentFactory()
        parts = DepartmentFactory()

        # Employee based in service but can float to inspection
        employee = EmployeeFactory(base_department=service)
        employee.floating_departments.add(inspection)

        assert employee.can_work_in_department(service) is True
        assert employee.can_work_in_department(inspection) is True
        assert employee.can_work_in_department(parts) is False

        assert service.total_employee_count == 1
        assert inspection.total_employee_count == 1
        assert parts.total_employee_count == 0
