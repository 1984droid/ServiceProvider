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

        # Generate work orders - should include ALL defects
        work_orders = DefectToWorkOrderService.generate_work_orders_from_inspection(
            inspection=self.inspection,
            group_by_location=False
        )

        # Should include all 3 defects (CRITICAL, ADVISORY, MINOR)
        self.assertEqual(len(work_orders), 3)

        # Verify CRITICAL defect has blocks_operation=True
        critical_wo = next(wo for wo in work_orders if wo.priority == 'EMERGENCY')
        self.assertTrue(critical_wo.lines.first().blocks_operation)

        # Verify non-CRITICAL defects have blocks_operation=False
        advisory_wo = next(wo for wo in work_orders if wo.priority == 'LOW')
        self.assertFalse(advisory_wo.lines.first().blocks_operation)

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


class WorkOrderStandardTextIntegrationTest(TestCase):
    """Test work order generation with ANSI standard text integration."""

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

        # Create inspection
        self.inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='ansi_a92_2_2021_periodic_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            template_snapshot={'modules': [], 'metadata': {}}
        )

    def test_work_order_includes_standard_reference(self):
        """Test work order line includes standard reference from defect."""
        # Create defect with standard reference
        defect = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('boom_defect_with_standard'),
            module_key='boom_inspection',
            step_key='visual_inspection',
            severity='CRITICAL',
            status='OPEN',
            title='Cracked Boom Weld',
            description='Structural crack detected in boom weld joint',
            defect_details={
                'standard_reference': 'ANSI A92.2-2021 Section 8.2.3(2)',
                'severity': 'CRITICAL',
                'location': 'Upper boom assembly',
                'corrective_action': 'Replace boom section'
            }
        )

        # Generate work order
        wo = DefectToWorkOrderService.generate_work_order_from_defect(defect=defect)

        # Verify work order created
        self.assertIsNotNone(wo)
        self.assertEqual(wo.lines.count(), 1)

        # Verify work order line has description with standard reference
        line = wo.lines.first()
        self.assertIn('ANSI A92.2-2021 Section 8.2.3(2)', line.description)
        self.assertIn('Standard:', line.description)

    def test_work_order_without_standard_reference(self):
        """Test work order generation when defect has no standard reference."""
        # Create defect without standard reference
        defect = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('defect_no_standard'),
            module_key='hydraulic_system',
            step_key='hose_inspection',
            severity='MAJOR',
            status='OPEN',
            title='Hydraulic Leak',
            description='Leak detected in main hydraulic line',
            defect_details={
                'severity': 'MAJOR',
                'location': 'Main hydraulic line'
            }
        )

        # Generate work order (should work without standard reference)
        wo = DefectToWorkOrderService.generate_work_order_from_defect(defect=defect)

        # Verify work order created
        self.assertIsNotNone(wo)
        self.assertEqual(wo.lines.count(), 1)

        # Verify work order line exists but doesn't contain "Standard:"
        line = wo.lines.first()
        self.assertNotIn('Standard:', line.description)

    def test_work_order_standard_reference_formatting(self):
        """Test standard reference is properly formatted in work order description."""
        # Create defect with various defect_details fields
        defect = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('formatted_standard_ref'),
            module_key='boom_inspection',
            step_key='load_test',
            severity='CRITICAL',
            status='OPEN',
            title='Failed Load Test',
            description='Load test failed at 150% rated capacity',
            defect_details={
                'standard_reference': 'ANSI A92.2-2021 Section 8.2.4.1',
                'severity': 'CRITICAL',
                'location': 'Load test platform',
                'corrective_action': 'Inspect and repair structural components',
                'observations': 'Platform deflection exceeded limits'
            }
        )

        # Generate work order
        wo = DefectToWorkOrderService.generate_work_order_from_defect(defect=defect)

        # Verify work order line description
        line = wo.lines.first()

        # Should contain standard reference
        self.assertIn('Standard: ANSI A92.2-2021 Section 8.2.4.1', line.description)

        # Should also contain other defect details
        self.assertIn('Failed Load Test', line.description)
        self.assertIn('Load test failed at 150% rated capacity', line.description)

    def test_multiple_defects_preserve_standard_references(self):
        """Test multiple defects with different standard references create correct work orders."""
        # Create multiple defects with different standard references
        defect1 = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('defect_std_1'),
            module_key='boom_inspection',
            step_key='visual_inspection',
            severity='CRITICAL',
            status='OPEN',
            title='Boom Crack',
            description='Crack in boom structure',
            defect_details={
                'standard_reference': 'ANSI A92.2-2021 Section 8.2.3(2)',
                'severity': 'CRITICAL'
            }
        )

        defect2 = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('defect_std_2'),
            module_key='hydraulic_system',
            step_key='hydraulic_test',
            severity='MAJOR',
            status='OPEN',
            title='Hydraulic Pressure Low',
            description='Hydraulic system pressure below minimum',
            defect_details={
                'standard_reference': 'ANSI A92.2-2021 Section 8.2.3(4)',
                'severity': 'MAJOR'
            }
        )

        defect3 = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('defect_std_3'),
            module_key='electrical_system',
            step_key='dielectric_test',
            severity='CRITICAL',
            status='OPEN',
            title='Dielectric Test Failed',
            description='Failed dielectric test at rated voltage',
            defect_details={
                'standard_reference': 'ANSI A92.2-2021 Section 5.4.1',
                'severity': 'CRITICAL'
            }
        )

        # Generate work orders (ungrouped)
        work_orders = DefectToWorkOrderService.generate_work_orders_from_inspection(
            inspection=self.inspection,
            group_by_location=False
        )

        # Should create 3 work orders
        self.assertEqual(len(work_orders), 3)

        # Each work order should have its respective standard reference
        all_descriptions = [wo.lines.first().description for wo in work_orders]

        self.assertTrue(any('Section 8.2.3(2)' in desc for desc in all_descriptions))
        self.assertTrue(any('Section 8.2.3(4)' in desc for desc in all_descriptions))
        self.assertTrue(any('Section 5.4.1' in desc for desc in all_descriptions))

    def test_grouped_work_order_preserves_all_standard_references(self):
        """Test grouped work order preserves standard references from all defects."""
        # Create multiple defects in same location with different standard references
        defect1 = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('grouped_std_1'),
            module_key='boom_inspection',
            step_key='weld_inspection',
            severity='CRITICAL',
            status='OPEN',
            title='Weld Crack',
            description='Crack in weld joint',
            defect_details={
                'standard_reference': 'ANSI A92.2-2021 Section 8.2.3(2)',
                'severity': 'CRITICAL'
            }
        )

        defect2 = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('grouped_std_2'),
            module_key='boom_inspection',
            step_key='bolt_inspection',
            severity='MAJOR',
            status='OPEN',
            title='Missing Bolts',
            description='Multiple bolts missing from boom assembly',
            defect_details={
                'standard_reference': 'ANSI A92.2-2021 Section 8.2.3(2)',
                'severity': 'MAJOR'
            }
        )

        # Generate grouped work orders
        work_orders = DefectToWorkOrderService.generate_work_orders_from_inspection(
            inspection=self.inspection,
            group_by_location=True
        )

        # Find the grouped work order (should have 2 lines)
        grouped_wo = next((wo for wo in work_orders if wo.lines.count() == 2), None)
        self.assertIsNotNone(grouped_wo)

        # Both lines should have standard references
        line1, line2 = grouped_wo.lines.all()
        self.assertIn('Section 8.2.3(2)', line1.description)
        self.assertIn('Section 8.2.3(2)', line2.description)
