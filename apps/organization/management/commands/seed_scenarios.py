"""
Scenario-based seed data configuration.

Defines realistic, complete workflows for testing rather than random data.
Each scenario represents a real-world sequence of events.
"""
from datetime import timedelta
from django.utils import timezone


class InspectionScenarios:
    """Pre-defined inspection scenarios with realistic outcomes."""

    # Scenario 1: Critical hydraulic leak found
    HYDRAULIC_LEAK_CRITICAL = {
        'name': 'Critical Hydraulic Leak Discovery',
        'equipment_index': 0,  # First equipment in list
        'template': 'ansi_a92_2_2021_periodic_inspection',
        'inspector_index': 0,
        'days_ago': 7,
        'duration_hours': 3,
        'status': 'COMPLETED',
        'defects': [
            {
                'module_key': 'hydraulic_system',
                'step_key': 'hydraulic_inspection',
                'severity': 'CRITICAL',
                'title': 'Hydraulic Leak at Boom Cylinder',
                'description': 'Active hydraulic fluid leak observed at boom cylinder rod seal. Fluid loss rate approximately 50ml/hour. Seal appears damaged with visible scoring on rod surface.',
                'location': 'BOOM',
                'component': 'Boom Cylinder',
                'recommended_action': 'Replace cylinder rod seal immediately. Inspect rod for damage. Unit should not be operated until repair is completed.',
                'standard_reference': 'ANSI A92.2-2021 Section 8.3.2 - Hydraulic System Requirements',
            }
        ]
    }

    # Scenario 2: Multiple minor issues found
    ROUTINE_MAINTENANCE_ITEMS = {
        'name': 'Routine Maintenance Items',
        'equipment_index': 1,
        'template': 'ansi_a92_2_2021_frequent_inspection',
        'inspector_index': 1,
        'days_ago': 3,
        'duration_hours': 2,
        'status': 'COMPLETED',
        'defects': [
            {
                'module_key': 'platform_safety',
                'step_key': 'platform_condition',
                'severity': 'MINOR',
                'title': 'Platform Gate Latch Worn',
                'description': 'Platform gate latch showing moderate wear. Engages properly but requires replacement soon.',
                'location': 'PLATFORM',
                'component': 'Platform Gate Latch',
                'recommended_action': 'Schedule latch replacement during next service interval.',
                'standard_reference': 'ANSI A92.2-2021 Section 6.4.1 - Platform Requirements',
            },
            {
                'module_key': 'electrical_system',
                'step_key': 'control_function',
                'severity': 'MINOR',
                'title': 'Control Button Sticking',
                'description': 'Platform up control button occasionally sticks when pressed. Function operates correctly but tactile feedback is inconsistent.',
                'location': 'PLATFORM',
                'component': 'Control Panel',
                'recommended_action': 'Clean and lubricate control buttons. Replace if cleaning does not resolve issue.',
                'standard_reference': 'ANSI A92.2-2021 Section 7.2.3 - Control Requirements',
            }
        ]
    }

    # Scenario 3: Major structural concern
    STRUCTURAL_CRACK = {
        'name': 'Structural Crack Detection',
        'equipment_index': 2,
        'template': 'ansi_a92_2_2021_annual_aerial_vehicle',
        'inspector_index': 0,
        'days_ago': 14,
        'duration_hours': 4,
        'status': 'COMPLETED',
        'defects': [
            {
                'module_key': 'structural',
                'step_key': 'weld_inspection',
                'severity': 'MAJOR',
                'title': 'Hairline Crack in Boom Weld',
                'description': 'Hairline crack approximately 2 inches in length discovered at boom base weld joint. Crack appears to be progressing. Dye penetrant test confirms crack propagation.',
                'location': 'BOOM',
                'component': 'Boom Base Weld',
                'recommended_action': 'Remove from service immediately. Conduct full structural analysis. Weld repair must be performed by certified welder per manufacturer specifications.',
                'standard_reference': 'ANSI A92.2-2021 Section 5.3.1 - Structural Integrity',
            }
        ]
    }

    # Scenario 4: Clean inspection (no defects)
    CLEAN_INSPECTION = {
        'name': 'Clean Inspection - No Issues',
        'equipment_index': 3,
        'template': 'ansi_a92_2_2021_frequent_inspection',
        'inspector_index': 1,
        'days_ago': 1,
        'duration_hours': 1,
        'status': 'COMPLETED',
        'defects': []  # No defects found
    }

    # Scenario 5: In-progress inspection
    IN_PROGRESS_INSPECTION = {
        'name': 'Inspection In Progress',
        'equipment_index': 4,
        'template': 'ansi_a92_2_2021_periodic_inspection',
        'inspector_index': 0,
        'days_ago': 0,
        'duration_hours': 0,
        'status': 'IN_PROGRESS',
        'defects': []  # Not completed yet
    }


class WorkOrderScenarios:
    """Pre-defined work order scenarios following proper workflows."""

    # Scenario 1: Work order from critical defect (Scenario 1)
    HYDRAULIC_REPAIR_FROM_INSPECTION = {
        'name': 'Emergency Hydraulic Cylinder Repair',
        'from_inspection_scenario': 'Critical Hydraulic Leak Discovery',  # Must match inspection scenario name
        'defect_index': 0,
        'days_after_inspection': 0,  # Created same day
        'priority': 'EMERGENCY',
        'assigned_employee_index': 0,  # First service tech
        'lines': [
            {
                'line_number': 1,
                'verb': 'Replace',
                'noun': 'Hydraulic Cylinder Rod Seal',
                'service_location': 'BOOM',
                'description': 'Remove and replace hydraulic cylinder rod seal. Inspect rod for scoring or damage.',
                'estimated_hours': 4.0,
                'parts_required': ['Cylinder rod seal kit', 'Hydraulic fluid (2 gal)'],
                'blocks_operation': True,
            },
            {
                'line_number': 2,
                'verb': 'Inspect',
                'noun': 'Hydraulic System',
                'service_location': 'BOOM',
                'description': 'Pressure test hydraulic system after seal replacement. Check for additional leaks.',
                'estimated_hours': 1.0,
                'parts_required': [],
                'blocks_operation': False,
            }
        ],
        'workflow': [
            {'status': 'DRAFT', 'approval_status': 'DRAFT', 'days_offset': 0},
            {'status': 'PENDING', 'approval_status': 'PENDING_APPROVAL', 'days_offset': 0},
            {'status': 'IN_PROGRESS', 'approval_status': 'APPROVED', 'days_offset': 1},
            {'status': 'COMPLETED', 'approval_status': 'APPROVED', 'days_offset': 2},
        ]
    }

    # Scenario 2: Grouped work order from minor defects (Scenario 2)
    ROUTINE_MAINTENANCE_FROM_INSPECTION = {
        'name': 'Routine Maintenance Repairs',
        'from_inspection_scenario': 'Routine Maintenance Items',  # Must match inspection scenario name
        'defect_index': None,  # Both defects
        'days_after_inspection': 2,
        'priority': 'NORMAL',
        'assigned_employee_index': 1,  # Second service tech
        'lines': [
            {
                'line_number': 1,
                'verb': 'Replace',
                'noun': 'Platform Gate Latch',
                'service_location': 'PLATFORM',
                'description': 'Replace worn platform gate latch assembly.',
                'estimated_hours': 1.5,
                'parts_required': ['Platform gate latch assembly'],
                'blocks_operation': False,
            },
            {
                'line_number': 2,
                'verb': 'Service',
                'noun': 'Control Panel',
                'service_location': 'PLATFORM',
                'description': 'Clean and lubricate control buttons. Test all functions.',
                'estimated_hours': 0.5,
                'parts_required': ['Electrical contact cleaner', 'Dielectric grease'],
                'blocks_operation': False,
            }
        ],
        'workflow': [
            {'status': 'DRAFT', 'approval_status': 'DRAFT', 'days_offset': 0},
            {'status': 'PENDING', 'approval_status': 'APPROVED', 'days_offset': 1},
            {'status': 'IN_PROGRESS', 'approval_status': 'APPROVED', 'days_offset': 3},
        ]
    }

    # Scenario 3: Customer-requested preventive maintenance
    PREVENTIVE_MAINTENANCE_CUSTOMER_REQUEST = {
        'name': '5000 Hour Preventive Maintenance',
        'from_inspection_scenario': None,  # Not from inspection
        'equipment_index': 5,
        'days_ago': 10,
        'priority': 'NORMAL',
        'assigned_employee_index': 0,
        'source_type': 'CUSTOMER_REQUEST',
        'lines': [
            {
                'line_number': 1,
                'verb': 'Replace',
                'noun': 'Hydraulic Filters',
                'service_location': 'CHASSIS',
                'description': 'Replace hydraulic system filters per manufacturer PM schedule.',
                'estimated_hours': 2.0,
                'parts_required': ['Hydraulic filter set', 'Hydraulic fluid (5 gal)'],
                'blocks_operation': False,
            },
            {
                'line_number': 2,
                'verb': 'Inspect',
                'noun': 'Hydraulic Hoses',
                'service_location': 'BOOM',
                'description': 'Visual inspection of all hydraulic hoses for wear, cracks, or damage.',
                'estimated_hours': 1.0,
                'parts_required': [],
                'blocks_operation': False,
            },
            {
                'line_number': 3,
                'verb': 'Lubricate',
                'noun': 'Boom Pivot Points',
                'service_location': 'BOOM',
                'description': 'Lubricate all boom pivot points and pins per manufacturer specifications.',
                'estimated_hours': 1.5,
                'parts_required': ['Multipurpose grease (2 tubes)'],
                'blocks_operation': False,
            }
        ],
        'workflow': [
            {'status': 'DRAFT', 'approval_status': 'DRAFT', 'days_offset': 0},
            {'status': 'PENDING', 'approval_status': 'APPROVED', 'days_offset': 1},
            {'status': 'COMPLETED', 'approval_status': 'APPROVED', 'days_offset': 8},
        ]
    }

    # Scenario 4: Emergency breakdown repair
    BREAKDOWN_EMERGENCY = {
        'name': 'Emergency Boom Failure Repair',
        'from_inspection_scenario': None,
        'equipment_index': 6,
        'days_ago': 5,
        'priority': 'EMERGENCY',
        'assigned_employee_index': 1,
        'source_type': 'BREAKDOWN',
        'lines': [
            {
                'line_number': 1,
                'verb': 'Repair',
                'noun': 'Electrical System',
                'service_location': 'BOOM',
                'description': 'Diagnose and repair boom elevation function failure. Replace failed contactor.',
                'estimated_hours': 3.0,
                'parts_required': ['Main contactor', 'Wire terminals (10 pack)'],
                'blocks_operation': True,
            }
        ],
        'workflow': [
            {'status': 'DRAFT', 'approval_status': 'DRAFT', 'days_offset': 0},
            {'status': 'IN_PROGRESS', 'approval_status': 'APPROVED', 'days_offset': 0},  # Emergency, approved immediately
            {'status': 'COMPLETED', 'approval_status': 'APPROVED', 'days_offset': 0},  # Same day repair
        ]
    }

    # Scenario 5: Pending approval work order
    PENDING_APPROVAL = {
        'name': 'Platform Deck Replacement',
        'from_inspection_scenario': None,
        'equipment_index': 7,
        'days_ago': 2,
        'priority': 'HIGH',
        'assigned_employee_index': None,  # Not assigned yet
        'source_type': 'MANUAL',
        'lines': [
            {
                'line_number': 1,
                'verb': 'Replace',
                'noun': 'Platform Deck',
                'service_location': 'PLATFORM',
                'description': 'Remove and replace platform deck flooring due to excessive wear.',
                'estimated_hours': 6.0,
                'parts_required': ['Platform deck kit', 'Fasteners (50 pack)'],
                'blocks_operation': True,
            }
        ],
        'workflow': [
            {'status': 'DRAFT', 'approval_status': 'DRAFT', 'days_offset': 0},
            {'status': 'PENDING', 'approval_status': 'PENDING_APPROVAL', 'days_offset': 1},
        ]
    }


# Registry of all scenarios
ALL_INSPECTION_SCENARIOS = [
    InspectionScenarios.HYDRAULIC_LEAK_CRITICAL,
    InspectionScenarios.ROUTINE_MAINTENANCE_ITEMS,
    InspectionScenarios.STRUCTURAL_CRACK,
    InspectionScenarios.CLEAN_INSPECTION,
    InspectionScenarios.IN_PROGRESS_INSPECTION,
]

ALL_WORK_ORDER_SCENARIOS = [
    WorkOrderScenarios.HYDRAULIC_REPAIR_FROM_INSPECTION,
    WorkOrderScenarios.ROUTINE_MAINTENANCE_FROM_INSPECTION,
    WorkOrderScenarios.PREVENTIVE_MAINTENANCE_CUSTOMER_REQUEST,
    WorkOrderScenarios.BREAKDOWN_EMERGENCY,
    WorkOrderScenarios.PENDING_APPROVAL,
]
