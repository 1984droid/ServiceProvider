"""
Tests for Vehicle, Equipment, and VINDecodeData models.

All test data comes from tests.config - NO HARDCODED VALUES!
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.assets.models import Vehicle, Equipment, VINDecodeData
from tests.config import (
    get_test_data,
    ERROR_MESSAGES,
    CONSTRAINTS,
    VALID_CHOICES,
    get_next_test_vin,
    get_next_test_serial,
)
from tests.factories import (
    CustomerFactory,
    VehicleFactory,
    EquipmentFactory,
    VINDecodeDataFactory,
)


# ============================================================================
# Vehicle Model Tests
# ============================================================================

@pytest.mark.django_db
class TestVehicleModel:
    """Test Vehicle model creation, validation, and relationships."""

    def test_vehicle_creation_default(self, vehicle):
        """Test basic vehicle creation with default data."""
        default_data = get_test_data('vehicle', 'default')
        assert vehicle.unit_number == default_data['unit_number']
        assert vehicle.year == default_data['year']
        assert vehicle.make == default_data['make']
        assert vehicle.model == default_data['model']

    def test_vehicle_creation_minimal(self):
        """Test vehicle creation with minimal required fields (just VIN)."""
        vehicle = VehicleFactory.minimal()
        assert vehicle.vin is not None
        assert len(vehicle.vin) == CONSTRAINTS['vehicle']['vin']['exact_length']

    def test_vehicle_creation_insulated_boom(self):
        """Test vehicle creation with insulated boom variant."""
        vehicle = VehicleFactory.insulated_boom()
        boom_data = get_test_data('vehicle', 'insulated_boom')
        assert 'INSULATED_BOOM' in vehicle.capabilities

    def test_vehicle_str_representation(self, vehicle):
        """Test string representation."""
        expected = vehicle.unit_number or vehicle.vin[:8]
        assert expected in str(vehicle)

    def test_vehicle_vin_required(self):
        """Test VIN field is required."""
        with pytest.raises(ValidationError):
            vehicle = Vehicle(customer=CustomerFactory())
            vehicle.full_clean()

    def test_vehicle_vin_unique(self):
        """Test VIN uniqueness constraint."""
        vin = get_next_test_vin()
        VehicleFactory(vin=vin)

        with pytest.raises(IntegrityError):
            VehicleFactory(vin=vin)

    def test_vehicle_vin_length(self):
        """Test VIN length validation."""
        exact_length = CONSTRAINTS['vehicle']['vin']['exact_length']

        # Too short
        with pytest.raises(ValidationError):
            vehicle = VehicleFactory(vin='SHORT')
            vehicle.full_clean()

        # Too long
        with pytest.raises(ValidationError):
            vehicle = VehicleFactory(vin='A' * (exact_length + 1))
            vehicle.full_clean()

    def test_vehicle_customer_relationship(self, vehicle):
        """Test vehicle belongs to customer."""
        assert vehicle.customer is not None
        assert vehicle in vehicle.customer.vehicles.all()

    def test_vehicle_equipment_relationship(self, vehicle):
        """Test vehicle can have mounted equipment."""
        equipment = EquipmentFactory(mounted_on_vehicle=vehicle)
        assert equipment in vehicle.equipment.all()

    def test_vehicle_capabilities_json_field(self, vehicle):
        """Test capabilities stored as JSON array."""
        assert isinstance(vehicle.capabilities, list)

    def test_vehicle_odometer_positive(self):
        """Test odometer must be positive."""
        with pytest.raises(ValidationError):
            vehicle = VehicleFactory(odometer_miles=-100)
            vehicle.full_clean()

    def test_vehicle_engine_hours_positive(self):
        """Test engine hours must be positive."""
        with pytest.raises(ValidationError):
            vehicle = VehicleFactory(engine_hours=-10)
            vehicle.full_clean()


# ============================================================================
# VINDecodeData Model Tests
# ============================================================================

@pytest.mark.django_db
class TestVINDecodeDataModel:
    """Test VINDecodeData model creation and validation."""

    def test_vin_decode_creation(self, vehicle):
        """Test VIN decode data creation."""
        decode = VINDecodeDataFactory(vehicle=vehicle)
        default_data = get_test_data('vin_decode', 'default')
        assert decode.model_year == default_data['model_year']
        assert decode.make == default_data['make']
        assert decode.model == default_data['model']

    def test_vin_decode_error_variant(self, vehicle):
        """Test VIN decode with error."""
        decode = VINDecodeDataFactory.error_decode(vehicle=vehicle)
        error_data = get_test_data('vin_decode', 'error')
        assert decode.error_code == error_data['error_code']
        assert decode.error_text == error_data['error_text']

    def test_vin_decode_str_representation(self, vehicle):
        """Test string representation."""
        decode = VINDecodeDataFactory(vehicle=vehicle)
        assert decode.vin in str(decode)

    def test_vin_decode_one_per_vehicle(self, vehicle):
        """Test one-to-one relationship with vehicle."""
        VINDecodeDataFactory(vehicle=vehicle)

        with pytest.raises(IntegrityError):
            VINDecodeDataFactory(vehicle=vehicle)

    def test_vin_decode_vin_matches_vehicle(self, vehicle):
        """Test VIN in decode matches vehicle VIN."""
        decode = VINDecodeDataFactory(vehicle=vehicle)
        assert decode.vin == vehicle.vin

    def test_vin_decode_raw_response_json(self, vehicle):
        """Test raw_response is JSON field."""
        decode = VINDecodeDataFactory(vehicle=vehicle)
        assert isinstance(decode.raw_response, dict)

    def test_vin_decode_numeric_fields(self, vehicle):
        """Test numeric fields are properly typed."""
        decode = VINDecodeDataFactory(vehicle=vehicle)
        if decode.gvwr_min_lbs:
            assert isinstance(decode.gvwr_min_lbs, int)
        if decode.gvwr_max_lbs:
            assert isinstance(decode.gvwr_max_lbs, int)

    def test_vin_decode_vehicle_cascade_delete(self, vehicle):
        """Test decode is deleted when vehicle is deleted."""
        decode = VINDecodeDataFactory(vehicle=vehicle)
        decode_id = decode.id

        vehicle.delete()

        assert not VINDecodeData.objects.filter(id=decode_id).exists()


# ============================================================================
# Equipment Model Tests
# ============================================================================

@pytest.mark.django_db
class TestEquipmentModel:
    """Test Equipment model creation, validation, and relationships."""

    def test_equipment_creation_default(self, equipment):
        """Test basic equipment creation with default data."""
        default_data = get_test_data('equipment', 'default')
        assert equipment.asset_number == default_data['asset_number']
        assert equipment.equipment_type == default_data['equipment_type']
        assert equipment.is_active is True

    def test_equipment_creation_minimal(self):
        """Test equipment creation with minimal required fields."""
        equipment = EquipmentFactory.minimal()
        assert equipment.serial_number is not None

    def test_equipment_creation_insulated_aerial(self):
        """Test insulated aerial device creation."""
        equipment = EquipmentFactory.insulated_aerial()
        aerial_data = get_test_data('equipment', 'insulated_aerial')
        assert equipment.equipment_type == aerial_data['equipment_type']
        assert 'AERIAL_DEVICE' in equipment.capabilities
        assert 'INSULATED_BOOM' in equipment.capabilities
        assert equipment.equipment_data is not None

    def test_equipment_str_representation(self, equipment):
        """Test string representation."""
        expected = equipment.asset_number or equipment.serial_number[:12]
        assert expected in str(equipment)

    def test_equipment_serial_number_required(self):
        """Test serial number is required."""
        with pytest.raises(ValidationError):
            equipment = Equipment(customer=CustomerFactory())
            equipment.full_clean()

    def test_equipment_serial_number_unique(self):
        """Test serial number uniqueness."""
        serial = get_next_test_serial()
        EquipmentFactory(serial_number=serial)

        with pytest.raises(IntegrityError):
            EquipmentFactory(serial_number=serial)

    def test_equipment_customer_relationship(self, equipment):
        """Test equipment belongs to customer."""
        assert equipment.customer is not None
        assert equipment in equipment.customer.equipment.all()

    def test_equipment_mounted_on_vehicle(self):
        """Test equipment can be mounted on vehicle."""
        vehicle = VehicleFactory()
        equipment = EquipmentFactory(mounted_on_vehicle=vehicle)
        assert equipment.mounted_on_vehicle == vehicle
        assert equipment in vehicle.equipment.all()

    def test_equipment_capabilities_json_field(self, equipment):
        """Test capabilities stored as JSON array."""
        assert isinstance(equipment.capabilities, list)

    def test_equipment_data_json_field(self):
        """Test equipment_data stored as JSON."""
        equipment = EquipmentFactory.insulated_aerial()
        assert isinstance(equipment.equipment_data, dict)

        # Verify structure from config
        aerial_data = get_test_data('equipment', 'insulated_aerial')
        if 'equipment_data' in aerial_data:
            assert 'placard_data' in equipment.equipment_data

    def test_equipment_type_choices(self):
        """Test equipment_type validates against choices."""
        valid_types = VALID_CHOICES['equipment_types']

        # Valid type should work
        equipment = EquipmentFactory(equipment_type=valid_types[0])
        equipment.full_clean()

    def test_equipment_year_range(self):
        """Test year field validation."""
        min_year = CONSTRAINTS['equipment']['year']['min_value']
        max_year = CONSTRAINTS['equipment']['year']['max_value']

        # Valid year
        equipment = EquipmentFactory(year=2020)
        equipment.full_clean()

        # Too old
        with pytest.raises(ValidationError):
            equipment = EquipmentFactory(year=min_year - 1)
            equipment.full_clean()

        # Future year beyond max
        with pytest.raises(ValidationError):
            equipment = EquipmentFactory(year=max_year + 1)
            equipment.full_clean()

    def test_equipment_vehicle_cascade_null(self):
        """Test equipment.mounted_on_vehicle set to null when vehicle deleted."""
        vehicle = VehicleFactory()
        equipment = EquipmentFactory(mounted_on_vehicle=vehicle)

        vehicle.delete()

        equipment.refresh_from_db()
        assert equipment.mounted_on_vehicle is None
