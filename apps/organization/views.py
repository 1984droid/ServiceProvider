"""API views for organization models."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Company, Department, Employee
from .serializers import (
    CompanySerializer,
    DepartmentSerializer,
    EmployeeSerializer,
    EmployeeMinimalSerializer
)


class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Company.

    Single-tenant: Only one company record should exist.
    """
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
    """API endpoint for Departments."""
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
    """API endpoint for Employees."""
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
