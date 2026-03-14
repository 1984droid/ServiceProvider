"""
Test Configuration - Single source of truth for all test data.

NO HARDCODED VALUES IN TESTS! All test data comes from this config.
This allows tests to grow with the application without breaking.
"""

# Customer Test Data
CUSTOMER_DATA = {
    'default': {
        'name': 'Acme Utilities',
        'legal_name': 'Acme Utilities Corporation',
        'address_line1': '123 Main Street',
        'city': 'Springfield',
        'state': 'IL',
        'postal_code': '62701',
        'country': 'US',
        'usdot_number': '123456',
        'mc_number': 'MC654321',
    },
    'minimal': {
        'name': 'Simple Co',
    },
    'with_usdot': {
        'name': 'USDOT Carrier',
        'usdot_number': '999888',
    },
}

# Contact Test Data
CONTACT_DATA = {
    'default': {
        'first_name': 'John',
        'last_name': 'Smith',
        'title': 'Fleet Manager',
        'email': 'john.smith@example.com',
        'phone': '555-0100',
        'mobile': '555-0101',
        'receive_invoices': True,
        'receive_service_updates': True,
    },
    'minimal': {
        'first_name': 'Jane',
        'last_name': 'Doe',
        'email': 'jane@example.com',
    },
    'automated': {
        'first_name': 'API',
        'last_name': 'System',
        'email': 'api@example.com',
        'is_automated': True,
    },
}

# Vehicle Test Data
VEHICLE_DATA = {
    'default': {
        'vin': '1HGCM82633A123456',
        'unit_number': 'T-001',
        'year': 2020,
        'make': 'Ford',
        'model': 'F-350',
        'license_plate': 'ABC1234',
        'odometer_miles': 50000,
        'engine_hours': 2500,
        'capabilities': ['UTILITY_TRUCK'],
    },
    'minimal': {
        'vin': '1HGCM82633A654321',
    },
    'insulated_boom': {
        'vin': '1HGCM82633A111111',
        'unit_number': 'T-100',
        'year': 2021,
        'make': 'International',
        'model': '4300',
        'capabilities': ['INSULATED_BOOM', 'DIELECTRIC'],
    },
}

# Equipment Test Data
EQUIPMENT_DATA = {
    'default': {
        'serial_number': 'SN-ABC-12345',
        'asset_number': 'EQ-001',
        'equipment_type': 'A92_2_AERIAL',
        'manufacturer': 'Terex',
        'model': 'HRX55',
        'year': 2020,
        'engine_hours': 500,
        'capabilities': ['AERIAL_DEVICE'],
    },
    'minimal': {
        'serial_number': 'SN-MIN-00001',
        'equipment_type': 'A92_2_AERIAL',
    },
    'insulated_aerial': {
        'serial_number': 'SN-AERIAL-9999',
        'asset_number': 'EQ-100',
        'equipment_type': 'A92_2_AERIAL',
        'manufacturer': 'Altec',
        'model': 'AT40G',
        'year': 2021,
        'capabilities': ['DIELECTRIC'],
        'equipment_data': {
            'placard_data': {
                'max_platform_height': 45,
                'max_working_height': 51,
                'platform_capacity': 500,
                'max_wind_speed': 28,
            },
            'dielectric': {
                'insulation_rating_kv': 46,
                'last_test_date': '2024-06-15',
                'next_test_due': '2025-06-15',
                'test_certificate_number': 'DT-2024-1234',
            },
        },
    },
}

# VIN Decode Test Data
VIN_DECODE_DATA = {
    'default': {
        'vin': '1HGCM82633A123456',
        'model_year': 2020,
        'make': 'Ford',
        'model': 'F-350',
        'manufacturer': 'Ford Motor Company',
        'vehicle_type': 'Truck',
        'body_class': 'Cab & Chassis',
        'engine_model': 'Power Stroke',
        'engine_cylinders': 8,
        'displacement_liters': 6.7,
        'fuel_type_primary': 'Diesel',
        'gvwr': 'Class 3: 10,001 - 14,000 lb (4,536 - 6,350 kg)',
        'gvwr_min_lbs': 10001,
        'gvwr_max_lbs': 14000,
        'error_code': '0',
    },
    'error': {
        'vin': 'INVALID_VIN_123',
        'error_code': '7',
        'error_text': 'Invalid VIN format',
    },
}

# USDOT Profile Test Data
USDOT_PROFILE_DATA = {
    'default': {
        'usdot_number': '123456',
        'mc_number': 'MC654321',
        'legal_name': 'Acme Utilities Corporation',
        'dba_name': 'Acme Utilities',
        'physical_address': '123 Main Street',
        'physical_city': 'Springfield',
        'physical_state': 'IL',
        'physical_zip': '62701',
        'phone': '555-0200',
        'email': 'dispatch@acmeutilities.com',
        'safety_rating': 'SATISFACTORY',
        'total_power_units': 25,
        'total_drivers': 30,
    },
}

# Inspection Run Test Data
INSPECTION_RUN_DATA = {
    'default': {
        'asset_type': 'EQUIPMENT',
        'template_key': 'ansi_a92_2_periodic',
        'program_key': 'ANSI_A92_2',
        'status': 'DRAFT',
        'started_at': '2025-01-15T08:00:00Z',
        'inspector_name': 'John Smith',
        'template_snapshot': {
            'template_key': 'ansi_a92_2_periodic',
            'template_version': '1.0',
            'modules': [
                {
                    'module_key': 'visual_inspection',
                    'title': 'Visual Inspection',
                    'steps': [
                        {
                            'step_key': 'hydraulic_leaks',
                            'title': 'Check for Hydraulic Leaks',
                            'type': 'pass_fail',
                        },
                    ],
                },
            ],
        },
        'step_data': {},
        'notes': '',
    },
    'in_progress': {
        'asset_type': 'EQUIPMENT',
        'template_key': 'ansi_a92_2_periodic',
        'program_key': 'ANSI_A92_2',
        'status': 'IN_PROGRESS',
        'started_at': '2025-01-15T08:00:00Z',
        'inspector_name': 'Jane Doe',
        'template_snapshot': {
            'template_key': 'ansi_a92_2_periodic',
            'template_version': '1.0',
            'modules': [],
        },
        'step_data': {
            'visual_inspection.hydraulic_leaks': {
                'value': 'FAIL',
                'notes': 'Leak detected at cylinder base',
            },
        },
    },
    'completed': {
        'asset_type': 'EQUIPMENT',
        'template_key': 'ansi_a92_2_periodic',
        'program_key': 'ANSI_A92_2',
        'status': 'COMPLETED',
        'started_at': '2025-01-15T08:00:00Z',
        'finalized_at': '2025-01-15T10:30:00Z',
        'inspector_name': 'Bob Johnson',
        'inspector_signature': {
            'signature_data': 'base64_signature_here',
            'signed_at': '2025-01-15T10:30:00Z',
            'signed_by': 'Bob Johnson',
            'ip_address': '192.168.1.100',
        },
        'template_snapshot': {
            'template_key': 'ansi_a92_2_periodic',
            'template_version': '1.0',
            'modules': [],
        },
        'step_data': {
            'visual_inspection.hydraulic_leaks': {'value': 'PASS'},
            'visual_inspection.structural_damage': {'value': 'PASS'},
        },
    },
}

# Inspection Defect Test Data
INSPECTION_DEFECT_DATA = {
    'critical': {
        'module_key': 'visual_inspection',
        'step_key': 'hydraulic_leaks',
        'rule_id': 'hydraulic_leak_check',
        'severity': 'CRITICAL',
        'status': 'OPEN',
        'title': 'Hydraulic Leak Detected at Cylinder Base',
        'description': 'Significant hydraulic fluid leak observed at the base cylinder connection. Equipment is unsafe to operate.',
        'defect_details': {
            'location': 'Base cylinder connection',
            'photos': ['photo1.jpg', 'photo2.jpg'],
            'measurements': {
                'leak_rate': 'moderate',
                'fluid_level': 'low',
            },
        },
        'evaluation_trace': {
            'rule_id': 'hydraulic_leak_check',
            'condition': 'response == FAIL',
            'evaluated_at': '2025-01-15T09:15:00Z',
            'response_data': {'value': 'FAIL'},
        },
    },
    'major': {
        'module_key': 'structural_inspection',
        'step_key': 'weld_integrity',
        'rule_id': 'weld_crack_check',
        'severity': 'MAJOR',
        'status': 'OPEN',
        'title': 'Crack in Boom Weld',
        'description': 'Small crack detected in boom weld joint. Requires immediate attention.',
        'defect_details': {
            'location': 'Boom section 2, weld joint',
            'crack_length_mm': 15,
        },
        'evaluation_trace': {
            'rule_id': 'weld_crack_check',
            'condition': 'crack_detected == true',
            'evaluated_at': '2025-01-15T09:30:00Z',
        },
    },
    'minor': {
        'module_key': 'visual_inspection',
        'step_key': 'paint_condition',
        'rule_id': None,
        'severity': 'MINOR',
        'status': 'OPEN',
        'title': 'Paint Chipping on Platform Rail',
        'description': 'Minor paint damage observed on platform rail. Cosmetic issue.',
        'defect_details': {
            'location': 'Platform rail, left side',
        },
        'evaluation_trace': None,
    },
}

# Work Order Test Data
WORK_ORDER_DATA = {
    'default': {
        'asset_type': 'EQUIPMENT',
        'status': 'DRAFT',
        'priority': 'NORMAL',
        'source': 'INSPECTION',
        'description': 'Repair hydraulic leak at cylinder base',
        'notes': '',
    },
    'scheduled': {
        'asset_type': 'EQUIPMENT',
        'status': 'PENDING',
        'priority': 'HIGH',
        'source': 'INSPECTION',
        'description': 'Repair critical defects from inspection',
        'scheduled_date': '2025-01-20',
        'notes': 'Parts ordered, ETA 2 days',
    },
    'completed': {
        'asset_type': 'EQUIPMENT',
        'status': 'COMPLETED',
        'priority': 'HIGH',
        'source': 'INSPECTION',
        'description': 'Repaired hydraulic leak and replaced seals',
        'scheduled_date': '2025-01-20',
        'started_at': '2025-01-20T08:00:00Z',
        'completed_at': '2025-01-20T14:30:00Z',
        'odometer_at_service': None,
        'engine_hours_at_service': 2547,
        'notes': 'Replaced cylinder seals and refilled hydraulic fluid',
    },
    'customer_request': {
        'asset_type': 'VEHICLE',
        'status': 'DRAFT',
        'priority': 'LOW',
        'source': 'CUSTOMER_REQUEST',
        'description': 'Customer requested oil change and tire rotation',
        'source_inspection_run': None,
    },
}

# Valid Values for Choice Fields
VALID_CHOICES = {
    'states': ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'],
    'safety_ratings': ['SATISFACTORY', 'CONDITIONAL', 'UNSATISFACTORY'],
    'equipment_types': ['A92_2_AERIAL', 'A92_20_SCISSOR', 'A92_20_BOOM', 'DIGGER_DERRICK', 'FORKLIFT'],
    'vehicle_tags': ['INSULATED_BOOM', 'DIELECTRIC', 'UTILITY_TRUCK', 'BUCKET_TRUCK', 'CRANE', 'HEAVY_DUTY'],
    'equipment_tags': ['AERIAL_DEVICE', 'INSULATED_BOOM', 'DIELECTRIC', 'CRANE', 'HYDRAULIC', 'PNEUMATIC'],
    'asset_types': ['VEHICLE', 'EQUIPMENT'],
    'inspection_statuses': ['DRAFT', 'IN_PROGRESS', 'COMPLETED'],
    'defect_severities': ['CRITICAL', 'MAJOR', 'MINOR', 'ADVISORY'],
    'defect_statuses': ['OPEN', 'WORK_ORDER_CREATED', 'RESOLVED'],
    'work_order_statuses': ['DRAFT', 'PENDING', 'IN_PROGRESS', 'ON_HOLD', 'COMPLETED', 'CANCELLED'],
    'work_order_priorities': ['LOW', 'NORMAL', 'HIGH', 'EMERGENCY'],
    'work_order_sources': ['INSPECTION', 'CUSTOMER_REQUEST', 'PM_SCHEDULE', 'BREAKDOWN'],
}

# Test VINs (valid format for testing)
TEST_VINS = [
    '1HGCM82633A123456',
    '1HGCM82633A654321',
    '1HGCM82633A111111',
    '1HGCM82633A222222',
    '1HGCM82633A333333',
    'JH4KA7561MC001234',
    '5FNRL38209B123456',
    'WBAPH7C51BE123456',
]

# Test Serial Numbers
TEST_SERIAL_NUMBERS = [
    'SN-ABC-12345',
    'SN-MIN-00001',
    'SN-AERIAL-9999',
    'SN-TEST-0001',
    'SN-TEST-0002',
    'SN-TEST-0003',
]

# API Test Configuration
API_CONFIG = {
    'page_size': 10,
    'max_page_size': 100,
    'throttle_rate': '100/hour',
}

# Validation Rules (for testing constraints)
VALIDATION_RULES = {
    'vin_length': 17,
    'state_code_length': 2,
    'country_code_length': 2,
    'min_year': 1900,
    'email_regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
}

# Database Constraints (for testing)
CONSTRAINTS = {
    'unique_fields': {
        'customer': ['usdot_number', 'mc_number'],
        'vehicle': ['vin'],
        'equipment': ['serial_number'],
    },
    'required_fields': {
        'customer': ['name'],
        'contact': ['customer', 'first_name', 'last_name'],
        'vehicle': ['customer', 'vin'],
        'equipment': ['customer', 'serial_number'],
    },
    'vehicle': {
        'vin': {
            'exact_length': 17,
            'min_length': 17,
            'max_length': 17,
        },
        'year': {
            'min_value': 1900,
            'max_value': 2100,
        },
    },
    'equipment': {
        'year': {
            'min_value': 1900,
            'max_value': 2100,
        },
    },
    'customer': {
        'name': {
            'max_length': 255,
        },
        'state': {
            'max_length': 2,
            'valid_choices': ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                             'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                             'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                             'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                             'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'],
        },
    },
    'inspection_defect': {
        'identity': {
            'exact_length': 64,
        },
    },
}

# Test User Credentials
TEST_USERS = {
    'admin': {
        'username': 'admin',
        'password': 'testpass123',
        'email': 'admin@test.com',
        'is_staff': True,
        'is_superuser': True,
    },
    'regular': {
        'username': 'user',
        'password': 'testpass123',
        'email': 'user@test.com',
        'is_staff': False,
        'is_superuser': False,
    },
}

# Expected Error Messages (for validation testing)
ERROR_MESSAGES = {
    'vin_length': 'VIN must be exactly 17 characters',
    'vin_unique': 'Vehicle with VIN {vin} already exists',
    'serial_unique': 'Equipment with serial number {serial} already exists',
    'usdot_unique': 'Customer with USDOT number {usdot} already exists',
    'primary_contact_mismatch': 'Primary contact must belong to this customer',
    'email_required_automated': 'Automated contacts must have an email address',
}

# Company Test Data
COMPANY_DATA = {
    'default': {
        'name': 'Test Service Company LLC',
        'dba_name': 'TestCo Service',
        'phone': '555-0100',
        'email': 'info@testco.com',
        'website': 'https://testco.com',
        'address_line1': '100 Industrial Parkway',
        'address_line2': 'Suite 200',
        'city': 'Springfield',
        'state': 'IL',
        'zip_code': '62701',
        'tax_id': '12-3456789',
        'usdot_number': '9876543',
        'settings': {},
    },
    'minimal': {
        'name': 'Minimal Company',
    },
}

# Department Test Data
DEPARTMENT_DATA = {
    'default': {
        'name': 'Service',
        'code': 'SRV',
        'description': 'Service and repair department',
        'is_active': True,
        'allows_floating': True,
    },
    'inspection': {
        'name': 'Inspection',
        'code': 'INSP',
        'description': 'Equipment inspection department',
        'is_active': True,
        'allows_floating': True,
    },
    'parts': {
        'name': 'Parts',
        'code': 'PART',
        'description': 'Parts and inventory department',
        'is_active': True,
        'allows_floating': False,
    },
    'minimal': {
        'name': 'Admin',
        'code': 'ADM',
    },
}

# Employee Test Data
EMPLOYEE_DATA = {
    'default': {
        'employee_number': 'E001',
        'first_name': 'John',
        'last_name': 'Smith',
        'email': 'john.smith@testco.com',
        'phone': '555-0101',
        'title': 'Lead Technician',
        'is_active': True,
        'certifications': ['ASE Master', 'CDL Class A'],
        'skills': ['Diesel Repair', 'Hydraulics', 'Electrical'],
        'settings': {},
    },
    'inspector': {
        'employee_number': 'E002',
        'first_name': 'Jane',
        'last_name': 'Doe',
        'email': 'jane.doe@testco.com',
        'phone': '555-0102',
        'title': 'Senior Inspector',
        'is_active': True,
        'certifications': ['ANSI A92.2', 'IPAF'],
        'skills': ['Aerial Inspections', 'Report Writing'],
        'settings': {},
    },
    'minimal': {
        'employee_number': 'E999',
        'first_name': 'Test',
        'last_name': 'User',
    },
}


def get_test_data(model_name, variant='default'):
    """
    Get test data for a model.

    Args:
        model_name: Name of model (customer, contact, vehicle, equipment, etc.)
        variant: Variant of data to get (default, minimal, etc.)

    Returns:
        dict: Test data for creating model instance

    Example:
        >>> data = get_test_data('customer', 'minimal')
        >>> customer = Customer.objects.create(**data)
    """
    data_map = {
        'customer': CUSTOMER_DATA,
        'contact': CONTACT_DATA,
        'vehicle': VEHICLE_DATA,
        'equipment': EQUIPMENT_DATA,
        'vin_decode': VIN_DECODE_DATA,
        'usdot_profile': USDOT_PROFILE_DATA,
        'inspection_run': INSPECTION_RUN_DATA,
        'inspection_defect': INSPECTION_DEFECT_DATA,
        'work_order': WORK_ORDER_DATA,
        'company': COMPANY_DATA,
        'department': DEPARTMENT_DATA,
        'employee': EMPLOYEE_DATA,
    }

    if model_name not in data_map:
        raise ValueError(f"Unknown model: {model_name}")

    data = data_map[model_name].get(variant)
    if data is None:
        raise ValueError(f"Unknown variant '{variant}' for model '{model_name}'")

    # Return a copy to prevent accidental mutation
    import copy
    return copy.deepcopy(data)


def get_next_test_vin(used_vins=None):
    """
    Get next available test VIN.

    Args:
        used_vins: Set of VINs already used in this test

    Returns:
        str: Next available VIN from TEST_VINS
    """
    if used_vins is None:
        used_vins = set()

    for vin in TEST_VINS:
        if vin not in used_vins:
            return vin

    # If all used, generate a new one
    import random
    return f"1HGCM82633A{random.randint(100000, 999999)}"


def get_next_test_serial(used_serials=None):
    """
    Get next available test serial number.

    Args:
        used_serials: Set of serial numbers already used in this test

    Returns:
        str: Next available serial number
    """
    if used_serials is None:
        used_serials = set()

    for serial in TEST_SERIAL_NUMBERS:
        if serial not in used_serials:
            return serial

    # If all used, generate a new one
    import random
    return f"SN-TEST-{random.randint(10000, 99999)}"
