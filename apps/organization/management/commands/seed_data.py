"""
Django management command to seed realistic test data.

Usage:
    python manage.py seed_data [--clear]

Options:
    --clear    Clear existing data before seeding (WARNING: Destructive!)
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction
from apps.customers.models import Customer, Contact
from apps.assets.models import Vehicle, Equipment
from apps.organization.models import Company, Department, Employee
from apps.inspections.models import InspectionRun
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Seed database with realistic test data for frontend development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding (WARNING: Destructive!)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self._clear_data()

        self.stdout.write(self.style.SUCCESS('Starting data seed...'))

        # Create data in order of dependencies
        company = self._create_company()
        departments = self._create_departments(company)
        employees = self._create_employees(departments)
        users = self._create_users(employees)
        customers = self._create_customers()
        self._create_contacts(customers)
        vehicles = self._create_vehicles(customers)
        equipment = self._create_equipment(customers)

        self.stdout.write(self.style.SUCCESS('[OK] Data seed completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'  - Company: 1'))
        self.stdout.write(self.style.SUCCESS(f'  - Departments: {len(departments)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Employees: {len(employees)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Users: {len(users)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Customers: {len(customers)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Vehicles: {len(vehicles)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Equipment: {len(equipment)}'))

    def _clear_data(self):
        """Clear all seeded data (except superuser)."""
        InspectionRun.objects.all().delete()
        Equipment.objects.all().delete()
        Vehicle.objects.all().delete()
        Contact.objects.all().delete()
        Customer.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Employee.objects.all().delete()
        Department.objects.all().delete()
        Company.objects.all().delete()
        self.stdout.write(self.style.WARNING('[OK] Existing data cleared'))

    def _create_company(self):
        """Create the single company record."""
        company, created = Company.objects.get_or_create(
            name='Acme Inspection Services',
            defaults={
                'dba_name': 'Acme Inspections',
                'address_line1': '123 Main Street',
                'city': 'Springfield',
                'state': 'IL',
                'zip_code': '62701',
            }
        )
        if created:
            self.stdout.write('  [OK] Created company')
        return company

    def _create_departments(self, company):
        """Create departments."""
        departments_data = [
            {'name': 'Inspections', 'code': 'INSP', 'allows_floating': False},
            {'name': 'Service & Repair', 'code': 'SVCRPR', 'allows_floating': True},
            {'name': 'Customer Service', 'code': 'CUSTSVC', 'allows_floating': False},
            {'name': 'Administration', 'code': 'ADMIN', 'allows_floating': False},
        ]

        departments = []
        for data in departments_data:
            dept, created = Department.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            departments.append(dept)
            if created:
                self.stdout.write(f'  [OK] Created department: {dept.name}')

        return departments

    def _create_employees(self, departments):
        """Create employees across departments."""
        employees_data = [
            # Inspections
            {'first_name': 'John', 'last_name': 'Inspector', 'employee_number': 'EMP001', 'dept': 0},
            {'first_name': 'Jane', 'last_name': 'Technician', 'employee_number': 'EMP002', 'dept': 0},
            # Service & Repair
            {'first_name': 'Bob', 'last_name': 'Mechanic', 'employee_number': 'EMP003', 'dept': 1},
            {'first_name': 'Alice', 'last_name': 'ServiceTech', 'employee_number': 'EMP004', 'dept': 1},
            # Customer Service
            {'first_name': 'Carol', 'last_name': 'Support', 'employee_number': 'EMP005', 'dept': 2},
            # Administration
            {'first_name': 'David', 'last_name': 'Admin', 'employee_number': 'EMP006', 'dept': 3},
        ]

        employees = []
        for data in employees_data:
            dept_index = data.pop('dept')
            emp, created = Employee.objects.get_or_create(
                employee_number=data['employee_number'],
                defaults={
                    **data,
                    'base_department': departments[dept_index],
                    'hire_date': datetime.now().date() - timedelta(days=random.randint(30, 1000)),
                }
            )
            employees.append(emp)
            if created:
                self.stdout.write(f'  [OK] Created employee: {emp.full_name}')

        return employees

    def _create_users(self, employees):
        """Create users linked to employees with different roles."""
        users_data = [
            {'username': 'admin', 'role': 'ADMIN', 'emp_index': 5},  # David Admin
            {'username': 'inspector1', 'role': 'INSPECTOR', 'emp_index': 0},  # John Inspector
            {'username': 'inspector2', 'role': 'INSPECTOR', 'emp_index': 1},  # Jane Technician
            {'username': 'service1', 'role': 'SERVICE_TECH', 'emp_index': 2},  # Bob Mechanic
            {'username': 'service2', 'role': 'SERVICE_TECH', 'emp_index': 3},  # Alice ServiceTech
            {'username': 'support1', 'role': 'CUSTOMER_SERVICE', 'emp_index': 4},  # Carol Support
        ]

        users = []
        for data in users_data:
            emp = employees[data['emp_index']]
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': f"{data['username']}@acme.com",
                    'first_name': emp.first_name,
                    'last_name': emp.last_name,
                    'is_active': True,
                }
            )

            if created:
                # Set password (all users have 'admin' as password for testing)
                user.set_password('admin')
                user.save()

                # Assign role
                try:
                    role_group = Group.objects.get(name=data['role'])
                    user.groups.add(role_group)
                except Group.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'  ! Role {data["role"]} not found. Run create_roles first.'))

                # Link to employee
                emp.user = user
                emp.save()

                self.stdout.write(f'  [OK] Created user: {user.username} (role: {data["role"]})')

            users.append(user)

        return users

    def _create_customers(self):
        """Create customers."""
        customers_data = [
            {
                'name': 'ABC Transport Inc',
                'legal_name': 'ABC Transport Incorporated',
                'usdot_number': '1234567',
                'mc_number': 'MC123456',
                'address_line1': '456 Oak Avenue',
                'city': 'Chicago',
                'state': 'IL',
                'postal_code': '60601',
            },
            {
                'name': 'XYZ Logistics LLC',
                'legal_name': 'XYZ Logistics Limited Liability Company',
                'usdot_number': '7654321',
                'mc_number': 'MC654321',
                'address_line1': '789 Elm Street',
                'city': 'Aurora',
                'state': 'IL',
                'postal_code': '60505',
            },
            {
                'name': 'Quick Freight Co',
                'legal_name': 'Quick Freight Company',
                'address_line1': '321 Pine Road',
                'city': 'Naperville',
                'state': 'IL',
                'postal_code': '60540',
            },
        ]

        customers = []
        for data in customers_data:
            customer, created = Customer.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            customers.append(customer)
            if created:
                self.stdout.write(f'  [OK] Created customer: {customer.name}')

        return customers

    def _create_contacts(self, customers):
        """Create contacts for customers."""
        for customer in customers:
            # Primary contact
            contact1, created = Contact.objects.get_or_create(
                customer=customer,
                email=f'primary@{customer.name.lower().replace(" ", "")}.com',
                defaults={
                    'first_name': 'Primary',
                    'last_name': 'Contact',
                    'phone': '555-0100',
                }
            )
            if created:
                customer.primary_contact = contact1
                customer.save()
                self.stdout.write(f'    [OK] Created primary contact for {customer.name}')

            # Secondary contact
            Contact.objects.get_or_create(
                customer=customer,
                email=f'secondary@{customer.name.lower().replace(" ", "")}.com',
                defaults={
                    'first_name': 'Secondary',
                    'last_name': 'Contact',
                    'phone': '555-0101',
                }
            )

    def _create_vehicles(self, customers):
        """Create vehicles for customers."""
        vehicles = []
        for customer in customers:
            for i in range(2):  # 2 vehicles per customer
                vehicle, created = Vehicle.objects.get_or_create(
                    customer=customer,
                    unit_number=f'{customer.name[:3].upper()}-V{i+1:03d}',
                    defaults={
                        'vin': f'1HGBH41JXMN{random.randint(100000, 999999)}',
                        'year': random.randint(2015, 2024),
                        'make': random.choice(['Freightliner', 'Peterbilt', 'Kenworth', 'Volvo']),
                        'model': random.choice(['Cascadia', '579', 'T680', 'VNL']),
                        'license_plate': f'{random.choice(["IL", "IN", "WI"])}{random.randint(1000, 9999)}',
                    }
                )
                vehicles.append(vehicle)
                if created:
                    self.stdout.write(f'    [OK] Created vehicle: {vehicle.unit_number}')

        return vehicles

    def _create_equipment(self, customers):
        """Create equipment for customers (aerial devices only)."""
        equipment_list = []
        for customer in customers:
            for i in range(2):  # 2 aerial devices per customer
                equipment, created = Equipment.objects.get_or_create(
                    customer=customer,
                    asset_number=f'{customer.name[:3].upper()}-E{i+1:03d}',
                    defaults={
                        'equipment_type': 'AERIAL_DEVICE',
                        'manufacturer': random.choice(['Altec', 'Terex', 'Versalift']),
                        'model': random.choice(['AT40G', 'Hi-Ranger TL50', 'VST-240']),
                        'serial_number': f'SN{random.randint(100000, 999999)}',
                    }
                )
                equipment_list.append(equipment)
                if created:
                    self.stdout.write(f'    [OK] Created equipment: {equipment.asset_number}')

        return equipment_list
