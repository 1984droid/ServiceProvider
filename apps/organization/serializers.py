"""API serializers for organization models."""
from rest_framework import serializers
from .models import Company, Department, Employee


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model."""

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'dba_name', 'phone', 'email', 'website',
            'address_line1', 'address_line2', 'city', 'state', 'zip_code',
            'tax_id', 'usdot_number', 'logo', 'settings',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model."""
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    employee_count = serializers.IntegerField(read_only=True)
    total_employee_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'description', 'manager', 'manager_name',
            'is_active', 'allows_floating', 'employee_count', 'total_employee_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model."""
    full_name = serializers.CharField(read_only=True)
    base_department_name = serializers.CharField(source='base_department.name', read_only=True)
    floating_department_names = serializers.SerializerMethodField()
    all_departments = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'employee_number', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'base_department', 'base_department_name',
            'floating_departments', 'floating_department_names', 'all_departments',
            'title', 'hire_date', 'termination_date', 'is_active',
            'certifications', 'skills', 'settings',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'created_at', 'updated_at']

    def get_floating_department_names(self, obj):
        """Get names of floating departments."""
        return [dept.name for dept in obj.floating_departments.all()]

    def get_all_departments(self, obj):
        """Get all departments (base + floating)."""
        return [
            {'id': str(dept.id), 'name': dept.name, 'code': dept.code}
            for dept in obj.all_departments
        ]


class EmployeeMinimalSerializer(serializers.ModelSerializer):
    """Minimal employee serializer for nested representations."""
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'employee_number', 'full_name', 'title']
        read_only_fields = ['id', 'full_name']
