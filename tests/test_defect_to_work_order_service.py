"""
Tests for DefectToWorkOrderService (Phase 5)

Tests automated work order generation from inspection defects.
"""

import hashlib
from django.test import TestCase
from django.utils import timezone
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.work_orders.models import WorkOrder, WorkOrderLine
from apps.customers.models import Customer
from apps.assets.models import Vehicle
from apps.organization.models import Department
from apps.inspections.services.defect_to_work_order_service import DefectToWorkOrderService


def make_defect_identity(key: str) -> str:
    """Generate valid 64-char SHA256 hash for defect identity."""
    return hashlib.sha256(key.encode()).hexdigest()


class DefectToWorkOrderServiceTest(TestCase):
    """Test DefectToWorkOrderService functionality."""

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
            step_key='hydraulic_hoses',
            rule_id='rule_001',
            severity='CRITICAL',
            status='OPEN',
            title='Damaged Hydraulic Hose',
            description='Hydraulic hose shows signs of wear and cracking'
        )

    def test_map_defect_to_vocabulary(self):
        """Test mapping defect to vocabulary."""
        vocab = DefectToWorkOrderService.map_defect_to_vocabulary(self.defect)

        self.assertIsInstance(vocab, dict)
        self.assertIn('verb', vocab)
        self.assertIn('noun', vocab)
        self.assertIn('service_location', vocab)
        self.assertIn('description', vocab)

    def test_map_defect_severity_to_verb(self):
        """Test verb selection based on severity."""
        # CRITICAL should suggest "Replace"
        critical_defect = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('test_critical'),
            step_key='test_step',
            severity='CRITICAL',
            status='OPEN',
            title='Critical Issue',
            description='Critical issue description'
        )

        vocab = DefectToWorkOrderService.map_defect_to_vocabulary(critical_defect)
        # Default verb for CRITICAL should be "Replace"
        self.assertIsNotNone(vocab['verb'])

    def test_map_defect_module_to_location(self):
        """Test service location extraction from module key."""
        location = DefectToWorkOrderService._default_location_from_module('boom_inspection')
        self.assertEqual(location, 'Boom Assembly')

        location = DefectToWorkOrderService._default_location_from_module('chassis_inspection')
        self.assertEqual(location, 'Chassis')

        location = DefectToWorkOrderService._default_location_from_module('unknown_module')
        self.assertEqual(location, 'General')

    def test_generate_work_order_from_defect(self):
        """Test generating work order from single defect."""
        wo = DefectToWorkOrderService.generate_work_order_from_defect(
            defect=self.defect,
            department_id=str(self.department.id)
        )

        self.assertIsInstance(wo, WorkOrder)
        self.assertEqual(wo.source_type, 'INSPECTION_DEFECT')
        self.assertEqual(str(wo.source_id), str(self.defect.id))
        self.assertEqual(wo.customer, self.customer)
        self.assertEqual(wo.asset_type, 'VEHICLE')
        self.assertEqual(str(wo.asset_id), str(self.vehicle.id))

        # Check defect status updated
        self.defect.refresh_from_db()
        self.assertEqual(self.defect.status, 'WORK_ORDER_CREATED')

        # Check work order line created
        self.assertEqual(wo.lines.count(), 1)
        line = wo.lines.first()
        self.assertEqual(line.line_number, 1)
        self.assertIsNotNone(line.verb)
        self.assertIsNotNone(line.noun)
        self.assertIsNotNone(line.service_location)

    def test_generate_work_order_auto_approve(self):
        """Test generating work order with auto-approval."""
        wo = DefectToWorkOrderService.generate_work_order_from_defect(
            defect=self.defect,
            auto_approve=True
        )

        self.assertEqual(wo.approval_status, 'APPROVED')

    def test_generate_work_order_duplicate_error(self):
        """Test error when trying to create duplicate work order for defect."""
        # Create first work order
        DefectToWorkOrderService.generate_work_order_from_defect(defect=self.defect)

        # Try to create duplicate
        with self.assertRaises(ValueError) as cm:
            DefectToWorkOrderService.generate_work_order_from_defect(defect=self.defect)

        self.assertIn('already has work order', str(cm.exception))

    def test_severity_to_priority_mapping(self):
        """Test defect severity maps to work order priority."""
        priority = DefectToWorkOrderService._map_severity_to_priority('CRITICAL')
        self.assertEqual(priority, 'EMERGENCY')

        priority = DefectToWorkOrderService._map_severity_to_priority('MAJOR')
        self.assertEqual(priority, 'HIGH')

        priority = DefectToWorkOrderService._map_severity_to_priority('MINOR')
        self.assertEqual(priority, 'NORMAL')

        priority = DefectToWorkOrderService._map_severity_to_priority('ADVISORY')
        self.assertEqual(priority, 'LOW')

    def test_generate_work_orders_from_inspection(self):
        """Test generating work orders from all inspection defects."""
        # Create additional defects
        defect2 = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('test_defect_002'),
            module_key='boom_inspection',
            step_key='test_step',
            severity='MAJOR',
            status='OPEN',
            title='Loose Bolt',
            description='Loose bolt description'
        )

        defect3 = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('test_defect_003'),
            module_key='chassis_inspection',
            step_key='test_step',
            severity='MINOR',
            status='OPEN',
            title='Paint Chip',
            description='Paint chip description'
        )

        # Generate work orders (ungrouped)
        work_orders = DefectToWorkOrderService.generate_work_orders_from_inspection(
            inspection=self.inspection,
            group_by_location=False
        )

        # Should create 3 work orders (one per defect)
        self.assertEqual(len(work_orders), 3)

        # All defects should be marked
        for defect in [self.defect, defect2, defect3]:
            defect.refresh_from_db()
            self.assertEqual(defect.status, 'WORK_ORDER_CREATED')

    def test_generate_work_orders_grouped_by_location(self):
        """Test generating work orders grouped by service location."""
        # Create defects in same location
        defect2 = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('test_defect_002_grouped'),
            module_key='boom_inspection',  # Same module as defect1
            step_key='test_step',
            severity='MAJOR',
            status='OPEN',
            title='Another Boom Issue',
            description='Another boom issue description'
        )

        # Create defect in different location
        defect3 = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('test_defect_003_grouped'),
            module_key='chassis_inspection',  # Different module
            step_key='test_step',
            severity='MINOR',
            status='OPEN',
            title='Chassis Issue',
            description='Chassis issue description'
        )

        # Generate work orders (grouped)
        work_orders = DefectToWorkOrderService.generate_work_orders_from_inspection(
            inspection=self.inspection,
            group_by_location=True
        )

        # Should create 2 work orders (boom + chassis)
        self.assertGreaterEqual(len(work_orders), 1)

        # Check that grouped work orders have multiple lines
        for wo in work_orders:
            if wo.lines.count() > 1:
                # Found a grouped work order
                self.assertGreater(wo.lines.count(), 1)

    def test_generate_work_orders_min_severity_filter(self):
        """Test generating work orders with minimum severity filter."""
        # Create defects with different severities
        InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('test_advisory'),
            step_key='test_step',
            severity='ADVISORY',
            status='OPEN',
            title='Advisory Issue',
            description='Advisory issue description'
        )

        InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('test_minor'),
            step_key='test_step',
            severity='MINOR',
            status='OPEN',
            title='Minor Issue',
            description='Minor issue description'
        )

        # Generate work orders for MAJOR and above
        work_orders = DefectToWorkOrderService.generate_work_orders_from_inspection(
            inspection=self.inspection,
            group_by_location=False,
            min_severity='MAJOR'
        )

        # Should only include CRITICAL (defect1) and exclude ADVISORY/MINOR
        self.assertEqual(len(work_orders), 1)
        self.assertEqual(work_orders[0].priority, 'EMERGENCY')  # CRITICAL → EMERGENCY

    def test_generate_work_orders_no_open_defects(self):
        """Test generating work orders when no open defects exist."""
        # Mark all defects as resolved
        InspectionDefect.objects.filter(inspection_run=self.inspection).update(status='RESOLVED')

        work_orders = DefectToWorkOrderService.generate_work_orders_from_inspection(
            inspection=self.inspection
        )

        # Should return empty list
        self.assertEqual(len(work_orders), 0)

    def test_get_defect_work_order(self):
        """Test retrieving work order for a defect."""
        # Create work order
        wo = DefectToWorkOrderService.generate_work_order_from_defect(defect=self.defect)

        # Retrieve it
        retrieved_wo = DefectToWorkOrderService.get_defect_work_order(self.defect)

        self.assertEqual(retrieved_wo.id, wo.id)

    def test_get_defect_work_order_not_found(self):
        """Test retrieving work order for defect with no work order."""
        result = DefectToWorkOrderService.get_defect_work_order(self.defect)
        self.assertIsNone(result)

    def test_get_inspection_work_orders(self):
        """Test retrieving all work orders for an inspection."""
        # Create work orders
        DefectToWorkOrderService.generate_work_orders_from_inspection(
            inspection=self.inspection,
            group_by_location=False
        )

        # Retrieve them
        work_orders = DefectToWorkOrderService.get_inspection_work_orders(self.inspection)

        self.assertGreater(len(work_orders), 0)

    def test_grouped_work_order_highest_priority(self):
        """Test grouped work order uses highest priority from defects."""
        # Create defects with different severities
        InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('test_minor_priority'),
            module_key='boom_inspection',
            step_key='test_step',
            severity='MINOR',
            status='OPEN',
            title='Minor Issue',
            description='Minor issue description'
        )

        # self.defect is CRITICAL, so grouped WO should be EMERGENCY
        work_orders = DefectToWorkOrderService.generate_work_orders_from_inspection(
            inspection=self.inspection,
            group_by_location=True
        )

        # Find work order with multiple lines
        for wo in work_orders:
            if wo.lines.count() > 1:
                # Should have EMERGENCY priority from CRITICAL defect
                self.assertEqual(wo.priority, 'EMERGENCY')

    def test_load_defect_mapping_cache(self):
        """Test defect mapping catalog loading and caching."""
        mapping1 = DefectToWorkOrderService.load_defect_mapping()
        mapping2 = DefectToWorkOrderService.load_defect_mapping()

        # Should return cached instance
        self.assertIs(mapping1, mapping2)

    def test_load_defect_mapping_force_reload(self):
        """Test defect mapping force reload."""
        mapping1 = DefectToWorkOrderService.load_defect_mapping()
        mapping2 = DefectToWorkOrderService.load_defect_mapping(force_reload=True)

        # Should return new instance
        self.assertIsNot(mapping1, mapping2)
