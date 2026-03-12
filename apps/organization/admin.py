"""Admin interface for organization models."""
from django.contrib import admin
from .models import Company, Department, Employee


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin interface for Company model."""
    list_display = ['name', 'dba_name', 'phone', 'email', 'city', 'state']
    search_fields = ['name', 'dba_name', 'email']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'dba_name', 'logo')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'zip_code')
        }),
        ('Business Details', {
            'fields': ('tax_id', 'usdot_number')
        }),
        ('Settings', {
            'fields': ('settings',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['id', 'created_at', 'updated_at']

    def has_add_permission(self, request):
        """Only allow adding if no company exists."""
        return not Company.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of company."""
        return False


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin interface for Department model."""
    list_display = ['code', 'name', 'manager', 'employee_count', 'is_active']
    list_filter = ['is_active', 'allows_floating']
    search_fields = ['name', 'code', 'description']
    ordering = ['code']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Management', {
            'fields': ('manager',)
        }),
        ('Settings', {
            'fields': ('is_active', 'allows_floating')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['id', 'created_at', 'updated_at']

    def employee_count(self, obj):
        """Display employee count."""
        return obj.employee_count
    employee_count.short_description = 'Employees'


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin interface for Employee model."""
    list_display = ['employee_number', 'full_name', 'title', 'base_department', 'is_active', 'hire_date']
    list_filter = ['is_active', 'base_department', 'hire_date']
    search_fields = ['employee_number', 'first_name', 'last_name', 'email']
    filter_horizontal = ['floating_departments']
    ordering = ['employee_number']
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee_number', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Department Assignments', {
            'fields': ('base_department', 'floating_departments')
        }),
        ('Employment Details', {
            'fields': ('title', 'hire_date', 'termination_date', 'is_active')
        }),
        ('System Access', {
            'fields': ('user',),
            'description': 'Link to Django user account for system login'
        }),
        ('Skills & Certifications', {
            'fields': ('certifications', 'skills'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('settings',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['id', 'created_at', 'updated_at']

    def full_name(self, obj):
        """Display full name."""
        return obj.full_name
    full_name.short_description = 'Name'
    full_name.admin_order_field = 'last_name'
