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
from apps.customers.models import Customer, Contact, USDOTProfile
from apps.assets.models import Vehicle, Equipment
from apps.organization.models import Company, Department, Employee
from apps.inspections.models import InspectionRun
from datetime import datetime
import random
import secrets
import string
from .seed_config import SeedConfig


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
        self._create_usdot_profiles(customers)
        contacts = self._create_contacts(customers)
        contact_users = self._create_contact_users(contacts)
        vehicles = self._create_vehicles(customers)
        equipment = self._create_equipment(customers, vehicles)

        self.stdout.write(self.style.SUCCESS('[OK] Data seed completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'  - Company: 1'))
        self.stdout.write(self.style.SUCCESS(f'  - Departments: {len(departments)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Employees: {len(employees)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Employee Users: {len(users)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Customers: {len(customers)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Contacts: {len(contacts)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Contact Portal Users: {len(contact_users)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Vehicles: {len(vehicles)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Equipment: {len(equipment)}'))

    def _clear_data(self):
        """Clear all seeded data (except superuser)."""
        InspectionRun.objects.all().delete()
        Equipment.objects.all().delete()
        Vehicle.objects.all().delete()
        Contact.objects.all().delete()
        USDOTProfile.objects.all().delete()
        Customer.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Employee.objects.all().delete()
        Department.objects.all().delete()
        Company.objects.all().delete()
        self.stdout.write(self.style.WARNING('[OK] Existing data cleared'))

    def _create_company(self):
        """Create the single company record."""
        company, created = Company.objects.get_or_create(
            name=SeedConfig.COMPANY['name'],
            defaults=SeedConfig.COMPANY
        )
        if created:
            self.stdout.write('  [OK] Created company')
        return company

    def _create_departments(self, company):
        """Create departments from config."""
        departments = []
        for data in SeedConfig.DEPARTMENTS:
            dept, created = Department.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            departments.append(dept)
            if created:
                self.stdout.write(f'  [OK] Created department: {dept.name}')

        return departments

    def _create_employees(self, departments):
        """Create employees with certifications and skills from config."""
        # Build department lookup
        dept_lookup = {d.code: d for d in departments}

        employees = []
        for emp_data in SeedConfig.EMPLOYEES:
            dept = dept_lookup[emp_data['dept_code']]

            # Build certifications from config
            certifications = []
            for cert_key in emp_data.get('certifications', []):
                certs_for_standard = SeedConfig.CERTIFICATIONS.get(cert_key, [])
                for cert in certs_for_standard:
                    certifications.append({
                        'standard': cert['standard'],
                        'cert_number': cert['cert_number'],
                        'expiry_date': SeedConfig.get_cert_expiry_date(cert['expiry_months']).isoformat(),
                    })

            emp, created = Employee.objects.get_or_create(
                employee_number=emp_data['employee_number'],
                defaults={
                    'first_name': emp_data['first_name'],
                    'last_name': emp_data['last_name'],
                    'email': emp_data.get('email', ''),
                    'phone': emp_data.get('phone', ''),
                    'title': emp_data.get('title', ''),
                    'base_department': dept,
                    'hire_date': SeedConfig.get_random_hire_date(),
                    'certifications': certifications,
                    'skills': emp_data.get('skills', []),
                }
            )
            employees.append(emp)
            if created:
                cert_count = len(certifications)
                cert_info = f' ({cert_count} certs)' if cert_count > 0 else ''
                self.stdout.write(f'  [OK] Created employee: {emp.full_name}{cert_info}')

        return employees

    def _create_users(self, employees):
        """Create users linked to employees with different roles from config."""
        # Build employee lookup
        emp_lookup = {e.employee_number: e for e in employees}

        users = []
        for user_data in SeedConfig.USERS:
            emp = emp_lookup[user_data['emp_number']]
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': emp.email or f"{user_data['username']}@advantagefleet.com",
                    'first_name': emp.first_name,
                    'last_name': emp.last_name,
                    'is_active': True,
                }
            )

            if created:
                # Set password from config
                user.set_password(user_data['password'])
                user.save()

                # Assign role
                try:
                    role_group = Group.objects.get(name=user_data['role'])
                    user.groups.add(role_group)
                except Group.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'  ! Role {user_data["role"]} not found. Run create_roles first.'))

                # Link to employee
                emp.user = user
                emp.save()

                self.stdout.write(f'  [OK] Created user: {user.username} (role: {user_data["role"]})')

            users.append(user)

        return users

    def _create_customers(self):
        """Create customers from config."""
        customers = []
        for data in SeedConfig.CUSTOMERS:
            customer, created = Customer.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            customers.append(customer)
            if created:
                self.stdout.write(f'  [OK] Created customer: {customer.name}')

        return customers

    def _create_usdot_profiles(self, customers):
        """Create comprehensive USDOT profiles for customers that have USDOT numbers."""
        for customer in customers:
            if customer.usdot_number:
                profile, created = USDOTProfile.objects.get_or_create(
                    customer=customer,
                    defaults={
                        'usdot_number': customer.usdot_number,
                        'mc_number': customer.mc_number or '',
                        'legal_name': customer.legal_name or customer.name,
                        'dba_name': customer.name,
                        'entity_type': random.choice(SeedConfig.USDOT_CONFIG['entity_types']),
                        'physical_address': customer.address_line1,
                        'physical_city': customer.city,
                        'physical_state': customer.state,
                        'physical_zip': customer.postal_code,
                        'mailing_address': customer.address_line1,
                        'mailing_city': customer.city,
                        'mailing_state': customer.state,
                        'mailing_zip': customer.postal_code,
                        'phone': '555-0000',
                        'email': f'info@{SeedConfig.sanitize_for_domain(customer.name)}.com',
                        'carrier_operation': random.choice(SeedConfig.USDOT_CONFIG['carrier_operations']),
                        'cargo_carried': random.choice(SeedConfig.USDOT_CONFIG['cargo_types']),
                        'operation_classification': random.choice(SeedConfig.USDOT_CONFIG['operation_classifications']),
                        'safety_rating': random.choice(SeedConfig.USDOT_CONFIG['safety_ratings']),
                        'out_of_service_date': None,
                        'total_power_units': random.randint(*SeedConfig.USDOT_CONFIG['power_units_range']),
                        'total_drivers': random.randint(*SeedConfig.USDOT_CONFIG['drivers_range']),
                        'raw_fmcsa_data': {},
                    }
                )
                if created:
                    self.stdout.write(f'    [OK] Created USDOT profile for {customer.name}')

    def _create_contacts(self, customers):
        """Create diverse contacts for customers with varied correspondence preferences from config."""
        all_contacts = []
        for customer in customers:
            # Create 3-4 regular contacts per customer
            num_contacts = random.randint(3, 4)
            templates_to_use = random.sample(SeedConfig.CONTACT_TEMPLATES, num_contacts)

            for idx, template in enumerate(templates_to_use):
                first_name = random.choice(template['first_names'])
                last_name = random.choice(template['last_names'])
                email = f'{first_name.lower()}.{last_name.lower()}@{SeedConfig.sanitize_for_domain(customer.name)}.com'

                contact, created = Contact.objects.get_or_create(
                    customer=customer,
                    email=email,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'title': template['role'],
                        'phone': f'{random.randint(200, 999)}-555-{random.randint(1000, 9999)}',
                        'phone_extension': str(random.randint(100, 999)) if random.random() > 0.5 else '',
                        'mobile': f'{random.randint(200, 999)}-555-{random.randint(1000, 9999)}' if template['is_primary_template'] else '',
                        'is_active': True,
                        'is_automated': False,
                        'receive_invoices': template['receive_invoices'],
                        'receive_estimates': template['receive_estimates'],
                        'receive_service_updates': template['receive_service_updates'],
                        'receive_inspection_reports': template['receive_inspection_reports'],
                        'notes': f'Primary contact for {template["role"].lower()} matters.' if template['is_primary_template'] else '',
                    }
                )
                all_contacts.append(contact)

                if created:
                    # Set first contact as primary for customer
                    if template['is_primary_template']:
                        customer.primary_contact = contact
                        customer.save()
                        self.stdout.write(f'    [OK] Created primary contact: {contact.full_name} for {customer.name}')
                    else:
                        self.stdout.write(f'    [OK] Created contact: {contact.full_name} ({template["role"]}) for {customer.name}')

            # 50% chance to add automated system contact
            if random.random() > 0.5:
                auto_email = f'alerts@{SeedConfig.sanitize_for_domain(customer.name)}.com'
                # Filter out has_portal_access since it's not a Contact field
                auto_defaults = {k: v for k, v in SeedConfig.AUTOMATED_CONTACT.items() if k != 'has_portal_access'}
                auto_contact, created = Contact.objects.get_or_create(
                    customer=customer,
                    email=auto_email,
                    defaults=auto_defaults
                )
                all_contacts.append(auto_contact)
                if created:
                    self.stdout.write(f'    [OK] Created automated contact for {customer.name}')

        return all_contacts

    def _create_contact_users(self, contacts):
        """Create portal user accounts for contacts based on config."""
        contact_users = []

        for contact in contacts:
            # Skip automated contacts
            if contact.is_automated:
                continue

            # Find template to check if should have portal access
            has_portal_access = False
            for template in SeedConfig.CONTACT_TEMPLATES:
                if contact.title == template['role']:
                    has_portal_access = template.get('has_portal_access', False)
                    break

            if not has_portal_access:
                continue

            # Generate username from email
            username = contact.email.split('@')[0] if contact.email else f"{contact.first_name.lower()}{contact.last_name.lower()}"

            # Ensure uniqueness
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Generate temporary password
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(12))

            # Create user and link to contact
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': contact.email or '',
                    'first_name': contact.first_name,
                    'last_name': contact.last_name,
                    'is_active': True,
                }
            )

            if created:
                user.set_password(password)
                user.save()

                contact.user = user
                contact.save(update_fields=['user', 'updated_at'])

                contact_users.append(user)
                self.stdout.write(f'    [OK] Created portal user: {username} for {contact.full_name}')

        return contact_users

    def _create_vehicles(self, customers):
        """Create vehicles with comprehensive data from config."""
        vehicles = []
        for customer in customers:
            # Get count range from config
            num_vehicles = random.randint(
                SeedConfig.VEHICLE_CONFIG['min_per_customer'],
                SeedConfig.VEHICLE_CONFIG['max_per_customer']
            )

            for i in range(num_vehicles):
                make = random.choice(list(SeedConfig.VEHICLE_CONFIG['makes_models'].keys()))
                model = random.choice(SeedConfig.VEHICLE_CONFIG['makes_models'][make])
                year = random.randint(*SeedConfig.VEHICLE_CONFIG['year_range'])
                body_type = random.choice(SeedConfig.VEHICLE_CONFIG['body_types'])

                vehicle, created = Vehicle.objects.get_or_create(
                    customer=customer,
                    unit_number=f'{customer.name[:3].upper()}-{i+1:03d}',
                    defaults={
                        'vin': f'1HGBH41JXMN{random.randint(100000, 999999)}',
                        'year': year,
                        'make': make,
                        'model': model,
                        'body_type': body_type,
                        'license_plate': f'{random.choice(SeedConfig.VEHICLE_CONFIG["states"])}{random.choice(["T", "K", "F"])}{random.randint(10000, 99999)}',
                        'odometer_miles': random.randint(50000, 450000),
                        'engine_hours': random.randint(2000, 15000),
                        'is_active': random.random() < SeedConfig.VEHICLE_CONFIG['active_rate'],
                        'notes': f'{year} {make} {model}. Regular maintenance schedule.' if random.random() > 0.7 else '',
                    }
                )
                vehicles.append(vehicle)
                if created:
                    self.stdout.write(f'    [OK] Created vehicle: {vehicle.unit_number} ({year} {make} {model})')

        return vehicles

    def _create_equipment(self, customers, vehicles):
        """Create equipment with comprehensive data from config, some mounted on vehicles."""
        equipment_list = []
        for customer in customers:
            # Get customer's vehicles for potential mounting
            customer_vehicles = [v for v in vehicles if v.customer == customer]

            # Get count range from config
            num_equipment = random.randint(
                SeedConfig.EQUIPMENT_CONFIG['min_per_customer'],
                SeedConfig.EQUIPMENT_CONFIG['max_per_customer']
            )

            for i in range(num_equipment):
                equip_type = random.choice(list(SeedConfig.EQUIPMENT_CONFIG['types'].keys()))
                manufacturer = random.choice(SeedConfig.EQUIPMENT_CONFIG['types'][equip_type]['manufacturers'])
                model = random.choice(SeedConfig.EQUIPMENT_CONFIG['types'][equip_type]['models'][manufacturer])
                year = random.randint(*SeedConfig.EQUIPMENT_CONFIG['year_range'])

                # Check if should mount on vehicle based on config mount_rate
                mounted_vehicle = None
                if customer_vehicles and random.random() < SeedConfig.EQUIPMENT_CONFIG['mount_rate']:
                    mounted_vehicle = random.choice(customer_vehicles)

                equipment, created = Equipment.objects.get_or_create(
                    customer=customer,
                    asset_number=f'{customer.name[:3].upper()}-E{i+1:03d}',
                    defaults={
                        'equipment_type': equip_type,
                        'manufacturer': manufacturer,
                        'model': model,
                        'year': year,
                        'serial_number': f'{manufacturer[:3].upper()}{year}{random.randint(10000, 99999)}',
                        'mounted_on_vehicle': mounted_vehicle,
                        'engine_hours': random.randint(500, 8000),
                        'is_active': random.random() < SeedConfig.EQUIPMENT_CONFIG['active_rate'],
                        'notes': f'{year} {manufacturer} {model}. {"Mounted on " + mounted_vehicle.unit_number if mounted_vehicle else "Portable unit"}.' if random.random() > 0.6 else '',
                    }
                )
                equipment_list.append(equipment)
                if created:
                    mount_info = f' (mounted on {mounted_vehicle.unit_number})' if mounted_vehicle else ''
                    self.stdout.write(f'    [OK] Created equipment: {equipment.asset_number} ({year} {manufacturer} {model}){mount_info}')

        return equipment_list
