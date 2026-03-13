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
from datetime import datetime, timedelta, date
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
        self._create_usdot_profiles(customers)
        contacts = self._create_contacts(customers)
        vehicles = self._create_vehicles(customers)
        equipment = self._create_equipment(customers, vehicles)

        self.stdout.write(self.style.SUCCESS('[OK] Data seed completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'  - Company: 1'))
        self.stdout.write(self.style.SUCCESS(f'  - Departments: {len(departments)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Employees: {len(employees)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Users: {len(users)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Customers: {len(customers)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Contacts: {len(contacts)}'))
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
            name='Advantage Fleet Services',
            defaults={
                'dba_name': 'Advantage Fleet',
                'address_line1': '2450 Industrial Parkway',
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
            {'first_name': 'John', 'last_name': 'Ramirez', 'employee_number': 'EMP001', 'dept': 0},
            {'first_name': 'Jane', 'last_name': 'Martinez', 'employee_number': 'EMP002', 'dept': 0},
            # Service & Repair
            {'first_name': 'Robert', 'last_name': 'Chen', 'employee_number': 'EMP003', 'dept': 1},
            {'first_name': 'Alice', 'last_name': 'Johnson', 'employee_number': 'EMP004', 'dept': 1},
            # Customer Service
            {'first_name': 'Carol', 'last_name': 'Williams', 'employee_number': 'EMP005', 'dept': 2},
            # Administration
            {'first_name': 'David', 'last_name': 'Anderson', 'employee_number': 'EMP006', 'dept': 3},
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
            {'username': 'admin', 'role': 'ADMIN', 'emp_index': 5},  # David Anderson
            {'username': 'inspector1', 'role': 'INSPECTOR', 'emp_index': 0},  # John Ramirez
            {'username': 'inspector2', 'role': 'INSPECTOR', 'emp_index': 1},  # Jane Martinez
            {'username': 'service1', 'role': 'SERVICE_TECH', 'emp_index': 2},  # Robert Chen
            {'username': 'service2', 'role': 'SERVICE_TECH', 'emp_index': 3},  # Alice Johnson
            {'username': 'support1', 'role': 'CUSTOMER_SERVICE', 'emp_index': 4},  # Carol Williams
        ]

        users = []
        for data in users_data:
            emp = employees[data['emp_index']]
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': f"{data['username']}@advantagefleet.com",
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
        """Create customers with comprehensive data."""
        customers_data = [
            {
                'name': 'Midwest Express Logistics',
                'legal_name': 'Midwest Express Logistics, LLC',
                'usdot_number': '2847291',
                'mc_number': 'MC938472',
                'address_line1': '4820 Commerce Drive',
                'address_line2': 'Suite 200',
                'city': 'Chicago',
                'state': 'IL',
                'postal_code': '60607',
                'country': 'US',
                'notes': 'Preferred customer. Monthly inspections required. Contact 24 hours in advance for scheduling.',
            },
            {
                'name': 'Northern Freight Solutions',
                'legal_name': 'Northern Freight Solutions Corporation',
                'usdot_number': '1947382',
                'mc_number': 'MC847392',
                'address_line1': '1567 Industrial Boulevard',
                'city': 'Milwaukee',
                'state': 'WI',
                'postal_code': '53204',
                'country': 'US',
                'notes': 'Large fleet customer. Quarterly inspections for entire fleet. Invoices NET 30.',
            },
            {
                'name': 'Metro Delivery Services',
                'legal_name': 'Metro Delivery Services Inc',
                'usdot_number': '3928471',
                'mc_number': 'MC102938',
                'address_line1': '892 Warehouse Row',
                'city': 'Indianapolis',
                'state': 'IN',
                'postal_code': '46225',
                'country': 'US',
                'notes': 'Weekly maintenance schedule. Emergency service available 24/7.',
            },
            {
                'name': 'Prairie Hauling Co',
                'legal_name': 'Prairie Hauling Company',
                'address_line1': '2301 County Road 15',
                'city': 'Peoria',
                'state': 'IL',
                'postal_code': '61615',
                'country': 'US',
                'notes': 'Small fleet. Bi-annual inspection schedule.',
            },
            {
                'name': 'Great Lakes Transport',
                'legal_name': 'Great Lakes Transport Holdings LLC',
                'usdot_number': '2103847',
                'mc_number': 'MC847201',
                'address_line1': '7450 Lakeshore Drive',
                'address_line2': 'Building C',
                'city': 'Gary',
                'state': 'IN',
                'postal_code': '46402',
                'country': 'US',
                'notes': 'Multiple locations. Corporate account with centralized billing.',
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
                        'entity_type': random.choice(['LLC', 'Corporation', 'Partnership', 'Sole Proprietorship']),
                        'physical_address': customer.address_line1,
                        'physical_city': customer.city,
                        'physical_state': customer.state,
                        'physical_zip': customer.postal_code,
                        'mailing_address': customer.address_line1,
                        'mailing_city': customer.city,
                        'mailing_state': customer.state,
                        'mailing_zip': customer.postal_code,
                        'phone': '555-0000',
                        'email': f'info@{customer.name.lower().replace(" ", "").replace(",", "")}.com',
                        'carrier_operation': random.choice(['Interstate', 'Intrastate', 'Interstate and Intrastate']),
                        'cargo_carried': random.choice([
                            'General Freight',
                            'Household Goods',
                            'Building Materials, Commodities, Dry Van',
                            'Refrigerated Food, Beverages',
                            'Metal: Sheets, Coils, Rolls',
                            'Machinery, Large Objects',
                        ]),
                        'operation_classification': random.choice([
                            ['Authorized For Hire', 'Motor Carrier'],
                            ['Private (Property)', 'Motor Carrier'],
                            ['Authorized For Hire', 'Motor Carrier', 'Broker'],
                        ]),
                        'safety_rating': random.choice(['Satisfactory', 'Conditional', 'None', 'Unsatisfactory']),
                        'out_of_service_date': None,
                        'total_power_units': random.randint(8, 85),
                        'total_drivers': random.randint(5, 65),
                        'raw_fmcsa_data': {},
                    }
                )
                if created:
                    self.stdout.write(f'    [OK] Created USDOT profile for {customer.name}')

    def _create_contacts(self, customers):
        """Create diverse contacts for customers with varied correspondence preferences."""
        # Contact templates with different roles and preferences
        contact_templates = [
            {
                'role': 'Fleet Manager',
                'first_names': ['Michael', 'Jennifer', 'David', 'Lisa', 'Christopher'],
                'last_names': ['Thompson', 'Garcia', 'Rodriguez', 'Wilson', 'Martinez'],
                'receive_invoices': True,
                'receive_estimates': True,
                'receive_service_updates': True,
                'receive_inspection_reports': True,
                'is_primary_template': True,
            },
            {
                'role': 'Accounting Manager',
                'first_names': ['Sarah', 'James', 'Patricia', 'Robert', 'Linda'],
                'last_names': ['Anderson', 'Taylor', 'Moore', 'Jackson', 'White'],
                'receive_invoices': True,
                'receive_estimates': True,
                'receive_service_updates': False,
                'receive_inspection_reports': False,
                'is_primary_template': False,
            },
            {
                'role': 'Operations Director',
                'first_names': ['William', 'Mary', 'Richard', 'Barbara', 'Thomas'],
                'last_names': ['Harris', 'Martin', 'Brown', 'Davis', 'Miller'],
                'receive_invoices': False,
                'receive_estimates': True,
                'receive_service_updates': True,
                'receive_inspection_reports': True,
                'is_primary_template': False,
            },
            {
                'role': 'Safety Coordinator',
                'first_names': ['Charles', 'Susan', 'Joseph', 'Jessica', 'Daniel'],
                'last_names': ['Wilson', 'Lee', 'Walker', 'Hall', 'Allen'],
                'receive_invoices': False,
                'receive_estimates': False,
                'receive_service_updates': True,
                'receive_inspection_reports': True,
                'is_primary_template': False,
            },
        ]

        # Add an automated email system for some customers
        automated_contact_template = {
            'first_name': 'Maintenance',
            'last_name': 'Alerts',
            'title': 'Automated System',
            'receive_invoices': False,
            'receive_estimates': False,
            'receive_service_updates': True,
            'receive_inspection_reports': True,
            'is_automated': True,
        }

        all_contacts = []
        for customer in customers:
            # Create 3-4 regular contacts per customer
            num_contacts = random.randint(3, 4)
            templates_to_use = random.sample(contact_templates, num_contacts)

            for idx, template in enumerate(templates_to_use):
                first_name = random.choice(template['first_names'])
                last_name = random.choice(template['last_names'])
                email = f'{first_name.lower()}.{last_name.lower()}@{customer.name.lower().replace(" ", "").replace(",", "")}.com'

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
                auto_email = f'alerts@{customer.name.lower().replace(" ", "").replace(",", "")}.com'
                auto_contact, created = Contact.objects.get_or_create(
                    customer=customer,
                    email=auto_email,
                    defaults=automated_contact_template
                )
                all_contacts.append(auto_contact)
                if created:
                    self.stdout.write(f'    [OK] Created automated contact for {customer.name}')

        return all_contacts

    def _create_vehicles(self, customers):
        """Create vehicles with comprehensive data."""
        truck_makes = ['Freightliner', 'Peterbilt', 'Kenworth', 'Volvo', 'International', 'Mack']
        truck_models = {
            'Freightliner': ['Cascadia', 'M2 106', 'Columbia', 'Coronado'],
            'Peterbilt': ['579', '389', '567', '520'],
            'Kenworth': ['T680', 'W900', 'T880', 'T370'],
            'Volvo': ['VNL', 'VNR', 'VHD', 'VAH'],
            'International': ['LT', 'RH', 'HX', 'MV'],
            'Mack': ['Anthem', 'Pinnacle', 'Granite', 'TerraPro'],
        }
        body_types = ['', 'AERIAL']  # Valid choices from model
        states = ['IL', 'IN', 'WI', 'MI', 'OH', 'IA']

        vehicles = []
        for customer in customers:
            # 3-7 vehicles per customer based on fleet size
            num_vehicles = random.randint(3, 7)

            for i in range(num_vehicles):
                make = random.choice(truck_makes)
                model = random.choice(truck_models[make])
                year = random.randint(2016, 2024)
                # Most trucks have standard body, 20% have aerial
                body_type = 'AERIAL' if random.random() < 0.2 else ''

                vehicle, created = Vehicle.objects.get_or_create(
                    customer=customer,
                    unit_number=f'{customer.name[:3].upper()}-{i+1:03d}',
                    defaults={
                        'vin': f'1HGBH41JXMN{random.randint(100000, 999999)}',
                        'year': year,
                        'make': make,
                        'model': model,
                        'body_type': body_type,
                        'license_plate': f'{random.choice(states)}{random.choice(["T", "K", "F"])}{random.randint(10000, 99999)}',
                        'odometer_miles': random.randint(50000, 450000),
                        'engine_hours': random.randint(2000, 15000),
                        'is_active': random.random() > 0.1,  # 90% active
                        'notes': f'{year} {make} {model}. Regular maintenance schedule.' if random.random() > 0.7 else '',
                    }
                )
                vehicles.append(vehicle)
                if created:
                    self.stdout.write(f'    [OK] Created vehicle: {vehicle.unit_number} ({year} {make} {model})')

        return vehicles

    def _create_equipment(self, customers, vehicles):
        """Create equipment with comprehensive data, some mounted on vehicles."""
        # Only AERIAL_DEVICE is valid choice currently
        equipment_types = {
            'AERIAL_DEVICE': {
                'manufacturers': ['Altec', 'Terex', 'Versalift', 'Elliott', 'Manitex'],
                'models': {
                    'Altec': ['AT40G', 'AT37G', 'L42A', 'LRV-55'],
                    'Terex': ['Hi-Ranger TL50', 'TC60', 'TL40M', 'Telelect Commander'],
                    'Versalift': ['VST-240', 'SST-37', 'VO-255', 'VST-47'],
                    'Elliott': ['G85', 'G105', 'H110R', 'E120'],
                    'Manitex': ['2892C', '30112S', '22101S', '1970C'],
                },
            },
        }

        equipment_list = []
        for customer in customers:
            # Get customer's vehicles for potential mounting
            customer_vehicles = [v for v in vehicles if v.customer == customer]

            # 2-5 equipment pieces per customer
            num_equipment = random.randint(2, 5)

            for i in range(num_equipment):
                equip_type = random.choice(list(equipment_types.keys()))
                manufacturer = random.choice(equipment_types[equip_type]['manufacturers'])
                model = random.choice(equipment_types[equip_type]['models'][manufacturer])
                year = random.randint(2014, 2023)

                # 60% chance to mount on a vehicle if vehicles available
                mounted_vehicle = None
                if customer_vehicles and random.random() > 0.4:
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
                        'is_active': random.random() > 0.15,  # 85% active
                        'notes': f'{year} {manufacturer} {model}. {"Mounted on " + mounted_vehicle.unit_number if mounted_vehicle else "Portable unit"}.' if random.random() > 0.6 else '',
                    }
                )
                equipment_list.append(equipment)
                if created:
                    mount_info = f' (mounted on {mounted_vehicle.unit_number})' if mounted_vehicle else ''
                    self.stdout.write(f'    [OK] Created equipment: {equipment.asset_number} ({year} {manufacturer} {model}){mount_info}')

        return equipment_list
