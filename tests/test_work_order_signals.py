"""
Tests for Work Order Signals (Phase 5)

Tests status synchronization between work orders and defects.
"""

from django.test import TestCase
from django.utils import timezone
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.work_orders.models import WorkOrder, WorkOrderLine
from apps.customers.models import Customer
from apps.assets.models import Vehicle
from apps.organization.models import Employee, Department


class WorkOrderSignalsTest(TestCase):
    """Test work order signal handlers."""

    def setUp(self):
        """Set up test fixtures."""
        # Create customer
        self.customer = Customer.objects.create(
            name="Test Customer",
            city="Chicago",
            state="IL"
        )

        # Create vehicle
        self.vehicle = Vehicle.objects.create(
            customer=self.customer,
            vin="1HGCM82633A123456",
            year=2020,
            make="Ford",
            model="F-350"
        )

        # Create department
        self.department = Department.objects.create(
            name="Service Department",
            code="SVC"
        )

        # Create employee
        self.employee = Employee.objects.create(
            employee_number="EMP001",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            base_department=self.department
        )

        # Create inspection
        self.inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            template_snapshot={'modules': [], 'metadata': {}}
        )

        # Create defect (with proper SHA256 hash)
        self.defect = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity='a' * 64,  # Valid 64-character SHA256 hash
            module_key='boom_inspection',
            step_key='test_step',
            severity='CRITICAL',
            status='OPEN',
            title='Test Defect',
            description='Test defect description'
        )

    def test_work_order_completion_resolves_defect(self):
        """Test completing work order marks defect as RESOLVED."""
        # Create work order from defect
        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Test Work Order',
            description='Test work order description',
            source_type='INSPECTION_DEFECT',
            source_id=self.defect.id,
            status='PENDING',
            approval_status='APPROVED'
        )

        # Create line
        line = WorkOrderLine.objects.create(
            work_order=wo,
            line_number=1,
            verb='Replace',
            noun='Component',
            service_location='General',
            status='PENDING'
        )

        # Mark defect as work order created
        self.defect.status = 'WORK_ORDER_CREATED'
        self.defect.save()

        # Complete work order
        wo.status = 'COMPLETED'
        wo.completed_at = timezone.now()
        wo.save()

        # Defect should be resolved
        self.defect.refresh_from_db()
        self.assertEqual(self.defect.status, 'RESOLVED')

    def test_work_order_cancellation_reopens_defect(self):
        """Test cancelling work order reverts defect to OPEN."""
        # Create work order from defect
        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Test Work Order',
            description='Test work order description',
            source_type='INSPECTION_DEFECT',
            source_id=self.defect.id,
            status='PENDING',
            approval_status='APPROVED'
        )

        # Mark defect as work order created
        self.defect.status = 'WORK_ORDER_CREATED'
        self.defect.save()

        # Cancel work order
        wo.status = 'CANCELLED'
        wo.save()

        # Defect should be reopened
        self.defect.refresh_from_db()
        self.assertEqual(self.defect.status, 'OPEN')

    def test_work_order_deletion_reopens_defect(self):
        """Test deleting work order reverts defect to OPEN."""
        # Create work order from defect
        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Test Work Order',
            description='Test work order description',
            source_type='INSPECTION_DEFECT',
            source_id=self.defect.id,
            status='PENDING',
            approval_status='APPROVED'
        )

        # Mark defect as work order created
        self.defect.status = 'WORK_ORDER_CREATED'
        self.defect.save()

        # Delete work order
        wo.delete()

        # Defect should be reopened
        self.defect.refresh_from_db()
        self.assertEqual(self.defect.status, 'OPEN')

    def test_work_order_completion_no_defect(self):
        """Test completing work order without defect source doesn't error."""
        # Create work order without defect source
        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Test Work Order',
            description='Test work order description',
            source_type='MANUAL',
            status='PENDING',
            approval_status='APPROVED'
        )

        # Complete work order - should not error
        wo.status = 'COMPLETED'
        wo.completed_at = timezone.now()
        wo.save()

        # No error should occur

    def test_all_lines_completed_autocompletes_work_order(self):
        """Test completing all lines auto-completes work order."""
        # Create work order
        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Test Work Order',
            description='Test work order description',
            status='IN_PROGRESS',
            approval_status='APPROVED'
        )

        # Create multiple lines
        line1 = WorkOrderLine.objects.create(
            work_order=wo,
            line_number=1,
            verb='Replace',
            noun='Component A',
            service_location='General',
            status='PENDING'
        )

        line2 = WorkOrderLine.objects.create(
            work_order=wo,
            line_number=2,
            verb='Inspect',
            noun='Component B',
            service_location='General',
            status='PENDING'
        )

        # Complete first line
        line1.status = 'COMPLETED'
        line1.completed_at = timezone.now()
        line1.completed_by = self.employee
        line1.save()

        # Work order should still be in progress
        wo.refresh_from_db()
        self.assertEqual(wo.status, 'IN_PROGRESS')

        # Complete second line
        line2.status = 'COMPLETED'
        line2.completed_at = timezone.now()
        line2.completed_by = self.employee
        line2.save()

        # Work order should auto-complete
        wo.refresh_from_db()
        self.assertEqual(wo.status, 'COMPLETED')
        self.assertIsNotNone(wo.completed_at)

    def test_line_completion_no_autocomplete_if_already_completed(self):
        """Test line completion doesn't trigger if work order already completed."""
        # Create completed work order
        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Test Work Order',
            description='Test work order description',
            status='COMPLETED',
            completed_at=timezone.now(),
            approval_status='APPROVED'
        )

        # Create line
        line = WorkOrderLine.objects.create(
            work_order=wo,
            line_number=1,
            verb='Replace',
            noun='Component',
            service_location='General',
            status='PENDING'
        )

        # Complete line
        line.status = 'COMPLETED'
        line.completed_at = timezone.now()
        line.completed_by = self.employee
        line.save()

        # Work order should remain completed
        wo.refresh_from_db()
        self.assertEqual(wo.status, 'COMPLETED')

    def test_signal_handles_nonexistent_defect(self):
        """Test signal handler gracefully handles deleted/nonexistent defect."""
        import uuid

        # Create work order with non-existent defect ID
        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Test Work Order',
            description='Test work order description',
            source_type='INSPECTION_DEFECT',
            source_id=uuid.uuid4(),  # Random UUID that doesn't exist
            status='PENDING',
            approval_status='APPROVED'
        )

        # Complete work order - should not error
        wo.status = 'COMPLETED'
        wo.completed_at = timezone.now()
        wo.save()

        # No error should occur

    def test_resolved_defect_not_reopened_twice(self):
        """Test already resolved defect status is not changed by work order completion."""
        # Create work order
        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Test Work Order',
            description='Test work order description',
            source_type='INSPECTION_DEFECT',
            source_id=self.defect.id,
            status='PENDING',
            approval_status='APPROVED'
        )

        # Manually resolve defect
        self.defect.status = 'RESOLVED'
        self.defect.save()

        # Complete work order
        wo.status = 'COMPLETED'
        wo.save()

        # Defect should remain resolved
        self.defect.refresh_from_db()
        self.assertEqual(self.defect.status, 'RESOLVED')
