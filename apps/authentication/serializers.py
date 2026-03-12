"""
Authentication serializers.

Handles serialization for:
- User authentication (login, register)
- User profile with permissions
- Password management
"""
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.organization.models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    """Minimal employee info for user profile."""
    full_name = serializers.CharField(read_only=True)
    department = serializers.CharField(source='base_department.name', read_only=True)
    department_code = serializers.CharField(source='base_department.code', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'employee_number',
            'full_name',
            'first_name',
            'last_name',
            'email',
            'phone',
            'department',
            'department_code',
            'title',
            'is_active',
        ]


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer without permissions (for lists)."""
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'employee',
        ]
        read_only_fields = ['id', 'is_staff']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Full user profile with permissions and roles.

    Used for /api/auth/me/ endpoint to provide complete user context
    including all permissions for frontend authorization.
    """
    employee = EmployeeSerializer(read_only=True)
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'employee',
            'roles',
            'permissions',
            'last_login',
            'date_joined',
        ]
        read_only_fields = ['id', 'is_staff', 'is_superuser', 'last_login', 'date_joined']

    def get_roles(self, obj):
        """Get user's role names (from groups)."""
        return list(obj.groups.values_list('name', flat=True))

    def get_permissions(self, obj):
        """
        Get all user permissions.

        Returns both:
        - Django model permissions (from groups + user_permissions)
        - Custom business logic permissions
        """
        # Get all Django permissions
        perms = set(obj.get_all_permissions())

        # Add custom business logic permissions based on employee context
        if hasattr(obj, 'employee') and obj.employee:
            employee = obj.employee

            # All authenticated users can view own profile
            perms.add('authentication.view_own_profile')

            # Inspectors get special permissions
            if obj.groups.filter(name='INSPECTOR').exists():
                perms.add('inspections.perform_inspection')
                perms.add('inspections.view_own_inspections')
                perms.add('inspections.edit_own_inspections')

            # Department-based permissions
            if employee.base_department.code == 'INSP':
                perms.add('inspections.view_department_inspections')

            # Super admins get wildcard
            if obj.is_superuser or obj.groups.filter(name='SUPER_ADMIN').exists():
                perms.add('*')

        return sorted(list(perms))


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user profile in response.

    Returns:
    - access: JWT access token
    - refresh: JWT refresh token
    - user: Full user profile with permissions
    """

    def validate(self, attrs):
        """Add user profile to token response."""
        data = super().validate(attrs)

        # Add user profile with permissions
        user_serializer = UserProfileSerializer(self.user)
        data['user'] = user_serializer.data

        return data


class RegisterSerializer(serializers.ModelSerializer):
    """
    User registration serializer.

    Creates new user account with password validation.
    Admin-only endpoint for creating employee accounts.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    employee_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="Link to existing employee record"
    )
    roles = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        help_text="List of role names to assign"
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'password_confirm',
            'employee_id',
            'roles',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        """Validate password confirmation and employee."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })

        # Validate employee exists if provided
        if 'employee_id' in attrs and attrs['employee_id']:
            try:
                employee = Employee.objects.get(id=attrs['employee_id'])
                if employee.user:
                    raise serializers.ValidationError({
                        'employee_id': 'This employee already has a user account.'
                    })
                attrs['employee'] = employee
            except Employee.DoesNotExist:
                raise serializers.ValidationError({
                    'employee_id': 'Employee not found.'
                })

        return attrs

    def validate_roles(self, value):
        """Validate that all role names exist."""
        if value:
            existing_roles = set(Group.objects.filter(name__in=value).values_list('name', flat=True))
            invalid_roles = set(value) - existing_roles
            if invalid_roles:
                raise serializers.ValidationError(
                    f"Invalid roles: {', '.join(invalid_roles)}"
                )
        return value

    def create(self, validated_data):
        """Create user with hashed password and link to employee."""
        # Remove non-user fields
        validated_data.pop('password_confirm')
        employee = validated_data.pop('employee', None)
        roles = validated_data.pop('roles', [])
        validated_data.pop('employee_id', None)

        # Create user
        user = User.objects.create_user(**validated_data)

        # Link to employee if provided
        if employee:
            employee.user = user
            employee.save()

        # Assign roles
        if roles:
            groups = Group.objects.filter(name__in=roles)
            user.groups.set(groups)

        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Change password serializer.

    Requires current password for verification.
    """
    current_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match.'
            })
        return attrs

    def validate_current_password(self, value):
        """Verify current password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value
