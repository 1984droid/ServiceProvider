"""
Unit tests for Inspection models.

Tests follow the no-hardcode rule: all test data comes from tests.config.
"""

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from apps.inspections.models import InspectionRun, InspectionDefect
from tests.factories import (
    InspectionRunFactory,
    InspectionDefectFactory,
    CustomerFactory,
    VehicleFactory,
    EquipmentFactory,
)
from tests.config import get_test_data, VALID_CHOICES


# ============================================================================
# InspectionRun Model Tests
# ============================================================================

@pytest.mark.django_db
class TestInspectionRunModel:
    """Test InspectionRun model."""

    def test_create_inspection_run_default(self):
        """Test creating inspection run with default factory."""
        inspection = InspectionRunFactory()

        assert inspection.id is not None
        assert inspection.customer is not None
        assert inspection.asset_type in VALID_CHOICES['asset_types']
        assert inspection.asset_id is not None
        assert inspection.template_key == get_test_data('inspection_run', 'default')['template_key']
        assert inspection.status in VALID_CHOICES['inspection_statuses']
        assert inspection.started_at is not None
        assert inspection.template_snapshot is not None
        assert isinstance(inspection.step_data, dict)

    def test_create_inspection_for_vehicle(self):
        """Test creating inspection run for a vehicle."""
        customer = CustomerFactory()
        vehicle = VehicleFactory(customer=customer)
        inspection = InspectionRunFactory.for_vehicle(vehicle=vehicle)

        assert inspection.asset_type == 'VEHICLE'
        assert inspection.asset_id == vehicle.id
        assert inspection.customer == vehicle.customer

    def test_create_inspection_for_equipment(self):
        """Test creating inspection run for equipment."""
        customer = CustomerFactory()
        equipment = EquipmentFactory(customer=customer)
        inspection = InspectionRunFactory.for_equipment(equipment=equipment)

        assert inspection.asset_type == 'EQUIPMENT'
        assert inspection.asset_id == equipment.id
        assert inspection.customer == equipment.customer

    def test_inspection_run_asset_property_vehicle(self):
        """Test asset property returns correct vehicle instance."""
        customer = CustomerFactory()
        vehicle = VehicleFactory(customer=customer)
        inspection = InspectionRunFactory.for_vehicle(vehicle=vehicle)

        asset = inspection.asset
        assert asset.id == vehicle.id
        assert asset.vin == vehicle.vin

    def test_inspection_run_asset_property_equipment(self):
        """Test asset property returns correct equipment instance."""
        customer = CustomerFactory()
        equipment = EquipmentFactory(customer=customer)
        inspection = InspectionRunFactory.for_equipment(equipment=equipment)

        asset = inspection.asset
        assert asset.id == equipment.id
        assert asset.serial_number == equipment.serial_number

    def test_inspection_run_is_finalized_property(self):
        """Test is_finalized property."""
        inspection = InspectionRunFactory(finalized_at=None)
        assert inspection.is_finalized is False

        inspection.finalized_at = timezone.now()
        inspection.save()
        assert inspection.is_finalized is True

    def test_inspection_run_defect_count_property(self):
        """Test defect_count property."""
        inspection = InspectionRunFactory()
        assert inspection.defect_count == 0

        InspectionDefectFactory(inspection_run=inspection)
        assert inspection.defect_count == 1

        InspectionDefectFactory(inspection_run=inspection)
        assert inspection.defect_count == 2

    def test_inspection_run_critical_defect_count_property(self):
        """Test critical_defect_count property."""
        inspection = InspectionRunFactory()

        InspectionDefectFactory.critical(inspection_run=inspection)
        InspectionDefectFactory.major(inspection_run=inspection)
        InspectionDefectFactory.minor(inspection_run=inspection)

        assert inspection.critical_defect_count == 1
        assert inspection.defect_count == 3

    def test_inspection_run_status_choices(self):
        """Test all valid inspection statuses."""
        for status in VALID_CHOICES['inspection_statuses']:
            inspection = InspectionRunFactory(status=status)
            assert inspection.status == status

    def test_inspection_run_invalid_status(self):
        """Test invalid status raises error."""
        with pytest.raises(ValidationError):
            inspection = InspectionRunFactory.build(status='INVALID')
            inspection.full_clean()

    def test_inspection_run_asset_customer_mismatch(self):
        """Test validation fails when asset customer doesn't match."""
        customer1 = CustomerFactory()
        customer2 = CustomerFactory()
        equipment = EquipmentFactory(customer=customer1)

        with pytest.raises(ValidationError) as exc_info:
            inspection = InspectionRunFactory.build(
                customer=customer2,
                asset_type='EQUIPMENT',
                asset_id=equipment.id
            )
            inspection.full_clean()

        assert 'customer' in str(exc_info.value)

    def test_inspection_run_status_cannot_go_backwards(self):
        """Test status cannot go from higher to lower state."""
        inspection = InspectionRunFactory(status='COMPLETED')

        with pytest.raises(ValidationError) as exc_info:
            inspection.status = 'DRAFT'
            inspection.full_clean()

        assert 'status' in str(exc_info.value)

    def test_inspection_run_template_snapshot_must_be_dict(self):
        """Test template_snapshot must be a dictionary."""
        with pytest.raises(ValidationError) as exc_info:
            InspectionRunFactory(template_snapshot="not a dict")

        assert 'template_snapshot' in str(exc_info.value)

    def test_inspection_run_template_snapshot_must_have_modules(self):
        """Test template_snapshot must contain 'modules' key."""
        with pytest.raises(ValidationError) as exc_info:
            InspectionRunFactory(template_snapshot={'no_modules': 'here'})

        assert 'template_snapshot' in str(exc_info.value)
        assert 'modules' in str(exc_info.value)

    def test_inspection_run_immutability_after_finalization(self):
        """Test protected fields cannot be modified after finalization."""
        inspection = InspectionRunFactory(
            status='COMPLETED',
            finalized_at=timezone.now(),
            step_data={'key': 'original'}
        )

        # Try to modify step_data
        with pytest.raises(ValidationError) as exc_info:
            inspection.step_data = {'key': 'modified'}
            inspection.save()

        assert 'step_data' in str(exc_info.value)
        assert 'finalized' in str(exc_info.value)

    def test_inspection_run_immutability_template_snapshot(self):
        """Test template_snapshot cannot be modified after finalization."""
        original_snapshot = get_test_data('inspection_run', 'completed')['template_snapshot']
        inspection = InspectionRunFactory(
            status='COMPLETED',
            finalized_at=timezone.now(),
            template_snapshot=original_snapshot
        )

        # Try to modify template_snapshot
        with pytest.raises(ValidationError) as exc_info:
            inspection.template_snapshot = {'modified': 'snapshot'}
            inspection.save()

        assert 'template_snapshot' in str(exc_info.value)

    def test_inspection_run_immutability_status(self):
        """Test status cannot be modified after finalization."""
        inspection = InspectionRunFactory(
            status='COMPLETED',
            finalized_at=timezone.now()
        )

        # Try to modify status
        with pytest.raises(ValidationError) as exc_info:
            inspection.status = 'DRAFT'
            inspection.save()

        assert 'status' in str(exc_info.value)

    def test_inspection_run_can_modify_notes_after_finalization(self):
        """Test notes can be modified even after finalization (not protected)."""
        inspection = InspectionRunFactory(
            status='COMPLETED',
            finalized_at=timezone.now(),
            notes='original notes'
        )

        # Notes should be modifiable
        inspection.notes = 'updated notes'
        inspection.save()  # Should not raise

        inspection.refresh_from_db()
        assert inspection.notes == 'updated notes'

    def test_inspection_run_str_representation(self):
        """Test string representation."""
        inspection = InspectionRunFactory()
        str_repr = str(inspection)

        assert inspection.template_key in str_repr
        assert inspection.asset_type in str_repr

    def test_inspection_run_ordering(self):
        """Test default ordering by started_at descending."""
        old_inspection = InspectionRunFactory(
            started_at=timezone.now() - timedelta(days=1)
        )
        new_inspection = InspectionRunFactory(
            started_at=timezone.now()
        )

        inspections = list(InspectionRun.objects.all())
        assert inspections[0] == new_inspection
        assert inspections[1] == old_inspection


# ============================================================================
# InspectionDefect Model Tests
# ============================================================================

@pytest.mark.django_db
class TestInspectionDefectModel:
    """Test InspectionDefect model."""

    def test_create_inspection_defect_default(self):
        """Test creating defect with default factory."""
        defect = InspectionDefectFactory()

        assert defect.id is not None
        assert defect.inspection_run is not None
        assert defect.defect_identity is not None
        assert len(defect.defect_identity) == 64  # SHA256 hash
        assert defect.severity in VALID_CHOICES['defect_severities']
        assert defect.status in VALID_CHOICES['defect_statuses']
        assert defect.title
        assert defect.description

    def test_create_defect_all_severities(self):
        """Test creating defects with all severity levels."""
        critical = InspectionDefectFactory.critical()
        assert critical.severity == 'CRITICAL'

        major = InspectionDefectFactory.major()
        assert major.severity == 'MAJOR'

        minor = InspectionDefectFactory.minor()
        assert minor.severity == 'MINOR'

    def test_defect_identity_generation(self):
        """Test defect identity hash generation."""
        inspection = InspectionRunFactory()
        module_key = 'visual_inspection'
        step_key = 'hydraulic_leaks'
        rule_id = 'leak_check_rule'

        identity = InspectionDefect.generate_defect_identity(
            inspection.id,
            module_key,
            step_key,
            rule_id
        )

        assert isinstance(identity, str)
        assert len(identity) == 64
        # Should be deterministic
        identity2 = InspectionDefect.generate_defect_identity(
            inspection.id,
            module_key,
            step_key,
            rule_id
        )
        assert identity == identity2

    def test_defect_identity_idempotency(self):
        """Test defect identity prevents duplicates."""
        inspection = InspectionRunFactory()
        defect_data = get_test_data('inspection_defect', 'critical')

        # Create first defect
        defect1 = InspectionDefectFactory(
            inspection_run=inspection,
            module_key=defect_data['module_key'],
            step_key=defect_data['step_key'],
            rule_id=defect_data['rule_id']
        )

        # Try to create duplicate with same identity
        with pytest.raises(Exception):  # IntegrityError for unique constraint
            InspectionDefectFactory(
                inspection_run=inspection,
                module_key=defect_data['module_key'],
                step_key=defect_data['step_key'],
                rule_id=defect_data['rule_id']
            )

    def test_defect_severity_choices(self):
        """Test all valid defect severities."""
        inspection = InspectionRunFactory()

        for severity in VALID_CHOICES['defect_severities']:
            defect = InspectionDefectFactory(
                inspection_run=inspection,
                severity=severity
            )
            assert defect.severity == severity

    def test_defect_status_choices(self):
        """Test all valid defect statuses."""
        inspection = InspectionRunFactory()

        for status in VALID_CHOICES['defect_statuses']:
            defect = InspectionDefectFactory(
                inspection_run=inspection,
                status=status
            )
            assert defect.status == status

    def test_defect_invalid_severity(self):
        """Test invalid severity raises error."""
        with pytest.raises(ValidationError):
            defect = InspectionDefectFactory.build(severity='INVALID')
            defect.full_clean()

    def test_defect_invalid_status(self):
        """Test invalid status raises error."""
        with pytest.raises(ValidationError):
            defect = InspectionDefectFactory.build(status='INVALID')
            defect.full_clean()

    def test_defect_identity_must_be_64_chars(self):
        """Test defect_identity must be exactly 64 characters."""
        with pytest.raises(ValidationError) as exc_info:
            InspectionDefectFactory(defect_identity='short')

        assert 'defect_identity' in str(exc_info.value)
        assert '64' in str(exc_info.value)

    def test_defect_details_must_be_dict(self):
        """Test defect_details must be a dictionary if provided."""
        with pytest.raises(ValidationError) as exc_info:
            InspectionDefectFactory(defect_details="not a dict")

        assert 'defect_details' in str(exc_info.value)

    def test_defect_details_can_be_null(self):
        """Test defect_details can be null."""
        defect = InspectionDefectFactory(defect_details=None)
        assert defect.defect_details is None

    def test_defect_evaluation_trace_can_be_null(self):
        """Test evaluation_trace can be null (manual defects)."""
        defect = InspectionDefectFactory(
            evaluation_trace=None,
            rule_id=None
        )
        assert defect.evaluation_trace is None
        assert defect.rule_id is None

    def test_defect_cascade_delete_with_inspection(self):
        """Test defects are deleted when inspection is deleted."""
        inspection = InspectionRunFactory()
        defect1 = InspectionDefectFactory(inspection_run=inspection)
        defect2 = InspectionDefectFactory(inspection_run=inspection)

        defect_ids = [defect1.id, defect2.id]

        # Delete inspection
        inspection.delete()

        # Defects should be deleted
        assert InspectionDefect.objects.filter(id__in=defect_ids).count() == 0

    def test_defect_str_representation(self):
        """Test string representation."""
        defect = InspectionDefectFactory()
        str_repr = str(defect)

        assert defect.severity in str_repr
        assert defect.title in str_repr

    def test_defect_ordering(self):
        """Test default ordering by created_at descending."""
        # Create defects with small time gap
        import time
        defect1 = InspectionDefectFactory()
        time.sleep(0.01)
        defect2 = InspectionDefectFactory()

        defects = list(InspectionDefect.objects.filter(
            id__in=[defect1.id, defect2.id]
        ))

        # Most recent first
        assert defects[0] == defect2
        assert defects[1] == defect1

    def test_manual_defect_without_rule(self):
        """Test creating manual defect (no rule_id)."""
        defect_data = get_test_data('inspection_defect', 'minor')
        assert defect_data['rule_id'] is None

        defect = InspectionDefectFactory.minor()
        assert defect.rule_id is None
        assert defect.evaluation_trace is None
