"""
Tests for Work Order Meter Updates (Phase 6)

Tests that completing work orders updates asset meters correctly.
"""

from django.test import TestCase
from django.utils import timezone
from apps.work_orders.models import WorkOrder
from apps.customers.models import Customer
from apps.assets.models import Vehicle, Equipment


class WorkOrderMeterUpdateTest(TestCase):
    """Test work order meter update functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create customer
        self.customer = Customer.objects.create(
            name="Test Customer",
            city="Chicago",
            state="IL"
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

        # Create equipment with initial meters
        self.equipment = Equipment.objects.create(
            customer=self.customer,
            serial_number="EQUIP-12345",
            equipment_type="AERIAL_LIFT",
            manufacturer="JLG",
            model="600AJ",
            engine_hours=500
        )

    def test_complete_vehicle_work_order_updates_odometer(self):
        """Test completing work order updates vehicle odometer."""
        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Oil Change',
            description='Regular oil change',
            status='IN_PROGRESS',
            odometer_at_service=51000,  # New reading
            approval_status='APPROVED'
        )

        # Complete work order
        wo.status = 'COMPLETED'
        wo.completed_at = timezone.now()
        wo.save()

        # Refresh vehicle
        self.vehicle.refresh_from_db()

        # Odometer should be updated
        self.assertEqual(self.vehicle.odometer_miles, 51000)

    def test_complete_vehicle_work_order_updates_engine_hours(self):
        """Test completing work order updates vehicle engine hours."""
        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Maintenance',
            description='Regular maintenance',
            status='IN_PROGRESS',
            engine_hours_at_service=1100,  # New reading
            approval_status='APPROVED'
        )

        # Complete work order
        wo.status = 'COMPLETED'
        wo.completed_at = timezone.now()
        wo.save()

        # Refresh vehicle
        self.vehicle.refresh_from_db()

        # Engine hours should be updated
        self.assertEqual(self.vehicle.engine_hours, 1100)

    def test_complete_vehicle_work_order_updates_both_meters(self):
        """Test completing work order updates both vehicle meters."""
        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Full Service',
            description='Complete service',
            status='IN_PROGRESS',
            odometer_at_service=52000,
            engine_hours_at_service=1150,
            approval_status='APPROVED'
        )

        # Complete work order
        wo.status = 'COMPLETED'
        wo.completed_at = timezone.now()
        wo.save()

        # Refresh vehicle
        self.vehicle.refresh_from_db()

        # Both meters should be updated
        self.assertEqual(self.vehicle.odometer_miles, 52000)
        self.assertEqual(self.vehicle.engine_hours, 1150)

    def test_complete_equipment_work_order_updates_engine_hours(self):
        """Test completing work order updates equipment engine hours."""
        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='EQUIPMENT',
            asset_id=self.equipment.id,
            title='Hydraulic Service',
            description='Hydraulic system service',
            status='IN_PROGRESS',
            engine_hours_at_service=600,  # New reading
            approval_status='APPROVED'
        )

        # Complete work order
        wo.status = 'COMPLETED'
        wo.completed_at = timezone.now()
        wo.save()

        # Refresh equipment
        self.equipment.refresh_from_db()

        # Engine hours should be updated
        self.assertEqual(self.equipment.engine_hours, 600)

    def test_meter_not_updated_if_lower_than_current(self):
        """Test meters not rolled back if new reading is lower."""
        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Service',
            description='Service work',
            status='IN_PROGRESS',
            odometer_at_service=40000,  # Lower than current 50000
            approval_status='APPROVED'
        )

        # Complete work order
        wo.status = 'COMPLETED'
        wo.completed_at = timezone.now()
        wo.save()

        # Refresh vehicle
        self.vehicle.refresh_from_db()

        # Odometer should NOT be rolled back
        self.assertEqual(self.vehicle.odometer_miles, 50000)

    def test_meter_updated_from_null(self):
        """Test meter updated when asset meter is null."""
        # Create vehicle with null meters
        vehicle2 = Vehicle.objects.create(
            customer=self.customer,
            vin="2HGCM82633A654321",
            year=2021,
            make="Chevy",
            model="Silverado",
            odometer_miles=None,
            engine_hours=None
        )

        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=vehicle2.id,
            title='First Service',
            description='Initial service',
            status='IN_PROGRESS',
            odometer_at_service=100,
            engine_hours_at_service=10,
            approval_status='APPROVED'
        )

        # Complete work order
        wo.status = 'COMPLETED'
        wo.completed_at = timezone.now()
        wo.save()

        # Refresh vehicle
        vehicle2.refresh_from_db()

        # Meters should be set
        self.assertEqual(vehicle2.odometer_miles, 100)
        self.assertEqual(vehicle2.engine_hours, 10)

    def test_meter_not_updated_if_not_provided(self):
        """Test meters not updated if not provided in work order."""
        initial_odometer = self.vehicle.odometer_miles
        initial_hours = self.vehicle.engine_hours

        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Quick Check',
            description='Quick inspection',
            status='IN_PROGRESS',
            # No meters provided
            approval_status='APPROVED'
        )

        # Complete work order
        wo.status = 'COMPLETED'
        wo.completed_at = timezone.now()
        wo.save()

        # Refresh vehicle
        self.vehicle.refresh_from_db()

        # Meters should remain unchanged
        self.assertEqual(self.vehicle.odometer_miles, initial_odometer)
        self.assertEqual(self.vehicle.engine_hours, initial_hours)

    def test_meter_not_updated_if_work_order_not_completed(self):
        """Test meters not updated for non-completed work orders."""
        initial_odometer = self.vehicle.odometer_miles

        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Service',
            description='Service work',
            status='IN_PROGRESS',
            odometer_at_service=55000,
            approval_status='APPROVED'
        )

        # Don't complete - just save
        wo.save()

        # Refresh vehicle
        self.vehicle.refresh_from_db()

        # Odometer should NOT be updated
        self.assertEqual(self.vehicle.odometer_miles, initial_odometer)

    def test_meter_update_idempotent(self):
        """Test meter update can be called multiple times safely."""
        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            title='Service',
            description='Service work',
            status='COMPLETED',
            completed_at=timezone.now(),
            odometer_at_service=53000,
            approval_status='APPROVED'
        )

        # Call update multiple times
        wo.update_asset_meters()
        wo.update_asset_meters()
        wo.update_asset_meters()

        # Refresh vehicle
        self.vehicle.refresh_from_db()

        # Should only update once
        self.assertEqual(self.vehicle.odometer_miles, 53000)

    def test_meter_update_handles_missing_asset(self):
        """Test meter update handles missing asset gracefully."""
        import uuid

        wo = WorkOrder.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=uuid.uuid4(),  # Non-existent asset
            title='Service',
            description='Service work',
            status='COMPLETED',
            completed_at=timezone.now(),
            odometer_at_service=60000,
            approval_status='APPROVED'
        )

        # Should not raise exception
        wo.update_asset_meters()
