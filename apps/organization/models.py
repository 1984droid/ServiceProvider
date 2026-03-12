"""
Organization models for company, departments, and employees.

Models:
- Company: Single-tenant company information
- Department: Organizational departments
- Employee: Staff members with department assignments
"""
import uuid
from django.db import models
from django.core.exceptions import ValidationError


class BaseModel(models.Model):
    """Abstract base model with UUID primary key and timestamps."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Company(BaseModel):
    """
    Company/Organization information.

    Single-tenant: Only one company record should exist.
    Contains all company-wide settings and information.
    """
    name = models.CharField(
        max_length=255,
        help_text="Legal company name"
    )
    dba_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Doing Business As name"
    )

    # Contact Information
    phone = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    website = models.URLField(blank=True, default='')

    # Address
    address_line1 = models.CharField(max_length=255, blank=True, default='')
    address_line2 = models.CharField(max_length=255, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=2, blank=True, default='')
    zip_code = models.CharField(max_length=20, blank=True, default='')

    # Business Details
    tax_id = models.CharField(
        max_length=20,
        blank=True,
        default='',
        help_text="EIN or Tax ID"
    )
    usdot_number = models.CharField(
        max_length=20,
        blank=True,
        default='',
        help_text="USDOT number if applicable"
    )

    # Settings
    logo = models.ImageField(
        upload_to='company/logos/',
        null=True,
        blank=True,
        help_text="Company logo"
    )
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Company-wide settings and preferences"
    )

    class Meta:
        db_table = 'company'
        verbose_name = 'Company'
        verbose_name_plural = 'Company'  # Only one company

    def __str__(self):
        return self.dba_name or self.name

    def clean(self):
        """Validate company - enforce single-tenant."""
        super().clean()
        if not self.pk and Company.objects.exists():
            raise ValidationError("Only one company record is allowed. Please update the existing company.")

    def save(self, *args, **kwargs):
        """Enforce single-tenant: only one company allowed."""
        # Skip validation if explicitly disabled
        if not kwargs.pop('skip_validation', False):
            self.full_clean()
        super().save(*args, **kwargs)


class Department(BaseModel):
    """
    Organizational department.

    Departments organize employees and can be assigned to work orders.
    Examples: Service, Inspection, Parts, Administration
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Department name"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Short department code (e.g., 'SRV', 'INSP')"
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text="Department description and responsibilities"
    )

    # Department Head
    manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        help_text="Department manager/supervisor"
    )

    # Settings
    is_active = models.BooleanField(
        default=True,
        help_text="Whether department is currently active"
    )
    allows_floating = models.BooleanField(
        default=True,
        help_text="Whether employees from other departments can float to this department"
    )

    class Meta:
        db_table = 'departments'
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def employee_count(self):
        """Get count of employees with this as base department."""
        return self.base_employees.filter(is_active=True).count()

    @property
    def total_employee_count(self):
        """Get count including floating employees."""
        return self.base_employees.filter(is_active=True).count() + \
               self.floating_employees.filter(is_active=True).count()


class Employee(BaseModel):
    """
    Company employee.

    Employees belong to a base department and can float to other departments.
    Linked to Django User for authentication.
    """
    # Django User Link (optional - not all employees need login access)
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee',
        help_text="Django user account (if employee has system access)"
    )

    # Basic Information
    employee_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique employee number/ID"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')

    # Department Assignments
    base_department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='base_employees',
        help_text="Primary/home department"
    )
    floating_departments = models.ManyToManyField(
        Department,
        blank=True,
        related_name='floating_employees',
        help_text="Additional departments employee can work in"
    )

    # Employment Details
    title = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Job title"
    )
    hire_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of hire"
    )
    termination_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of termination (if applicable)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether employee is currently active"
    )

    # Certifications and Skills
    certifications = models.JSONField(
        default=list,
        blank=True,
        help_text="List of certifications (e.g., ASE, CDL)"
    )
    skills = models.JSONField(
        default=list,
        blank=True,
        help_text="List of skills and specializations"
    )

    # Settings
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Employee preferences and settings"
    )

    class Meta:
        db_table = 'employees'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['base_department', 'is_active']),
            models.Index(fields=['employee_number']),
        ]
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

    def __str__(self):
        return f"{self.employee_number} - {self.full_name}"

    @property
    def full_name(self):
        """Get employee's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def all_departments(self):
        """Get list of all departments (base + floating)."""
        departments = [self.base_department]
        departments.extend(self.floating_departments.all())
        return departments

    def can_work_in_department(self, department):
        """Check if employee can work in given department."""
        if self.base_department == department:
            return True
        return self.floating_departments.filter(id=department.id).exists()

    def clean(self):
        """Validate employee data."""
        super().clean()
        errors = {}

        # Can't have termination date before hire date
        if self.hire_date and self.termination_date:
            if self.termination_date < self.hire_date:
                errors['termination_date'] = 'Termination date cannot be before hire date'

        # If terminated, should not be active
        if self.termination_date and self.is_active:
            errors['is_active'] = 'Terminated employees must be marked as inactive'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Override save to call full_clean() first."""
        self.full_clean()
        super().save(*args, **kwargs)
