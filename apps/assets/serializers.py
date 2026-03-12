"""
DRF Serializers for Asset Management

Serializers for:
- Vehicle (with VIN validation and decode data)
- Equipment (with serial number and tag-based data)
"""

from rest_framework import serializers
from .models import Vehicle, Equipment, VINDecodeData


class VehicleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing vehicles"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id',
            'customer',
            'customer_name',
            'vin',
            'unit_number',
            'year',
            'make',
            'model',
            'is_active',
            'tags',
            'created_at',
        ]
        read_only_fields = ['id', 'customer_name', 'created_at']


class VehicleDetailSerializer(serializers.ModelSerializer):
    """Full serializer for vehicle CRUD operations"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    equipment_count = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id',
            'customer',
            'customer_name',
            'vin',
            'unit_number',
            'year',
            'make',
            'model',
            'license_plate',
            'odometer_miles',
            'engine_hours',
            'is_active',
            'notes',
            'tags',
            'vin_decode_data',
            'equipment_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'customer_name', 'equipment_count', 'created_at', 'updated_at']

    def get_equipment_count(self, obj):
        """Get count of equipment mounted on this vehicle"""
        return obj.equipment.count()

    def validate_vin(self, value):
        """
        Validate VIN format and uniqueness
        VIN must be exactly 17 characters, alphanumeric (excluding I, O, Q)
        """
        if not value:
            return value

        # Clean VIN - uppercase and strip whitespace
        clean_vin = value.upper().strip()

        # Check length
        if len(clean_vin) != 17:
            raise serializers.ValidationError(
                f'VIN must be exactly 17 characters (got {len(clean_vin)})'
            )

        # Check characters (alphanumeric, no I, O, Q)
        invalid_chars = set('IOQ')
        for char in clean_vin:
            if not char.isalnum():
                raise serializers.ValidationError(
                    f'VIN contains invalid character: {char}'
                )
            if char in invalid_chars:
                raise serializers.ValidationError(
                    f'VIN cannot contain I, O, or Q (found: {char})'
                )

        # Check uniqueness
        qs = Vehicle.objects.filter(vin=clean_vin)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)

        if qs.exists():
            raise serializers.ValidationError(
                f'Vehicle with VIN {clean_vin} already exists'
            )

        return clean_vin

    def validate_unit_number(self, value):
        """Clean and validate unit number"""
        if value:
            return value.strip().upper()
        return value

    def validate_year(self, value):
        """Validate vehicle year"""
        if value:
            from datetime import datetime
            current_year = datetime.now().year

            if value < 1900:
                raise serializers.ValidationError('Year must be 1900 or later')
            if value > current_year + 2:
                raise serializers.ValidationError(
                    f'Year cannot be more than 2 years in the future'
                )

        return value

    def validate_tags(self, value):
        """
        Validate tags format and allowed values
        Tags should be uppercase strings
        """
        if not isinstance(value, list):
            raise serializers.ValidationError('Tags must be a list')

        # Define allowed tags (can be extended)
        ALLOWED_TAGS = {
            'AERIAL_DEVICE',
            'INSULATED_BOOM',
            'DIELECTRIC',
            'CRANE',
            'BUCKET_TRUCK',
            'DIGGER_DERRICK',
            'HYBRID',
            'ELECTRIC',
            'DIESEL',
            'GASOLINE',
            'CNG',
            'HEAVY_DUTY',
            'MEDIUM_DUTY',
            'LIGHT_DUTY',
        }

        cleaned_tags = []
        for tag in value:
            if not isinstance(tag, str):
                raise serializers.ValidationError('Each tag must be a string')

            clean_tag = tag.upper().strip()

            if clean_tag not in ALLOWED_TAGS:
                raise serializers.ValidationError(
                    f'Invalid tag: {tag}. Allowed tags: {", ".join(sorted(ALLOWED_TAGS))}'
                )

            if clean_tag not in cleaned_tags:
                cleaned_tags.append(clean_tag)

        return cleaned_tags

    def validate(self, data):
        """
        Business logic validation:
        - Must have at least unit_number or VIN
        - If year is provided, should have make/model
        """
        if not data.get('vin') and not data.get('unit_number'):
            raise serializers.ValidationError({
                'vehicle': 'Must provide either VIN or unit number'
            })

        if data.get('year') and not (data.get('make') and data.get('model')):
            raise serializers.ValidationError({
                'make': 'If year is provided, make and model are required'
            })

        return data


class EquipmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing equipment"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    mounted_on_unit = serializers.CharField(source='mounted_on_vehicle.unit_number', read_only=True)

    class Meta:
        model = Equipment
        fields = [
            'id',
            'customer',
            'customer_name',
            'serial_number',
            'asset_number',
            'equipment_type',
            'manufacturer',
            'model',
            'mounted_on_vehicle',
            'mounted_on_unit',
            'is_active',
            'tags',
            'created_at',
        ]
        read_only_fields = ['id', 'customer_name', 'mounted_on_unit', 'created_at']


class EquipmentDetailSerializer(serializers.ModelSerializer):
    """Full serializer for equipment CRUD operations"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    mounted_on_unit = serializers.CharField(source='mounted_on_vehicle.unit_number', read_only=True)
    mounted_on_vin = serializers.CharField(source='mounted_on_vehicle.vin', read_only=True)

    class Meta:
        model = Equipment
        fields = [
            'id',
            'customer',
            'customer_name',
            'serial_number',
            'asset_number',
            'equipment_type',
            'manufacturer',
            'model',
            'year',
            'mounted_on_vehicle',
            'mounted_on_unit',
            'mounted_on_vin',
            'is_active',
            'notes',
            'tags',
            'equipment_data',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'customer_name', 'mounted_on_unit', 'mounted_on_vin', 'created_at', 'updated_at']

    def validate_serial_number(self, value):
        """Validate serial number format and uniqueness"""
        if not value:
            raise serializers.ValidationError('Serial number is required')

        # Clean serial number
        clean_sn = value.strip().upper()

        # Check uniqueness
        qs = Equipment.objects.filter(serial_number=clean_sn)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)

        if qs.exists():
            raise serializers.ValidationError(
                f'Equipment with serial number {clean_sn} already exists'
            )

        return clean_sn

    def validate_asset_number(self, value):
        """Clean asset number"""
        if value:
            return value.strip().upper()
        return value

    def validate_mounted_on_vehicle(self, value):
        """Validate that vehicle belongs to same customer"""
        if value:
            # Get customer from context or instance
            customer = None
            if self.instance:
                customer = self.instance.customer
            elif 'customer' in self.initial_data:
                from apps.customers.models import Customer
                try:
                    customer = Customer.objects.get(id=self.initial_data['customer'])
                except Customer.DoesNotExist:
                    pass

            # Validate vehicle belongs to same customer
            if customer and value.customer_id != customer.id:
                raise serializers.ValidationError(
                    'Vehicle must belong to the same customer as the equipment'
                )

        return value

    def validate_tags(self, value):
        """
        Validate tags format and allowed values
        Tags drive what additional data needs to be collected
        """
        if not isinstance(value, list):
            raise serializers.ValidationError('Tags must be a list')

        # Define allowed equipment tags
        ALLOWED_TAGS = {
            'AERIAL_DEVICE',
            'INSULATED_BOOM',
            'DIELECTRIC',
            'CRANE',
            'DIGGER_DERRICK',
            'HYDRAULIC_LIFT',
            'PNEUMATIC',
            'ELECTRIC_POWERED',
            'ARTICULATING',
            'TELESCOPIC',
            'PLATFORM',
            'BUCKET',
        }

        cleaned_tags = []
        for tag in value:
            if not isinstance(tag, str):
                raise serializers.ValidationError('Each tag must be a string')

            clean_tag = tag.upper().strip()

            if clean_tag not in ALLOWED_TAGS:
                raise serializers.ValidationError(
                    f'Invalid tag: {tag}. Allowed tags: {", ".join(sorted(ALLOWED_TAGS))}'
                )

            if clean_tag not in cleaned_tags:
                cleaned_tags.append(clean_tag)

        return cleaned_tags

    def validate_equipment_data(self, value):
        """
        Validate equipment_data structure based on tags
        This is flexible but should follow expected patterns
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError('equipment_data must be a dictionary')

        # Optional: Add specific validation based on common data patterns
        # For example, if AERIAL_DEVICE tag exists, validate placard data structure

        return value

    def validate(self, data):
        """
        Business logic validation:
        - Serial number is required
        - Equipment type should be provided
        - If mounted on vehicle, validate vehicle customer matches
        """
        if not data.get('serial_number'):
            raise serializers.ValidationError({
                'serial_number': 'Serial number is required'
            })

        if not data.get('equipment_type'):
            raise serializers.ValidationError({
                'equipment_type': 'Equipment type is required'
            })

        return data


class EquipmentDataUpdateSerializer(serializers.Serializer):
    """
    Specialized serializer for updating equipment_data field
    Used during inspection setup to collect tag-specific data
    """
    data_type = serializers.ChoiceField(
        choices=['placard', 'dielectric', 'hydraulic', 'capabilities', 'other'],
        help_text="Type of data being updated"
    )
    data = serializers.JSONField(
        help_text="The data to merge into equipment_data"
    )

    def validate_data(self, value):
        """Validate data is a dictionary"""
        if not isinstance(value, dict):
            raise serializers.ValidationError('data must be a dictionary')
        return value

    def save(self, equipment):
        """
        Merge the provided data into equipment.equipment_data
        Preserves existing data while updating with new values
        """
        data_type = self.validated_data['data_type']
        new_data = self.validated_data['data']

        # Get existing equipment_data or initialize
        equipment_data = equipment.equipment_data or {}

        # Merge new data under data_type key
        if data_type not in equipment_data:
            equipment_data[data_type] = {}

        equipment_data[data_type].update(new_data)

        # Save back to equipment
        equipment.equipment_data = equipment_data
        equipment.save(update_fields=['equipment_data', 'updated_at'])

        return equipment


class VINDecodeDataSerializer(serializers.ModelSerializer):
    """Serializer for VIN decode data (NHTSA vPIC results)"""
    vehicle_unit_number = serializers.CharField(source='vehicle.unit_number', read_only=True)
    vehicle_customer_name = serializers.CharField(source='vehicle.customer.name', read_only=True)

    class Meta:
        model = VINDecodeData
        fields = [
            'id',
            'vehicle',
            'vehicle_unit_number',
            'vehicle_customer_name',
            'vin',
            'model_year',
            'make',
            'model',
            'manufacturer',
            'vehicle_type',
            'body_class',
            'engine_model',
            'engine_configuration',
            'engine_cylinders',
            'displacement_liters',
            'fuel_type_primary',
            'fuel_type_secondary',
            'gvwr',
            'gvwr_min_lbs',
            'gvwr_max_lbs',
            'abs',
            'airbag_locations',
            'plant_city',
            'plant_state',
            'plant_country',
            'error_code',
            'error_text',
            'decoded_at',
            'raw_response',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'vehicle_unit_number', 'vehicle_customer_name', 'decoded_at', 'created_at', 'updated_at']

    def validate_vin(self, value):
        """Ensure VIN matches the associated vehicle"""
        if value:
            clean_vin = value.upper().strip()

            # If updating existing decode, ensure VIN matches vehicle
            if self.instance and self.instance.vehicle.vin != clean_vin:
                raise serializers.ValidationError(
                    'VIN does not match the associated vehicle'
                )

            return clean_vin
        return value


class VINDecodeDataSerializer(serializers.ModelSerializer):
    """Serializer for VIN decode data (NHTSA vPIC results)"""
    vehicle_unit_number = serializers.CharField(source='vehicle.unit_number', read_only=True)
    vehicle_customer_name = serializers.CharField(source='vehicle.customer.name', read_only=True)

    class Meta:
        model = VINDecodeData
        fields = [
            'id',
            'vehicle',
            'vehicle_unit_number',
            'vehicle_customer_name',
            'vin',
            'model_year',
            'make',
            'model',
            'manufacturer',
            'vehicle_type',
            'body_class',
            'engine_model',
            'engine_configuration',
            'engine_cylinders',
            'displacement_liters',
            'fuel_type_primary',
            'fuel_type_secondary',
            'gvwr',
            'gvwr_min_lbs',
            'gvwr_max_lbs',
            'abs',
            'airbag_locations',
            'plant_city',
            'plant_state',
            'plant_country',
            'error_code',
            'error_text',
            'decoded_at',
            'raw_response',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'vehicle_unit_number', 'vehicle_customer_name', 'decoded_at', 'created_at', 'updated_at']

    def validate_vin(self, value):
        """Ensure VIN matches the associated vehicle"""
        if value:
            clean_vin = value.upper().strip()

            # If updating existing decode, ensure VIN matches vehicle
            if self.instance and self.instance.vehicle.vin != clean_vin:
                raise serializers.ValidationError(
                    'VIN does not match the associated vehicle'
                )

            return clean_vin
        return value
