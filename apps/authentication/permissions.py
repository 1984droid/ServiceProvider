"""
Custom permission classes for fine-grained access control.

Provides:
- Role-based permissions (inspector, admin, etc.)
- Object-level permissions (own resources, department resources)
- Business logic permissions (finalized inspections, etc.)
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class HasPermission(BasePermission):
    """
    Check if user has a specific Django permission.

    Usage in view:
        permission_classes = [HasPermission]
        required_permission = 'inspections.view_inspectionrun'
    """

    def has_permission(self, request, view):
        """Check model-level permission."""
        required_perm = getattr(view, 'required_permission', None)
        if not required_perm:
            return True
        return request.user.has_perm(required_perm)


class IsInspector(BasePermission):
    """User must have Inspector role."""

    def has_permission(self, request, view):
        """Check if user is in INSPECTOR group."""
        return request.user.groups.filter(name='INSPECTOR').exists()


class IsAdmin(BasePermission):
    """User must have Admin or Super Admin role."""

    def has_permission(self, request, view):
        """Check if user is in ADMIN or SUPER_ADMIN group."""
        return (
            request.user.is_superuser or
            request.user.groups.filter(name__in=['ADMIN', 'SUPER_ADMIN']).exists()
        )


class CanEditOwnInspection(BasePermission):
    """
    Can edit inspection if user created it or is admin.

    Object-level permission for inspections.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user can edit this inspection."""
        # Read-only permissions are always allowed
        if request.method in SAFE_METHODS:
            return True

        # Admins can edit anything
        if request.user.is_superuser or request.user.groups.filter(name__in=['ADMIN', 'SUPER_ADMIN']).exists():
            return True

        # Must be the inspector who created it
        if hasattr(request.user, 'employee') and request.user.employee:
            employee = request.user.employee
            return obj.inspector_name == employee.full_name

        return False


class CannotEditFinalizedInspection(BasePermission):
    """
    Cannot edit finalized inspections unless Super Admin.

    Business logic permission to prevent tampering with completed inspections.
    """

    def has_object_permission(self, request, view, obj):
        """Check if inspection can be edited based on status."""
        # Read-only permissions are always allowed
        if request.method in SAFE_METHODS:
            return True

        # If inspection is finalized/completed
        if obj.status == 'COMPLETED':
            # Only super admins can reopen/edit
            return request.user.is_superuser or request.user.groups.filter(name='SUPER_ADMIN').exists()

        return True


class CanViewDepartmentWorkOrders(BasePermission):
    """
    Can view work orders assigned to user's department.

    Used to filter work orders by department access.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user can view this work order."""
        # Admins can view all
        if request.user.is_superuser or request.user.groups.filter(name__in=['ADMIN', 'SUPER_ADMIN']).exists():
            return True

        # Must have employee record
        if not hasattr(request.user, 'employee') or not request.user.employee:
            return False

        employee = request.user.employee

        # Check if work order is assigned to user's department
        if hasattr(obj, 'assigned_department'):
            return employee.can_work_in_department(obj.assigned_department)

        # Check if user is assigned to the work order
        if hasattr(obj, 'assigned_to'):
            return obj.assigned_to == employee

        return False


class CanManageUsers(BasePermission):
    """
    Can create/edit/delete user accounts.

    Admin-only permission for user management.
    """

    def has_permission(self, request, view):
        """Check if user can manage other users."""
        return request.user.is_superuser or request.user.groups.filter(name__in=['ADMIN', 'SUPER_ADMIN']).exists()


class CanAssignRoles(BasePermission):
    """
    Can assign roles to users.

    Super Admin only - prevents privilege escalation.
    """

    def has_permission(self, request, view):
        """Check if user can assign roles."""
        # Only allow if trying to assign roles
        if 'roles' not in request.data:
            return True

        # Must be super admin to assign roles
        return request.user.is_superuser or request.user.groups.filter(name='SUPER_ADMIN').exists()


class ReadOnly(BasePermission):
    """
    Read-only permission.

    Useful for VIEWER role.
    """

    def has_permission(self, request, view):
        """Only allow safe methods."""
        return request.method in SAFE_METHODS


class IsOwnerOrAdmin(BasePermission):
    """
    Object is owned by user or user is admin.

    Generic object-level permission for resources with an 'owner' or 'created_by' field.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user owns object or is admin."""
        # Read-only permissions are always allowed
        if request.method in SAFE_METHODS:
            return True

        # Admins can do anything
        if request.user.is_superuser or request.user.groups.filter(name__in=['ADMIN', 'SUPER_ADMIN']).exists():
            return True

        # Check ownership
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user

        return False
