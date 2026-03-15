"""API views for organization models."""
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from .models import Company, Department, Employee
from .serializers import (
    CompanySerializer,
    DepartmentSerializer,
    EmployeeSerializer,
    EmployeeMinimalSerializer
)

User = get_user_model()


class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Company.

    Single-tenant: Only one company record should exist.

    Permissions:
    - Must be authenticated
    - Uses Django model permissions (view, add, change, delete)
    """
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the current company (should only be one)."""
        company = Company.objects.first()
        if company:
            serializer = self.get_serializer(company)
            return Response(serializer.data)
        return Response(
            {'detail': 'No company configured'},
            status=status.HTTP_404_NOT_FOUND
        )


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Departments.

    Permissions:
    - Must be authenticated
    - Uses Django model permissions (view, add, change, delete)
    """
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filterset_fields = ['is_active', 'allows_floating']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['code']

    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Get all employees in this department (base + floating)."""
        department = self.get_object()
        base_employees = department.base_employees.filter(is_active=True)
        floating_employees = department.floating_employees.filter(is_active=True)

        all_employees = list(base_employees) + list(floating_employees)
        serializer = EmployeeMinimalSerializer(all_employees, many=True)
        return Response(serializer.data)


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Employees.

    Permissions:
    - Must be authenticated
    - Uses Django model permissions (view, add, change, delete)
    """
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filterset_fields = ['is_active', 'base_department']
    search_fields = ['employee_number', 'first_name', 'last_name', 'email']
    ordering_fields = ['employee_number', 'last_name', 'hire_date']
    ordering = ['employee_number']

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active employees."""
        employees = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(employees, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current user's employee record with certifications."""
        try:
            employee = Employee.objects.get(user=request.user, is_active=True)
            serializer = self.get_serializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response(
                {'detail': 'No employee record found for current user'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def can_work_in(self, request, pk=None):
        """Check if employee can work in specified department."""
        employee = self.get_object()
        department_id = request.query_params.get('department_id')

        if not department_id:
            return Response(
                {'detail': 'department_id query parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            department = Department.objects.get(id=department_id)
            can_work = employee.can_work_in_department(department)
            return Response({'can_work': can_work, 'department': department.name})
        except Department.DoesNotExist:
            return Response(
                {'detail': 'Department not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def create_user(self, request, pk=None):
        """
        Create a user account for this employee.

        Request body:
            username (optional): If not provided, auto-generates from email or employee_number
            password (optional): If not provided, generates random password
            send_email (optional, default=True): Whether to send welcome email

        Returns user account info and temporary password if generated.
        """
        employee = self.get_object()

        # Check if employee already has a user
        if employee.user:
            return Response(
                {'error': 'Employee already has a user account'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or generate username
        username = request.data.get('username')
        if not username:
            # Auto-generate from email or employee number
            if employee.email:
                username = employee.email.split('@')[0]
            else:
                username = f"emp_{employee.employee_number}"

            # Ensure uniqueness
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': f'Username "{username}" already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or generate password
        password = request.data.get('password')
        password_generated = False
        if not password:
            # Generate random password
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(12))
            password_generated = True

        # Create user
        user = User.objects.create_user(
            username=username,
            email=employee.email or '',
            first_name=employee.first_name,
            last_name=employee.last_name,
            password=password
        )

        # Link employee to user
        employee.user = user
        employee.save()

        response_data = {
            'message': 'User account created successfully',
            'username': username,
            'employee_id': str(employee.id),
            'user_id': str(user.id),
        }

        # Include password in response if it was auto-generated
        if password_generated:
            response_data['temporary_password'] = password
            response_data['password_note'] = 'This password is shown only once. User should change it on first login.'

        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def revoke_user(self, request, pk=None):
        """
        Revoke user account access for this employee.

        This deactivates the user account but preserves the employee record.
        The user link is removed so a new account could be created later if needed.

        Request body:
            delete_user (optional, default=False): If true, deletes the user account entirely
        """
        employee = self.get_object()

        if not employee.user:
            return Response(
                {'error': 'Employee does not have a user account'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = employee.user
        delete_user = request.data.get('delete_user', False)

        if delete_user:
            # Completely delete the user account
            username = user.username
            employee.user = None
            employee.save()
            user.delete()

            return Response({
                'message': f'User account "{username}" has been deleted',
                'employee_id': str(employee.id),
            })
        else:
            # Just deactivate and unlink
            username = user.username
            user.is_active = False
            user.save()

            employee.user = None
            employee.save()

            return Response({
                'message': f'User account "{username}" has been deactivated and unlinked',
                'employee_id': str(employee.id),
                'note': 'User account still exists but is inactive. Can be reactivated if needed.'
            })
