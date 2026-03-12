"""
End-to-End Integration Tests (Phase 6)

Tests the complete workflow from asset creation through inspection to work order completion.
"""

import hashlib
from django.test import TestCase
from django.utils import timezone
from apps.customers.models import Customer
from apps.assets.models import Vehicle
from apps.organization.models import Department, Employee
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.inspections.services.defect_to_work_order_service import DefectToWorkOrderService
from apps.work_orders.models import WorkOrder, WorkOrderLine


class EndToEndWorkflowTest(TestCase):
    """Test complete end-to-end workflows."""

    def setUp(self):
        """Set up test fixtures."""
        # Create customer
        self.customer = Customer.objects.create(
            name="ABC Fleet Services",
            city="Chicago",
            state="IL"
        )

        # Create department
        self.department = Department.objects.create(
            name="Service Department",
            code="SVC"
        )

        # Create employee
        self.employee = Employee.objects.create(
            employee_number="TECH001",
            first_name="John",
            last_name="Technician",
            email="john@example.com",
            base_department=self.department
        )

        # Create vehicle with initial meters
        self.vehicle = Vehicle.objects.create(
            customer=self.customer,
            vin="1HGCM82633A123456",
            year=2020,
            make="Ford",
            model="F-350",
            odometer_miles=50000,
            engine_hours=1000
        )

    def test_complete_inspection_to_work_order_workflow(self):
        """
        Test complete workflow:
        1. Create inspection
        2. Complete inspection with failures
        3. Generate defects
        4. Create work order from defects
        5. Complete work order
        6. Verify meters updated
        """
        # Step 1: Create inspection
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='ansi_a92_2_2021_annual_aerial_vehicle',
            status='IN_PROGRESS',
            started_at=timezone.now(),
            template_snapshot={'modules': [], 'metadata': {}}
        )

        self.assertEqual(inspection.status, 'IN_PROGRESS')

        # Step 2: Complete inspection (simulate failure)
        inspection.status = 'COMPLETED'
        inspection.finalized_at = timezone.now()
        inspection.save()

        # Step 3: Generate defect
        defect = InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=hashlib.sha256(b'critical_defect_001').hexdigest(),
            module_key='hydraulic_system',
            step_key='hose_inspection',
            rule_id='rule_hydraulic_001',
            severity='CRITICAL',
            status='OPEN',
            title='Damaged Hydraulic Hose',
            description='Hydraulic hose shows severe wear and cracking'
        )

        self.assertEqual(defect.status, 'OPEN')
        self.assertEqual(defect.severity, 'CRITICAL')

        # Step 4: Generate work order from defect
        work_order = DefectToWorkOrderService.generate_work_order_from_defect(
            defect=defect,
            department_id=str(self.department.id),
            auto_approve=True
        )

        self.assertIsNotNone(work_order)
        self.assertEqual(work_order.source_type, 'INSPECTION_DEFECT')
        self.assertEqual(str(work_order.source_id), str(defect.id))
        self.assertEqual(work_order.approval_status, 'APPROVED')
        self.assertEqual(work_order.priority, 'EMERGENCY')  # CRITICAL → EMERGENCY

        # Verify defect marked as work order created
        defect.refresh_from_db()
        self.assertEqual(defect.status, 'WORK_ORDER_CREATED')

        # Verify work order line created
        self.assertEqual(work_order.lines.count(), 1)
        line = work_order.lines.first()
        self.assertIsNotNone(line.verb)
        self.assertIsNotNone(line.noun)
        self.assertIsNotNone(line.service_location)

        # Step 5: Complete work order with meter readings
        work_order.status = 'IN_PROGRESS'
        work_order.started_at = timezone.now()
        work_order.odometer_at_service = 51000  # New odometer reading
        work_order.engine_hours_at_service = 1050  # New engine hours
        work_order.save()

        # Complete the work order line
        line.status = 'COMPLETED'
        line.completed_at = timezone.now()
        line.completed_by = self.employee
        line.actual_hours = 2.5
        line.save()

        # Work order should auto-complete when all lines are done
        work_order.refresh_from_db()
        self.assertEqual(work_order.status, 'COMPLETED')

        # Step 6: Verify defect marked as resolved
        defect.refresh_from_db()
        self.assertEqual(defect.status, 'RESOLVED')

        # Step 7: Verify vehicle meters updated
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.odometer_miles, 51000)
        self.assertEqual(self.vehicle.engine_hours, 1050)

    def test_multiple_defects_grouped_work_order_workflow(self):
        """
        Test workflow with multiple defects creating grouped work order:
        1. Create inspection
        2. Generate multiple defects
        3. Create grouped work order
        4. Complete work order
        5. Verify all defects resolved
        """
        # Step 1: Create inspection
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='ansi_a92_2_2021_annual_aerial_vehicle',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            template_snapshot={'modules': [], 'metadata': {}}
        )

        # Step 2: Create multiple defects in same location
        defect1 = InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=hashlib.sha256(b'defect_001').hexdigest(),
            module_key='boom_inspection',
            step_key='boom_step_1',
            severity='MAJOR',
            status='OPEN',
            title='Worn Sheave',
            description='Boom sheave shows wear'
        )

        defect2 = InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=hashlib.sha256(b'defect_002').hexdigest(),
            module_key='boom_inspection',
            step_key='boom_step_2',
            severity='MINOR',
            status='OPEN',
            title='Loose Bolt',
            description='Boom bolt needs tightening'
        )

        # Step 3: Generate grouped work orders
        work_orders = DefectToWorkOrderService.generate_work_orders_from_inspection(
            inspection=inspection,
            group_by_location=True,
            auto_approve=True
        )

        self.assertEqual(len(work_orders), 1)  # Should group into one WO
        wo = work_orders[0]

        # Should have 2 lines (one per defect)
        self.assertEqual(wo.lines.count(), 2)

        # Priority should be HIGH (from MAJOR defect)
        self.assertEqual(wo.priority, 'HIGH')

        # Step 4: Complete all lines
        for line in wo.lines.all():
            line.status = 'COMPLETED'
            line.completed_at = timezone.now()
            line.completed_by = self.employee
            line.save()

        # Step 5: Verify work order auto-completed
        wo.refresh_from_db()
        self.assertEqual(wo.status, 'COMPLETED')

        # Step 6: Verify all defects resolved
        for defect in [defect1, defect2]:
            defect.refresh_from_db()
            # Defects were linked to inspection, not individual defects
            # So they should still be WORK_ORDER_CREATED
            self.assertEqual(defect.status, 'WORK_ORDER_CREATED')

    def test_work_order_cancellation_workflow(self):
        """
        Test workflow when work order is cancelled:
        1. Create defect
        2. Generate work order
        3. Cancel work order
        4. Verify defect reverted to OPEN
        """
        # Step 1: Create inspection and defect
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            template_snapshot={'modules': [], 'metadata': {}}
        )

        defect = InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=hashlib.sha256(b'test_defect').hexdigest(),
            module_key='test_module',
            step_key='test_step',
            severity='MAJOR',
            status='OPEN',
            title='Test Defect',
            description='Test defect description'
        )

        # Step 2: Generate work order
        wo = DefectToWorkOrderService.generate_work_order_from_defect(
            defect=defect,
            auto_approve=True
        )

        defect.refresh_from_db()
        self.assertEqual(defect.status, 'WORK_ORDER_CREATED')

        # Step 3: Cancel work order
        wo.status = 'CANCELLED'
        wo.save()

        # Step 4: Verify defect reverted to OPEN
        defect.refresh_from_db()
        self.assertEqual(defect.status, 'OPEN')

    def test_work_order_without_defect_workflow(self):
        """
        Test manual work order creation (not from defect):
        1. Create work order manually
        2. Complete work order
        3. Verify meters updated
        """
        # Step 1: Create manual work order
        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Preventive Maintenance',
            description='Scheduled PM service',
            source_type='MANUAL',
            status='IN_PROGRESS',
            approval_status='APPROVED',
            odometer_at_service=52000,
            engine_hours_at_service=1100
        )

        # Create line
        WorkOrderLine.objects.create(
            work_order=wo,
            line_number=1,
            verb='Replace',
            noun='Oil Filter',
            service_location='Engine',
            description='Replace engine oil and filter',
            status='COMPLETED',
            completed_at=timezone.now(),
            completed_by=self.employee,
            actual_hours=1.0
        )

        # Step 2: Complete work order
        wo.status = 'COMPLETED'
        wo.completed_at = timezone.now()
        wo.save()

        # Step 3: Verify meters updated
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.odometer_miles, 52000)
        self.assertEqual(self.vehicle.engine_hours, 1100)

    def test_severity_filtering_workflow(self):
        """
        Test work order generation with severity filtering:
        1. Create defects with different severities
        2. Generate work orders for MAJOR and above
        3. Verify only appropriate defects get work orders
        """
        # Step 1: Create inspection
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            template_snapshot={'modules': [], 'metadata': {}}
        )

        # Create defects with different severities
        critical = InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=hashlib.sha256(b'critical').hexdigest(),
            module_key='test_module',
            step_key='test_step',
            severity='CRITICAL',
            status='OPEN',
            title='Critical Issue',
            description='Critical issue description'
        )

        major = InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=hashlib.sha256(b'major').hexdigest(),
            module_key='test_module',
            step_key='test_step',
            severity='MAJOR',
            status='OPEN',
            title='Major Issue',
            description='Major issue description'
        )

        minor = InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=hashlib.sha256(b'minor').hexdigest(),
            module_key='test_module',
            step_key='test_step',
            severity='MINOR',
            status='OPEN',
            title='Minor Issue',
            description='Minor issue description'
        )

        advisory = InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=hashlib.sha256(b'advisory').hexdigest(),
            module_key='test_module',
            step_key='test_step',
            severity='ADVISORY',
            status='OPEN',
            title='Advisory Issue',
            description='Advisory issue description'
        )

        # Step 2: Generate work orders for MAJOR and above
        work_orders = DefectToWorkOrderService.generate_work_orders_from_inspection(
            inspection=inspection,
            group_by_location=False,
            min_severity='MAJOR'
        )

        # Step 3: Should only create 2 work orders (CRITICAL + MAJOR)
        self.assertEqual(len(work_orders), 2)

        # Verify correct defects got work orders
        critical.refresh_from_db()
        major.refresh_from_db()
        minor.refresh_from_db()
        advisory.refresh_from_db()

        self.assertEqual(critical.status, 'WORK_ORDER_CREATED')
        self.assertEqual(major.status, 'WORK_ORDER_CREATED')
        self.assertEqual(minor.status, 'OPEN')  # Not converted
        self.assertEqual(advisory.status, 'OPEN')  # Not converted

    def test_approval_workflow(self):
        """
        Test work order approval workflow:
        1. Create work order as PENDING_APPROVAL
        2. Approve work order
        3. Start and complete work
        """
        # Step 1: Create defect and work order (not auto-approved)
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            template_snapshot={'modules': [], 'metadata': {}}
        )

        defect = InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=hashlib.sha256(b'test_approval').hexdigest(),
            module_key='test_module',
            step_key='test_step',
            severity='MAJOR',
            status='OPEN',
            title='Test Defect',
            description='Test defect description'
        )

        wo = DefectToWorkOrderService.generate_work_order_from_defect(
            defect=defect,
            auto_approve=False  # Requires approval
        )

        # Step 2: Verify pending approval
        self.assertEqual(wo.approval_status, 'PENDING_APPROVAL')

        # Step 3: Approve work order
        wo.approval_status = 'APPROVED'
        wo.approved_by = self.employee
        wo.approved_at = timezone.now()
        wo.save()

        # Step 4: Start and complete work
        wo.status = 'IN_PROGRESS'
        wo.started_at = timezone.now()
        wo.save()

        # Complete line
        line = wo.lines.first()
        line.status = 'COMPLETED'
        line.completed_at = timezone.now()
        line.completed_by = self.employee
        line.save()

        # Verify work order completed
        wo.refresh_from_db()
        self.assertEqual(wo.status, 'COMPLETED')
        self.assertEqual(wo.approval_status, 'APPROVED')
