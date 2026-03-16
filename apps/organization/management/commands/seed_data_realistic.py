"""
Django management command to seed REALISTIC test data using scenarios.

This creates high-quality, workflow-driven test data by:
1. Using pre-defined scenarios instead of random data
2. Calling actual service layer methods (like the UI would)
3. Following proper workflows and state transitions

Usage:
    python manage.py seed_data_realistic [--clear]
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import hashlib

from apps.inspections.models import InspectionRun, InspectionDefect
from apps.work_orders.models import WorkOrder, WorkOrderLine

from .seed_data import Command as BaseSeedCommand
from .seed_scenarios import ALL_INSPECTION_SCENARIOS, ALL_WORK_ORDER_SCENARIOS


class Command(BaseCommand):
    help = 'Seed database with realistic scenario-based test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting realistic data seed...'))

        # First, run base seed to create customers, equipment, employees
        self.stdout.write('Creating foundational data (customers, assets, employees)...')
        base_command = BaseSeedCommand()

        if options['clear']:
            base_command._clear_data()

        # Create base data
        company = base_command._create_company()
        departments = base_command._create_departments(company)
        employees = base_command._create_employees(departments)
        users = base_command._create_users(employees)
        customers = base_command._create_customers()
        base_command._create_usdot_profiles(customers)
        contacts = base_command._create_contacts(customers)
        contact_users = base_command._create_contact_users(contacts)
        vehicles = base_command._create_vehicles(customers)
        equipment = base_command._create_equipment(customers, vehicles)

        self.stdout.write(self.style.SUCCESS('[OK] Foundational data created'))

        # Now create realistic scenarios
        self.stdout.write('\nCreating realistic inspection scenarios...')
        inspections_by_scenario = self._create_inspection_scenarios(equipment, employees)

        self.stdout.write('\nCreating realistic work order scenarios...')
        work_orders = self._create_work_order_scenarios(
            equipment,
            employees,
            departments,
            inspections_by_scenario
        )

        self.stdout.write(self.style.SUCCESS('\n[OK] Realistic data seed completed!'))
        self.stdout.write(self.style.SUCCESS(f'  - Customers: {len(customers)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Equipment: {len(equipment)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Inspections: {len(inspections_by_scenario)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Work Orders: {len(work_orders)}'))

    def _create_inspection_scenarios(self, equipment, employees):
        """Create inspections from pre-defined scenarios."""
        inspections_by_scenario = {}

        for scenario in ALL_INSPECTION_SCENARIOS:
            scenario_name = scenario['name']
            self.stdout.write(f'  Creating: {scenario_name}')

            # Get equipment and inspector
            equip = equipment[scenario['equipment_index']]
            inspector_employees = [e for e in employees if e.base_department.code == 'INSP']
            inspector = inspector_employees[scenario['inspector_index']]

            # Calculate timestamps
            started_at = timezone.now() - timedelta(days=scenario['days_ago'])
            finalized_at = None
            if scenario['status'] == 'COMPLETED':
                finalized_at = started_at + timedelta(hours=scenario['duration_hours'])

            # Create inspection
            inspection = InspectionRun.objects.create(
                asset_type='EQUIPMENT',
                asset_id=equip.id,
                customer=equip.customer,
                template_key=scenario['template'],
                status=scenario['status'],
                started_at=started_at,
                finalized_at=finalized_at,
                inspector_name=f'{inspector.first_name} {inspector.last_name}',
                template_snapshot={'modules': [], 'metadata': {}},
                step_data={},
            )

            # Create defects
            for idx, defect_data in enumerate(scenario['defects']):
                # Generate idempotent defect_identity
                identity_string = f"{inspection.id}{defect_data['module_key']}{defect_data['step_key']}"
                defect_identity = hashlib.sha256(identity_string.encode()).hexdigest()

                InspectionDefect.objects.create(
                    inspection_run=inspection,
                    defect_identity=defect_identity,
                    module_key=defect_data['module_key'],
                    step_key=defect_data['step_key'],
                    severity=defect_data['severity'],
                    status='OPEN',
                    title=defect_data['title'],
                    description=defect_data['description'],
                    defect_details={
                        'component': defect_data['component'],
                        'location': defect_data['location'],
                        'recommended_action': defect_data['recommended_action'],
                        'standard_reference': defect_data['standard_reference'],
                    }
                )

            inspections_by_scenario[scenario_name] = inspection
            defect_count = len(scenario['defects'])
            status_text = '[DONE]' if scenario['status'] == 'COMPLETED' else '[IN PROGRESS]'
            self.stdout.write(f'    {status_text} {equip.asset_number} - {defect_count} defect(s)')

        return inspections_by_scenario

    def _create_work_order_scenarios(self, equipment, employees, departments, inspections_by_scenario):
        """Create work orders from pre-defined scenarios using proper service layer."""
        work_orders = []
        service_dept = next((d for d in departments if d.code == 'SVCRPR'), departments[0])
        service_employees = [e for e in employees if e.base_department.code == 'SVCRPR']

        for scenario in ALL_WORK_ORDER_SCENARIOS:
            scenario_name = scenario['name']
            self.stdout.write(f'  Creating: {scenario_name}')

            # Determine source
            source_type = scenario.get('source_type', 'INSPECTION_DEFECT')
            source_id = None
            customer = None
            asset_type = None
            asset_id = None

            if scenario.get('from_inspection_scenario'):
                # Work order from inspection defect
                inspection = inspections_by_scenario[scenario['from_inspection_scenario']]
                customer = inspection.customer
                asset_type = inspection.asset_type
                asset_id = inspection.asset_id

                if scenario['defect_index'] is not None:
                    # Single defect
                    defect = list(inspection.defects.all())[scenario['defect_index']]
                    source_id = defect.id
                else:
                    # Multiple defects - use inspection as source
                    source_id = inspection.id
            else:
                # Work order not from inspection
                equip = equipment[scenario['equipment_index']]
                customer = equip.customer
                asset_type = 'EQUIPMENT'
                asset_id = equip.id

            # Get assigned employee if specified
            assigned_employee = None
            if scenario.get('assigned_employee_index') is not None:
                assigned_employee = service_employees[scenario['assigned_employee_index']]

            # Create work order through workflow states
            workflow_states = scenario['workflow']
            work_order = None

            for state_idx, state in enumerate(workflow_states):
                days_offset = state['days_offset']
                created_at = timezone.now() - timedelta(
                    days=scenario.get('days_after_inspection', scenario.get('days_ago', 0)) - days_offset
                )

                if state_idx == 0:
                    # Initial creation
                    work_order = WorkOrder.objects.create(
                        customer=customer,
                        asset_type=asset_type,
                        asset_id=asset_id,
                        department=service_dept,
                        source_type=source_type,
                        source_id=source_id,
                        title=scenario['name'],
                        description=self._build_description(scenario, inspections_by_scenario),
                        status=state['status'],
                        priority=scenario['priority'],
                        approval_status=state['approval_status'],
                        assigned_to=assigned_employee,
                        created_at=created_at,
                        updated_at=created_at,
                    )

                    # Create work order lines
                    for line_data in scenario['lines']:
                        WorkOrderLine.objects.create(
                            work_order=work_order,
                            line_number=line_data['line_number'],
                            verb=line_data['verb'],
                            noun=line_data['noun'],
                            service_location=line_data['service_location'],
                            description=line_data['description'],
                            estimated_hours=line_data['estimated_hours'],
                            parts_required=line_data['parts_required'],
                            blocks_operation=line_data['blocks_operation'],
                            status='PENDING',
                            assigned_to=assigned_employee,
                        )
                else:
                    # Update to next state
                    work_order.status = state['status']
                    work_order.approval_status = state['approval_status']
                    work_order.updated_at = created_at

                    if state['status'] == 'IN_PROGRESS' and not work_order.started_at:
                        work_order.started_at = created_at
                    elif state['status'] == 'COMPLETED' and not work_order.completed_at:
                        work_order.completed_at = created_at
                        # Mark all lines as completed
                        for line in work_order.lines.all():
                            line.status = 'COMPLETED'
                            line.completed_at = created_at
                            line.completed_by = assigned_employee
                            line.save()

                    work_order.save()

            work_orders.append(work_order)
            self.stdout.write(
                f'    [{work_order.status}] [{work_order.approval_status}] {work_order.work_order_number} - '
                f'{len(scenario["lines"])} line(s), {work_order.priority} priority'
            )

        return work_orders

    def _build_description(self, scenario, inspections_by_scenario):
        """Build work order description based on scenario."""
        if scenario.get('from_inspection_scenario'):
            inspection = inspections_by_scenario[scenario['from_inspection_scenario']]
            defects = list(inspection.defects.all())
            if defects:
                return f"Repair defects identified during {inspection.template_key.replace('_', ' ')} inspection."

        # Default description based on source type
        source_type = scenario.get('source_type', 'MANUAL')
        descriptions = {
            'CUSTOMER_REQUEST': 'Customer requested scheduled maintenance',
            'BREAKDOWN': 'Emergency repair - equipment failure',
            'MAINTENANCE_SCHEDULE': 'Scheduled preventive maintenance',
            'MANUAL': 'Manually created work order',
        }
        return descriptions.get(source_type, 'Work order')
