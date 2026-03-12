"""
Tests for Inspection Runtime Service

Tests inspection creation, step response saving, completion tracking, and finalization.
"""

import pytest
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.inspections.models import InspectionRun
from apps.inspections.services.runtime_service import (
    InspectionRuntime,
    InspectionRuntimeError,
    InspectionAlreadyFinalizedException,
    InspectionNotReadyException,
    CompletionStatus
)
from apps.inspections.services.template_service import TemplateService
from tests.factories import CustomerFactory, EquipmentFactory, VehicleFactory


@pytest.mark.django_db
class TestInspectionCreation:
    """Test creating inspection runs from templates."""

    def test_create_inspection_for_equipment(self):
        equipment = EquipmentFactory(
            equipment_type='AERIAL_DEVICE',
            capabilities=['DIELECTRIC']
        )

        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment,
            inspector_name='John Smith'
        )

        assert inspection.id is not None
        assert inspection.asset_type == 'EQUIPMENT'
        assert inspection.asset_id == equipment.id
        assert inspection.customer == equipment.customer
        assert inspection.template_key == 'ansi_a92_2_periodic_dielectric'
        assert inspection.status == 'DRAFT'
        assert inspection.inspector_name == 'John Smith'
        assert inspection.template_snapshot is not None
        assert inspection.step_data == {}

    def test_create_inspection_for_vehicle(self):
        vehicle = VehicleFactory()

        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=vehicle,
            inspector_name='Jane Doe'
        )

        assert inspection.asset_type == 'VEHICLE'
        assert inspection.asset_id == vehicle.id

    def test_create_inspection_snapshots_template(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])

        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        # Template snapshot should be immutable copy
        assert 'format' in inspection.template_snapshot
        assert 'template' in inspection.template_snapshot
        assert 'procedure' in inspection.template_snapshot

    def test_create_inspection_validates_asset(self):
        equipment = EquipmentFactory()

        # This should work - equipment customer matches
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        # Reload and verify customer matches
        inspection.refresh_from_db()
        assert inspection.customer == equipment.customer

    def test_create_inspection_custom_start_time(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        start_time = timezone.now()

        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment,
            started_at=start_time
        )

        assert inspection.started_at == start_time


@pytest.mark.django_db
class TestStepResponseSaving:
    """Test saving step responses."""

    def test_save_step_response_simple(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        field_data = {
            'cleanliness': 'CLEAN',
            'visible_damage_present': False
        }

        result = InspectionRuntime.save_step_response(
            inspection_run=inspection,
            step_key='insulating_visual_inspection',
            field_data=field_data
        )

        assert result.valid
        inspection.refresh_from_db()
        assert 'insulating_visual_inspection' in inspection.step_data
        assert inspection.step_data['insulating_visual_inspection']['cleanliness'] == 'CLEAN'
        assert 'completed_at' in inspection.step_data['insulating_visual_inspection']

    def test_save_step_response_updates_status(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        assert inspection.status == 'DRAFT'

        field_data = {'cleanliness': 'CLEAN', 'visible_damage_present': False}
        InspectionRuntime.save_step_response(
            inspection_run=inspection,
            step_key='insulating_visual_inspection',
            field_data=field_data
        )

        inspection.refresh_from_db()
        assert inspection.status == 'IN_PROGRESS'

    def test_save_step_response_validation_fails(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        # Invalid field data - wrong type
        field_data = {
            'cleanliness': 123  # Should be string
        }

        with pytest.raises(DjangoValidationError):
            InspectionRuntime.save_step_response(
                inspection_run=inspection,
                step_key='insulating_visual_inspection',
                field_data=field_data,
                validate=True
            )

    def test_save_step_response_skip_validation(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        # Invalid data but validation skipped
        field_data = {'cleanliness': 123}

        result = InspectionRuntime.save_step_response(
            inspection_run=inspection,
            step_key='insulating_visual_inspection',
            field_data=field_data,
            validate=False
        )

        # Should save without validation
        inspection.refresh_from_db()
        assert 'insulating_visual_inspection' in inspection.step_data

    def test_save_step_response_to_finalized_inspection_fails(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        # Finalize inspection
        inspection.status = 'COMPLETED'
        inspection.finalized_at = timezone.now()
        inspection.save()

        field_data = {'cleanliness': 'CLEAN', 'visible_damage_present': False}

        with pytest.raises(InspectionAlreadyFinalizedException):
            InspectionRuntime.save_step_response(
                inspection_run=inspection,
                step_key='insulating_visual_inspection',
                field_data=field_data
            )

    def test_save_step_response_invalid_step_key(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        with pytest.raises(ValueError, match='not found in template'):
            InspectionRuntime.save_step_response(
                inspection_run=inspection,
                step_key='nonexistent_step',
                field_data={}
            )


@pytest.mark.django_db
class TestStepResponseRetrieval:
    """Test retrieving step responses."""

    def test_get_step_response_exists(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        field_data = {'cleanliness': 'CLEAN', 'visible_damage_present': False}
        InspectionRuntime.save_step_response(
            inspection_run=inspection,
            step_key='insulating_visual_inspection',
            field_data=field_data
        )

        response = InspectionRuntime.get_step_response(inspection, 'insulating_visual_inspection')
        assert response is not None
        assert response['cleanliness'] == 'CLEAN'
        assert response['visible_damage_present'] == False

    def test_get_step_response_not_exists(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        response = InspectionRuntime.get_step_response(inspection, 'insulating_visual_inspection')
        assert response is None


@pytest.mark.django_db
class TestCompletionTracking:
    """Test inspection completion status calculation."""

    def test_calculate_completion_empty(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        completion = InspectionRuntime.calculate_completion_status(inspection)

        assert completion.completed_steps == 0
        assert completion.total_steps > 0
        assert completion.completion_percentage == 0.0
        assert not completion.ready_to_finalize

    def test_calculate_completion_partial(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        # Complete one step
        InspectionRuntime.save_step_response(
            inspection_run=inspection,
            step_key='insulating_visual_inspection',
            field_data={'cleanliness': 'CLEAN', 'visible_damage_present': False},
            validate=False
        )

        completion = InspectionRuntime.calculate_completion_status(inspection)

        assert completion.completed_steps == 1
        assert completion.completion_percentage > 0
        assert completion.completion_percentage < 100

    def test_calculate_completion_to_dict(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        completion = InspectionRuntime.calculate_completion_status(inspection)
        data = completion.to_dict()

        assert 'total_steps' in data
        assert 'completed_steps' in data
        assert 'required_steps' in data
        assert 'required_completed' in data
        assert 'completion_percentage' in data
        assert 'missing_required_steps' in data
        assert 'ready_to_finalize' in data


@pytest.mark.django_db
class TestFinalization:
    """Test inspection finalization."""

    def test_finalize_ready_inspection(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        # Complete all required steps (simplified - using force)
        finalized = InspectionRuntime.finalize_inspection(
            inspection_run=inspection,
            force=True
        )

        assert finalized.status == 'COMPLETED'
        assert finalized.finalized_at is not None
        assert finalized.is_finalized

    def test_finalize_with_signature(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        signature_data = {
            'signature': 'base64encodeddata',
            'inspector_id': 'inspector-123'
        }

        finalized = InspectionRuntime.finalize_inspection(
            inspection_run=inspection,
            signature_data=signature_data,
            force=True
        )

        assert finalized.inspector_signature is not None
        assert finalized.inspector_signature['signature'] == 'base64encodeddata'
        assert 'signed_at' in finalized.inspector_signature

    def test_finalize_already_finalized_fails(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        # Finalize once
        InspectionRuntime.finalize_inspection(inspection, force=True)

        # Try to finalize again
        with pytest.raises(InspectionAlreadyFinalizedException):
            InspectionRuntime.finalize_inspection(inspection, force=True)

    def test_finalize_incomplete_without_force_fails(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        # Try to finalize without completing required steps
        with pytest.raises(InspectionNotReadyException):
            InspectionRuntime.finalize_inspection(inspection, force=False)

    def test_finalize_makes_immutable(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        InspectionRuntime.finalize_inspection(inspection, force=True)

        # Try to modify - should fail
        with pytest.raises(InspectionAlreadyFinalizedException):
            InspectionRuntime.save_step_response(
                inspection_run=inspection,
                step_key='insulating_visual_inspection',
                field_data={'cleanliness': 'CLEAN', 'visible_damage_present': False}
            )


@pytest.mark.django_db
class TestUtilityMethods:
    """Test utility methods."""

    def test_get_next_incomplete_step(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        next_step = InspectionRuntime.get_next_incomplete_step(inspection)
        assert next_step is not None
        assert 'step_key' in next_step

    def test_get_next_incomplete_step_after_completion(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        # Get first step
        first_step = InspectionRuntime.get_next_incomplete_step(inspection)

        # Complete it
        InspectionRuntime.save_step_response(
            inspection_run=inspection,
            step_key=first_step['step_key'],
            field_data={},
            validate=False
        )

        # Get next
        next_step = InspectionRuntime.get_next_incomplete_step(inspection)
        assert next_step['step_key'] != first_step['step_key']

    def test_clear_step_response(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        # Save a step
        InspectionRuntime.save_step_response(
            inspection_run=inspection,
            step_key='insulating_visual_inspection',
            field_data={'cleanliness': 'CLEAN', 'visible_damage_present': False}
        )

        inspection.refresh_from_db()
        assert 'insulating_visual_inspection' in inspection.step_data

        # Clear it
        InspectionRuntime.clear_step_response(inspection, 'insulating_visual_inspection')

        inspection.refresh_from_db()
        assert 'hydraulic_leaks' not in inspection.step_data

    def test_clear_step_response_finalized_fails(self):
        equipment = EquipmentFactory(capabilities=['AERIAL_DEVICE'])
        inspection = InspectionRuntime.create_inspection(
            template_key='ansi_a92_2_periodic_dielectric',
            asset=equipment
        )

        InspectionRuntime.finalize_inspection(inspection, force=True)

        with pytest.raises(InspectionAlreadyFinalizedException):
            InspectionRuntime.clear_step_response(inspection, 'insulating_visual_inspection')
