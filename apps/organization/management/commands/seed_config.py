"""
Configuration for seed data generation.

This config allows tests and seed data to grow with the software.
NEVER hardcode values in seed scripts - always use these config variables.
"""
from datetime import datetime, timedelta
import random


class SeedConfig:
    """Configuration for seed data generation."""

    # Company
    COMPANY = {
        'name': 'Advantage Fleet Services',
        'dba_name': 'Advantage Fleet',
        'address_line1': '2450 Industrial Parkway',
        'city': 'Springfield',
        'state': 'IL',
        'zip_code': '62701',
    }

    # Departments
    DEPARTMENTS = [
        {'name': 'Inspections', 'code': 'INSP', 'allows_floating': False},
        {'name': 'Service & Repair', 'code': 'SVCRPR', 'allows_floating': True},
        {'name': 'Customer Service', 'code': 'CUSTSVC', 'allows_floating': False},
        {'name': 'Administration', 'code': 'ADMIN', 'allows_floating': False},
    ]

    # Employee certifications by standard
    CERTIFICATIONS = {
        'ANSI_A92_2': [
            {'standard': 'ANSI A92.2-2021', 'cert_number': 'A92-2-12345', 'expiry_months': 12},
        ],
        'ANSI_A92_5': [
            {'standard': 'ANSI A92.5-2021', 'cert_number': 'A92-5-67890', 'expiry_months': 24},
        ],
        'ANSI_A92_6': [
            {'standard': 'ANSI A92.6-2020', 'cert_number': 'A92-6-54321', 'expiry_months': 18},
        ],
    }

    # Employees with certifications and skills
    EMPLOYEES = [
        # Inspections Department
        {
            'first_name': 'John',
            'last_name': 'Ramirez',
            'employee_number': 'EMP001',
            'dept_code': 'INSP',
            'email': 'john.ramirez@advantagefleet.com',
            'phone': '217-555-0101',
            'title': 'Senior Inspector',
            'certifications': ['ANSI_A92_2', 'ANSI_A92_5'],
            'skills': ['Aerial Lifts', 'Forklifts', 'USDOT Inspections'],
        },
        {
            'first_name': 'Jane',
            'last_name': 'Martinez',
            'employee_number': 'EMP002',
            'dept_code': 'INSP',
            'email': 'jane.martinez@advantagefleet.com',
            'phone': '217-555-0102',
            'title': 'Inspector',
            'certifications': ['ANSI_A92_2'],
            'skills': ['Aerial Lifts', 'ANSI Standards'],
        },
        # Service & Repair Department
        {
            'first_name': 'Robert',
            'last_name': 'Chen',
            'employee_number': 'EMP003',
            'dept_code': 'SVCRPR',
            'email': 'robert.chen@advantagefleet.com',
            'phone': '217-555-0103',
            'title': 'Lead Technician',
            'certifications': ['ANSI_A92_2', 'ANSI_A92_6'],
            'skills': ['Hydraulics', 'Electrical', 'Welding'],
        },
        {
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'employee_number': 'EMP004',
            'dept_code': 'SVCRPR',
            'email': 'alice.johnson@advantagefleet.com',
            'phone': '217-555-0104',
            'title': 'Service Technician',
            'certifications': ['ANSI_A92_2'],
            'skills': ['General Repair', 'Diagnostics'],
        },
        # Customer Service Department
        {
            'first_name': 'Carol',
            'last_name': 'Williams',
            'employee_number': 'EMP005',
            'dept_code': 'CUSTSVC',
            'email': 'carol.williams@advantagefleet.com',
            'phone': '217-555-0105',
            'title': 'Customer Service Manager',
            'certifications': [],
            'skills': ['Customer Relations', 'Scheduling'],
        },
        # Administration Department
        {
            'first_name': 'David',
            'last_name': 'Anderson',
            'employee_number': 'EMP006',
            'dept_code': 'ADMIN',
            'email': 'david.anderson@advantagefleet.com',
            'phone': '217-555-0106',
            'title': 'Operations Manager',
            'certifications': ['ANSI_A92_2', 'ANSI_A92_5', 'ANSI_A92_6'],
            'skills': ['Management', 'Operations', 'Compliance'],
        },
    ]

    # Users linked to employees with roles
    USERS = [
        {'username': 'admin', 'role': 'ADMIN', 'emp_number': 'EMP006', 'password': 'admin'},
        {'username': 'inspector1', 'role': 'INSPECTOR', 'emp_number': 'EMP001', 'password': 'admin'},
        {'username': 'inspector2', 'role': 'INSPECTOR', 'emp_number': 'EMP002', 'password': 'admin'},
        {'username': 'service1', 'role': 'SERVICE_TECH', 'emp_number': 'EMP003', 'password': 'admin'},
        {'username': 'service2', 'role': 'SERVICE_TECH', 'emp_number': 'EMP004', 'password': 'admin'},
        {'username': 'support1', 'role': 'CUSTOMER_SERVICE', 'emp_number': 'EMP005', 'password': 'admin'},
    ]

    # Customers
    CUSTOMERS = [
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

    # Contact templates with roles and correspondence preferences
    CONTACT_TEMPLATES = [
        {
            'role': 'Fleet Manager',
            'first_names': ['Michael', 'Jennifer', 'David', 'Lisa', 'Christopher'],
            'last_names': ['Thompson', 'Garcia', 'Rodriguez', 'Wilson', 'Martinez'],
            'receive_invoices': True,
            'receive_estimates': True,
            'receive_service_updates': True,
            'receive_inspection_reports': True,
            'is_primary_template': True,
            'has_portal_access': True,
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
            'has_portal_access': True,
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
            'has_portal_access': False,
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
            'has_portal_access': True,
        },
    ]

    # Automated contact template
    AUTOMATED_CONTACT = {
        'first_name': 'Maintenance',
        'last_name': 'Alerts',
        'title': 'Automated System',
        'receive_invoices': False,
        'receive_estimates': False,
        'receive_service_updates': True,
        'receive_inspection_reports': True,
        'is_automated': True,
        'has_portal_access': False,
    }

    # Vehicle configuration
    VEHICLE_CONFIG = {
        'makes_models': {
            'Freightliner': ['Cascadia', 'M2 106', 'Columbia', 'Coronado'],
            'Peterbilt': ['579', '389', '567', '520'],
            'Kenworth': ['T680', 'W900', 'T880', 'T370'],
            'Volvo': ['VNL', 'VNR', 'VHD', 'VAH'],
            'International': ['LT', 'RH', 'HX', 'MV'],
            'Mack': ['Anthem', 'Pinnacle', 'Granite', 'TerraPro'],
        },
        'body_types': ['', 'SERVICE', 'FLATBED', 'STAKE', 'DUMP', 'VAN', 'BOX'],
        'states': ['IL', 'IN', 'WI', 'MI', 'OH', 'IA'],
        'min_per_customer': 3,
        'max_per_customer': 7,
        'year_range': (2016, 2024),
        'active_rate': 0.9,  # 90% active
    }

    # Equipment configuration
    EQUIPMENT_CONFIG = {
        'types': {
            'A92_2_AERIAL': {
                'manufacturers': ['Altec', 'Terex', 'Versalift', 'Elliott', 'Manitex'],
                'models': {
                    'Altec': ['AT40G', 'AT37G', 'L42A', 'LRV-55'],
                    'Terex': ['Hi-Ranger TL50', 'TC60', 'TL40M', 'Telelect Commander'],
                    'Versalift': ['VST-240', 'SST-37', 'VO-255', 'VST-47'],
                    'Elliott': ['G85', 'G105', 'H110R', 'E120'],
                    'Manitex': ['2892C', '30112S', '22101S', '1970C'],
                },
            },
        },
        'min_per_customer': 2,
        'max_per_customer': 5,
        'year_range': (2014, 2023),
        'mount_rate': 0.6,  # 60% mounted on vehicles
        'active_rate': 0.85,  # 85% active
    }

    # USDOT profile configuration
    USDOT_CONFIG = {
        'entity_types': ['LLC', 'Corporation', 'Partnership', 'Sole Proprietorship'],
        'carrier_operations': ['Interstate', 'Intrastate', 'Interstate and Intrastate'],
        'cargo_types': [
            'General Freight',
            'Household Goods',
            'Building Materials, Commodities, Dry Van',
            'Refrigerated Food, Beverages',
            'Metal: Sheets, Coils, Rolls',
            'Machinery, Large Objects',
        ],
        'operation_classifications': [
            ['Authorized For Hire', 'Motor Carrier'],
            ['Private (Property)', 'Motor Carrier'],
            ['Authorized For Hire', 'Motor Carrier', 'Broker'],
        ],
        'safety_ratings': ['Satisfactory', 'Conditional', 'None', 'Unsatisfactory'],
        'power_units_range': (8, 85),
        'drivers_range': (5, 65),
    }

    # Inspection configuration
    INSPECTION_CONFIG = {
        'templates': [
            'ansi_a92_2_2021_annual_aerial_vehicle',
            'ansi_a92_2_2021_periodic_inspection',
            'ansi_a92_2_2021_frequent_inspection',
        ],
        'per_equipment': 2,  # Create 2 inspections per equipment
        'completion_rate': 0.8,  # 80% completed, 20% draft/in-progress
        'defect_rate': 0.6,  # 60% of completed inspections have defects
        'defects_per_inspection_range': (1, 4),  # 1-4 defects per inspection
    }

    # Work order configuration
    WORK_ORDER_CONFIG = {
        'per_customer': (2, 5),  # 2-5 work orders per customer
        'source_type_distribution': {
            'INSPECTION_DEFECT': 0.5,  # 50% from inspections
            'CUSTOMER_REQUEST': 0.3,   # 30% customer requests
            'BREAKDOWN': 0.15,          # 15% breakdowns
            'MANUAL': 0.05,             # 5% manual
        },
        'status_distribution': {
            'DRAFT': 0.1,
            'PENDING': 0.2,
            'IN_PROGRESS': 0.3,
            'COMPLETED': 0.35,
            'CANCELLED': 0.05,
        },
        'priority_distribution': {
            'LOW': 0.2,
            'NORMAL': 0.5,
            'HIGH': 0.25,
            'EMERGENCY': 0.05,
        },
    }

    # Defect seed data (following data contract)
    DEFECT_TEMPLATES = [
        {
            'severity': 'CRITICAL',
            'templates': [
                {'title': 'Hydraulic Leak at Boom Cylinder', 'component': 'Boom Cylinder', 'location': 'BOOM'},
                {'title': 'Structural Crack in Platform Rail', 'component': 'Platform Rail', 'location': 'PLATFORM'},
                {'title': 'Emergency Stop Button Not Functioning', 'component': 'Emergency Stop', 'location': 'CONTROLS'},
            ],
        },
        {
            'severity': 'MAJOR',
            'templates': [
                {'title': 'Boom Extension Cylinder Seal Wear', 'component': 'Extension Cylinder', 'location': 'BOOM'},
                {'title': 'Leveling System Malfunction', 'component': 'Leveling System', 'location': 'CHASSIS'},
                {'title': 'Outrigger Hydraulic Leak', 'component': 'Outrigger', 'location': 'OUTRIGGERS'},
            ],
        },
        {
            'severity': 'MINOR',
            'templates': [
                {'title': 'Platform Decking Worn', 'component': 'Platform Decking', 'location': 'PLATFORM'},
                {'title': 'Boom Rotation Slow', 'component': 'Rotation Motor', 'location': 'BOOM'},
                {'title': 'Warning Light Not Illuminating', 'component': 'Warning Light', 'location': 'CHASSIS'},
            ],
        },
    ]

    @staticmethod
    def get_random_hire_date(min_days=30, max_days=1000):
        """Get a random hire date in the past."""
        return datetime.now().date() - timedelta(days=random.randint(min_days, max_days))

    @staticmethod
    def get_cert_expiry_date(months_from_now):
        """Get certification expiry date."""
        return datetime.now().date() + timedelta(days=30 * months_from_now)

    @staticmethod
    def sanitize_for_domain(name):
        """Convert company name to domain-friendly string."""
        return name.lower().replace(" ", "").replace(",", "")
