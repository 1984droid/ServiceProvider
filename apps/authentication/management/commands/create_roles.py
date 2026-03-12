"""
Management command to create roles and permissions.

Usage:
    python manage.py create_roles

Creates all role groups with appropriate permissions.
Safe to run multiple times - updates existing roles.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps


class Command(BaseCommand):
    help = 'Create user roles and assign permissions'

    ROLES = {
        'SUPER_ADMIN': {
            'name': 'Super Administrator',
            'permissions': '*',  # All permissions
        },
        'ADMIN': {
            'name': 'Administrator',
            'permissions': [
                # Customers
                'customers.view_customer',
                'customers.add_customer',
                'customers.change_customer',
                'customers.delete_customer',
                'customers.view_contact',
                'customers.add_contact',
                'customers.change_contact',
                'customers.delete_contact',
                # Assets
                'assets.view_vehicle',
                'assets.add_vehicle',
                'assets.change_vehicle',
                'assets.delete_vehicle',
                'assets.view_equipment',
                'assets.add_equipment',
                'assets.change_equipment',
                'assets.delete_equipment',
                # Inspections (view only)
                'inspections.view_inspectionrun',
                'inspections.view_inspectiondefect',
                # Work Orders
                'work_orders.view_workorder',
                'work_orders.add_workorder',
                'work_orders.change_workorder',
                'work_orders.delete_workorder',
                # Organization
                'organization.view_employee',
                'organization.add_employee',
                'organization.change_employee',
                'organization.delete_employee',
                'organization.view_department',
                'organization.add_department',
                'organization.change_department',
                'organization.delete_department',
                'organization.view_company',
                'organization.change_company',
            ]
        },
        'INSPECTOR': {
            'name': 'Inspector/Technician',
            'permissions': [
                # Inspections (full access)
                'inspections.view_inspectionrun',
                'inspections.add_inspectionrun',
                'inspections.change_inspectionrun',
                'inspections.view_inspectiondefect',
                'inspections.add_inspectiondefect',
                'inspections.change_inspectiondefect',
                'inspections.delete_inspectiondefect',
                # Customers (view only)
                'customers.view_customer',
                'customers.view_contact',
                # Assets (view only)
                'assets.view_vehicle',
                'assets.view_equipment',
                # Work Orders (view and update assigned)
                'work_orders.view_workorder',
                'work_orders.change_workorder',
            ]
        },
        'SERVICE_TECH': {
            'name': 'Service Technician',
            'permissions': [
                # Work Orders (full access)
                'work_orders.view_workorder',
                'work_orders.add_workorder',
                'work_orders.change_workorder',
                # Inspections (view only)
                'inspections.view_inspectionrun',
                'inspections.view_inspectiondefect',
                # Customers (view only)
                'customers.view_customer',
                'customers.view_contact',
                # Assets (view and update)
                'assets.view_vehicle',
                'assets.change_vehicle',
                'assets.view_equipment',
                'assets.change_equipment',
            ]
        },
        'DISPATCHER': {
            'name': 'Dispatcher',
            'permissions': [
                # Inspections (create and schedule)
                'inspections.view_inspectionrun',
                'inspections.add_inspectionrun',
                # Work Orders (create and schedule)
                'work_orders.view_workorder',
                'work_orders.add_workorder',
                'work_orders.change_workorder',
                # Customers (full access)
                'customers.view_customer',
                'customers.add_customer',
                'customers.change_customer',
                'customers.view_contact',
                'customers.add_contact',
                'customers.change_contact',
                # Assets (view only)
                'assets.view_vehicle',
                'assets.view_equipment',
                # Organization (view only)
                'organization.view_employee',
                'organization.view_department',
            ]
        },
        'CUSTOMER_SERVICE': {
            'name': 'Customer Service',
            'permissions': [
                # Customers (full access)
                'customers.view_customer',
                'customers.add_customer',
                'customers.change_customer',
                'customers.view_contact',
                'customers.add_contact',
                'customers.change_contact',
                'customers.delete_contact',
                # Inspections (view only)
                'inspections.view_inspectionrun',
                'inspections.view_inspectiondefect',
                # Work Orders (view only)
                'work_orders.view_workorder',
                # Assets (view only)
                'assets.view_vehicle',
                'assets.view_equipment',
            ]
        },
        'VIEWER': {
            'name': 'Read-Only Viewer',
            'permissions': [
                # View-only access to everything
                'customers.view_customer',
                'customers.view_contact',
                'assets.view_vehicle',
                'assets.view_equipment',
                'inspections.view_inspectionrun',
                'inspections.view_inspectiondefect',
                'work_orders.view_workorder',
                'organization.view_employee',
                'organization.view_department',
                'organization.view_company',
            ]
        },
    }

    def handle(self, *args, **options):
        """Create roles and assign permissions."""
        self.stdout.write(self.style.SUCCESS('Creating roles and permissions...\n'))

        for role_code, role_data in self.ROLES.items():
            self.stdout.write(f'Processing role: {role_code} ({role_data["name"]})')

            # Create or get group
            group, created = Group.objects.get_or_create(name=role_code)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created group: {role_code}'))
            else:
                self.stdout.write(f'  Group exists: {role_code}')

            # Clear existing permissions
            group.permissions.clear()

            # Assign permissions
            if role_data['permissions'] == '*':
                # Super admin gets all permissions
                all_permissions = Permission.objects.all()
                group.permissions.set(all_permissions)
                self.stdout.write(self.style.SUCCESS(f'  Assigned ALL permissions ({all_permissions.count()})'))
            else:
                # Assign specific permissions
                assigned_count = 0
                missing_permissions = []

                for perm_string in role_data['permissions']:
                    try:
                        app_label, codename = perm_string.split('.')
                        permission = Permission.objects.get(
                            content_type__app_label=app_label,
                            codename=codename
                        )
                        group.permissions.add(permission)
                        assigned_count += 1
                    except Permission.DoesNotExist:
                        missing_permissions.append(perm_string)
                    except ValueError:
                        self.stdout.write(
                            self.style.WARNING(f'  Invalid permission format: {perm_string}')
                        )

                self.stdout.write(self.style.SUCCESS(f'  Assigned {assigned_count} permissions'))

                if missing_permissions:
                    self.stdout.write(
                        self.style.WARNING(f'  Missing permissions: {", ".join(missing_permissions)}')
                    )

            self.stdout.write('')

        self.stdout.write(self.style.SUCCESS('\nRoles and permissions created successfully!'))
        self.stdout.write('\nAvailable roles:')
        for role_code, role_data in self.ROLES.items():
            self.stdout.write(f'  - {role_code}: {role_data["name"]}')
