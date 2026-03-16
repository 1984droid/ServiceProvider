"""
Unit tests for Work Order models.

Tests follow the no-hardcode rule: all test data comes from tests.config.
"""

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta, date

from apps.work_orders.models import WorkOrder, WorkOrderDefect
from apps.inspections.models import InspectionDefect
from tests.factories import (
    WorkOrderFactory,
    WorkOrderDefectFactory,
    InspectionRunFactory,
    InspectionDefectFactory,
    CustomerFactory,
    VehicleFactory,
    EquipmentFactory,
)
from tests.config import get_test_data, VALID_CHOICES


# ============================================================================
# WorkOrder Model Tests
# ============================================================================

@pytest.mark.django_db
class TestWorkOrderModel:
    """Test WorkOrder model."""

    def test_create_work_order_default(self):
        """Test creating work order with default factory."""
        work_order = WorkOrderFactory()

        assert work_order.id is not None
        assert work_order.work_order_number is not None
        assert work_order.work_order_number.startswith('WO-')
        assert work_order.customer is not None
        assert work_order.asset_type in VALID_CHOICES['asset_types']
        assert work_order.asset_id is not None
        assert work_order.status in VALID_CHOICES['work_order_statuses']
        assert work_order.priority in VALID_CHOICES['work_order_priorities']
        assert work_order.source_type in VALID_CHOICES['work_order_sources']
        assert work_order.description

    def test_work_order_number_auto_generation(self):
        """Test work order number is auto-generated."""
        work_order = WorkOrderFactory()

        assert work_order.work_order_number is not None
        # Format: WO-YYYY-#####
        parts = work_order.work_order_number.split('-')
        assert len(parts) == 3
        assert parts[0] == 'WO'
        assert len(parts[1]) == 4  # Year
        assert len(parts[2]) == 5  # Number

    def test_work_order_number_sequential(self):
        """Test work order numbers are sequential."""
        wo1 = WorkOrderFactory()
        wo2 = WorkOrderFactory()

        # Extract numbers
        num1 = int(wo1.work_order_number.split('-')[-1])
        num2 = int(wo2.work_order_number.split('-')[-1])

        assert num2 == num1 + 1

    def test_create_work_order_for_vehicle(self):
        """Test creating work order for a vehicle."""
        customer = CustomerFactory()
        vehicle = VehicleFactory(customer=customer)
        work_order = WorkOrderFactory.for_vehicle(vehicle=vehicle)

        assert work_order.asset_type == 'VEHICLE'
        assert work_order.asset_id == vehicle.id
        assert work_order.customer == vehicle.customer

    def test_create_work_order_for_equipment(self):
        """Test creating work order for equipment."""
        customer = CustomerFactory()
        equipment = EquipmentFactory(customer=customer)
        work_order = WorkOrderFactory.for_equipment(equipment=equipment)

        assert work_order.asset_type == 'EQUIPMENT'
        assert work_order.asset_id == equipment.id
        assert work_order.customer == equipment.customer

    def test_create_work_order_from_inspection(self):
        """Test creating work order from inspection."""
        inspection = InspectionRunFactory()
        work_order = WorkOrderFactory.from_inspection(inspection_run=inspection)

        assert work_order.source_type == 'INSPECTION_DEFECT'
        assert work_order.source_id == inspection.id
        assert work_order.customer == inspection.customer
        assert work_order.asset_type == inspection.asset_type
        assert work_order.asset_id == inspection.asset_id

    def test_work_order_asset_property_vehicle(self):
        """Test asset property returns correct vehicle instance."""
        customer = CustomerFactory()
        vehicle = VehicleFactory(customer=customer)
        work_order = WorkOrderFactory.for_vehicle(vehicle=vehicle)

        asset = work_order.asset
        assert asset.id == vehicle.id
        assert asset.vin == vehicle.vin

    def test_work_order_asset_property_equipment(self):
        """Test asset property returns correct equipment instance."""
        customer = CustomerFactory()
        equipment = EquipmentFactory(customer=customer)
        work_order = WorkOrderFactory.for_equipment(equipment=equipment)

        asset = work_order.asset
        assert asset.id == equipment.id
        assert asset.serial_number == equipment.serial_number

    def test_work_order_defect_count_property(self):
        """Test defect_count property."""
        work_order = WorkOrderFactory()
        assert work_order.defect_count == 0

        WorkOrderDefectFactory.create_for_work_order(work_order=work_order)
        assert work_order.defect_count == 1

        WorkOrderDefectFactory.create_for_work_order(work_order=work_order)
        assert work_order.defect_count == 2

    def test_work_order_is_completed_property(self):
        """Test is_completed property."""
        work_order = WorkOrderFactory(status='DRAFT')
        assert work_order.is_completed is False

        work_order.status = 'COMPLETED'
        assert work_order.is_completed is True

    def test_work_order_is_cancelled_property(self):
        """Test is_cancelled property."""
        work_order = WorkOrderFactory(status='DRAFT')
        assert work_order.is_cancelled is False

        work_order.status = 'CANCELLED'
        assert work_order.is_cancelled is True

    def test_work_order_status_choices(self):
        """Test all valid work order statuses."""
        for status in VALID_CHOICES['work_order_statuses']:
            work_order = WorkOrderFactory(status=status)
            assert work_order.status == status

    def test_work_order_priority_choices(self):
        """Test all valid work order priorities."""
        for priority in VALID_CHOICES['work_order_priorities']:
            work_order = WorkOrderFactory(priority=priority)
            assert work_order.priority == priority

    def test_work_order_source_choices(self):
        """Test all valid work order sources."""
        for source in VALID_CHOICES['work_order_sources']:
            work_order = WorkOrderFactory(source_type=source)
            assert work_order.source_type == source

    def test_work_order_invalid_status(self):
        """Test invalid status raises error."""
        with pytest.raises(ValidationError):
            work_order = WorkOrderFactory.build(status='INVALID')
            work_order.full_clean()

    def test_work_order_invalid_priority(self):
        """Test invalid priority raises error."""
        with pytest.raises(ValidationError):
            work_order = WorkOrderFactory.build(priority='INVALID')
            work_order.full_clean()

    def test_work_order_invalid_source(self):
        """Test invalid source raises error."""
        with pytest.raises(ValidationError):
            work_order = WorkOrderFactory.build(source='INVALID')
            work_order.full_clean()

    def test_work_order_asset_customer_mismatch(self):
        """Test validation fails when asset customer doesn't match."""
        customer1 = CustomerFactory()
        customer2 = CustomerFactory()
        equipment = EquipmentFactory(customer=customer1)

        with pytest.raises(ValidationError) as exc_info:
            work_order = WorkOrderFactory.build(
                customer=customer2,
                asset_type='EQUIPMENT',
                asset_id=equipment.id
            )
            work_order.full_clean()

        assert 'customer' in str(exc_info.value)

    def test_work_order_source_inspection_must_match_asset(self):
        """Test source inspection must be for same asset."""
        inspection = InspectionRunFactory()
        different_equipment = EquipmentFactory()

        with pytest.raises(ValidationError) as exc_info:
            work_order = WorkOrderFactory.build(
                source_type='INSPECTION_DEFECT',
                source_id=inspection.id,
                asset_type='EQUIPMENT',
                asset_id=different_equipment.id,
                customer=different_equipment.customer
            )
            work_order.full_clean()

        assert 'source_id' in str(exc_info.value)

    def test_work_order_cannot_reopen_completed(self):
        """Test cannot change status from COMPLETED back to other statuses."""
        work_order = WorkOrderFactory(status='COMPLETED')

        with pytest.raises(ValidationError) as exc_info:
            work_order.status = 'IN_PROGRESS'
            work_order.full_clean()

        assert 'status' in str(exc_info.value)
        assert 'reopen' in str(exc_info.value).lower()

    def test_work_order_cannot_reopen_cancelled(self):
        """Test cannot change status from CANCELLED back to other statuses."""
        work_order = WorkOrderFactory(status='CANCELLED')

        with pytest.raises(ValidationError) as exc_info:
            work_order.status = 'IN_PROGRESS'
            work_order.full_clean()

        assert 'status' in str(exc_info.value)

    def test_work_order_completed_before_started_invalid(self):
        """Test completed_at cannot be before started_at."""
        started = timezone.now()
        completed = started - timedelta(hours=1)

        with pytest.raises(ValidationError) as exc_info:
            WorkOrderFactory(
                started_at=started,
                completed_at=completed
            )

        assert 'completed_at' in str(exc_info.value)

    def test_work_order_scheduled_date_cannot_be_past(self):
        """Test scheduled_date cannot be in the past for DRAFT status."""
        past_date = date.today() - timedelta(days=1)

        with pytest.raises(ValidationError) as exc_info:
            WorkOrderFactory(
                status='DRAFT',
                scheduled_date=past_date
            )

        assert 'scheduled_date' in str(exc_info.value)

    def test_work_order_scheduled_variant(self):
        """Test creating scheduled work order."""
        work_order = WorkOrderFactory.scheduled()

        assert work_order.status == 'PENDING'
        assert work_order.scheduled_date is not None

    def test_work_order_completed_variant(self):
        """Test creating completed work order."""
        work_order = WorkOrderFactory.completed()

        assert work_order.status == 'COMPLETED'
        assert work_order.started_at is not None
        assert work_order.completed_at is not None
        assert work_order.completed_at > work_order.started_at

    def test_work_order_customer_request_variant(self):
        """Test creating customer request work order."""
        work_order = WorkOrderFactory.customer_request()

        assert work_order.source_type == 'CUSTOMER_REQUEST'
        assert work_order.source_id is None

    def test_work_order_str_representation(self):
        """Test string representation."""
        work_order = WorkOrderFactory()
        str_repr = str(work_order)

        assert work_order.work_order_number in str_repr
        assert work_order.status in str_repr

    def test_work_order_ordering(self):
        """Test default ordering by created_at descending."""
        import time
        wo1 = WorkOrderFactory()
        time.sleep(0.01)
        wo2 = WorkOrderFactory()

        work_orders = list(WorkOrder.objects.filter(
            id__in=[wo1.id, wo2.id]
        ))

        # Most recent first
        assert work_orders[0] == wo2
        assert work_orders[1] == wo1


# ============================================================================
# WorkOrderDefect Model Tests
# ============================================================================

@pytest.mark.django_db
class TestWorkOrderDefectModel:
    """Test WorkOrderDefect junction model."""

    def test_create_work_order_defect(self):
        """Test creating work order defect link."""
        link = WorkOrderDefectFactory.create_for_work_order()

        assert link.work_order is not None
        assert link.defect is not None
        assert link.linked_at is not None

    def test_work_order_defect_unique_constraint(self):
        """Test cannot link same defect to same work order twice."""
        # Create first link with matching work_order and defect
        link = WorkOrderDefectFactory.create_for_work_order()
        work_order = link.work_order
        defect = link.defect

        # Try to create duplicate
        with pytest.raises(Exception):  # IntegrityError for unique constraint
            WorkOrderDefectFactory.create_for_work_order(work_order=work_order, defect=defect)

    def test_work_order_defect_same_customer(self):
        """Test work order and defect must belong to same customer."""
        customer1 = CustomerFactory()
        customer2 = CustomerFactory()

        inspection = InspectionRunFactory(customer=customer1)
        defect = InspectionDefectFactory(inspection_run=inspection)

        work_order = WorkOrderFactory(customer=customer2)

        with pytest.raises(ValidationError) as exc_info:
            link = WorkOrderDefectFactory.build(
                work_order=work_order,
                defect=defect
            )
            link.full_clean()

        assert 'customer' in str(exc_info.value)

    def test_work_order_defect_same_asset(self):
        """Test work order and defect must be for same asset."""
        customer = CustomerFactory()
        equipment1 = EquipmentFactory(customer=customer)
        equipment2 = EquipmentFactory(customer=customer)

        inspection = InspectionRunFactory.for_equipment(equipment=equipment1)
        defect = InspectionDefectFactory(inspection_run=inspection)

        work_order = WorkOrderFactory.for_equipment(equipment=equipment2)

        with pytest.raises(ValidationError) as exc_info:
            link = WorkOrderDefectFactory.build(
                work_order=work_order,
                defect=defect
            )
            link.full_clean()

        assert 'asset' in str(exc_info.value)

    def test_work_order_defect_multiple_defects_one_work_order(self):
        """Test one work order can address multiple defects."""
        work_order = WorkOrderFactory()
        defect1 = InspectionDefectFactory(
            inspection_run__customer=work_order.customer,
            inspection_run__asset_type=work_order.asset_type,
            inspection_run__asset_id=work_order.asset_id
        )
        defect2 = InspectionDefectFactory(
            inspection_run__customer=work_order.customer,
            inspection_run__asset_type=work_order.asset_type,
            inspection_run__asset_id=work_order.asset_id
        )

        link1 = WorkOrderDefectFactory(work_order=work_order, defect=defect1)
        link2 = WorkOrderDefectFactory(work_order=work_order, defect=defect2)

        assert work_order.defect_links.count() == 2

    def test_work_order_defect_multiple_work_orders_one_defect(self):
        """Test one defect can be addressed by multiple work orders."""
        inspection = InspectionRunFactory()
        defect = InspectionDefectFactory(inspection_run=inspection)

        # Multiple work orders for the same defect (e.g., parts order, then installation)
        work_order1 = WorkOrderFactory(
            customer=inspection.customer,
            asset_type=inspection.asset_type,
            asset_id=inspection.asset_id
        )
        work_order2 = WorkOrderFactory(
            customer=inspection.customer,
            asset_type=inspection.asset_type,
            asset_id=inspection.asset_id
        )

        link1 = WorkOrderDefectFactory(work_order=work_order1, defect=defect)
        link2 = WorkOrderDefectFactory(work_order=work_order2, defect=defect)

        assert defect.work_order_links.count() == 2

    def test_work_order_defect_cascade_delete_with_work_order(self):
        """Test links are deleted when work order is deleted."""
        work_order = WorkOrderFactory()
        link = WorkOrderDefectFactory.create_for_work_order(work_order=work_order)

        link_id = link.id
        work_order.delete()

        assert not WorkOrderDefect.objects.filter(id=link_id).exists()

    def test_work_order_defect_cascade_delete_with_defect(self):
        """Test links are deleted when defect is deleted."""
        defect = InspectionDefectFactory()
        link = WorkOrderDefectFactory.create_for_work_order(defect=defect)

        link_id = link.id
        defect.delete()

        assert not WorkOrderDefect.objects.filter(id=link_id).exists()

    def test_work_order_defect_str_representation(self):
        """Test string representation."""
        link = WorkOrderDefectFactory.create_for_work_order()
        str_repr = str(link)

        assert link.work_order.work_order_number in str_repr
        # Title is truncated to 50 chars in __str__
        assert link.defect.title[:50] in str_repr

    def test_work_order_defect_linked_at_auto_set(self):
        """Test linked_at is automatically set on creation."""
        before = timezone.now()
        link = WorkOrderDefectFactory.create_for_work_order()
        after = timezone.now()

        assert link.linked_at is not None
        assert before <= link.linked_at <= after


# ============================================================================
# Note: Department and employee M2M assignment tests removed
# Work orders now use single department FK and WorkOrderLine.assigned_to
# ============================================================================
