"""
Serializers for Inspection models and runtime operations.
"""

from rest_framework import serializers
from apps.inspections.models import InspectionRun, InspectionDefect, InspectionPhoto
from apps.inspections.services.runtime_service import InspectionRuntime
from PIL import Image
from io import BytesIO


class InspectionDefectSerializer(serializers.ModelSerializer):
    """Serializer for InspectionDefect."""

    class Meta:
        model = InspectionDefect
        fields = [
            'id',
            'inspection_run',
            'defect_identity',
            'module_key',
            'step_key',
            'rule_id',
            'severity',
            'status',
            'title',
            'description',
            'defect_details',
            'evaluation_trace',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'defect_identity', 'created_at', 'updated_at']


class InspectionRunListSerializer(serializers.ModelSerializer):
    """Serializer for listing inspection runs."""

    asset_info = serializers.SerializerMethodField()
    defect_count = serializers.IntegerField(read_only=True)
    critical_defect_count = serializers.IntegerField(read_only=True)
    completion_status = serializers.SerializerMethodField()

    class Meta:
        model = InspectionRun
        fields = [
            'id',
            'asset_type',
            'asset_id',
            'asset_info',
            'customer',
            'template_key',
            'program_key',
            'status',
            'started_at',
            'finalized_at',
            'inspector_name',
            'defect_count',
            'critical_defect_count',
            'completion_status',
            'created_at'
        ]

    def get_asset_info(self, obj):
        """Get basic asset information."""
        try:
            asset = obj.asset
            if obj.asset_type == 'VEHICLE':
                return {
                    'type': 'VEHICLE',
                    'vin': asset.vin,
                    'unit_number': asset.unit_number,
                    'year': asset.year,
                    'make': asset.make,
                    'model': asset.model
                }
            else:  # EQUIPMENT
                return {
                    'type': 'EQUIPMENT',
                    'serial_number': asset.serial_number,
                    'asset_number': asset.asset_number,
                    'manufacturer': asset.manufacturer,
                    'model': asset.model,
                    'equipment_type': asset.equipment_type
                }
        except Exception:
            return None

    def get_completion_status(self, obj):
        """Get completion status."""
        try:
            status = InspectionRuntime.calculate_completion_status(obj)
            return status.to_dict()
        except Exception:
            return None


class InspectionRunDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed inspection run view."""

    asset_info = serializers.SerializerMethodField()
    defects = InspectionDefectSerializer(many=True, read_only=True)
    completion_status = serializers.SerializerMethodField()

    class Meta:
        model = InspectionRun
        fields = [
            'id',
            'asset_type',
            'asset_id',
            'asset_info',
            'customer',
            'template_key',
            'program_key',
            'status',
            'started_at',
            'finalized_at',
            'inspector_name',
            'inspector_signature',
            'template_snapshot',
            'step_data',
            'notes',
            'defects',
            'completion_status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'template_snapshot', 'defects']

    def get_asset_info(self, obj):
        """Get detailed asset information."""
        try:
            asset = obj.asset
            if obj.asset_type == 'VEHICLE':
                return {
                    'type': 'VEHICLE',
                    'id': str(asset.id),
                    'vin': asset.vin,
                    'unit_number': asset.unit_number,
                    'year': asset.year,
                    'make': asset.make,
                    'model': asset.model,
                    'license_plate': asset.license_plate,
                    'capabilities': asset.capabilities
                }
            else:  # EQUIPMENT
                return {
                    'type': 'EQUIPMENT',
                    'id': str(asset.id),
                    'serial_number': asset.serial_number,
                    'asset_number': asset.asset_number,
                    'manufacturer': asset.manufacturer,
                    'model': asset.model,
                    'equipment_type': asset.equipment_type,
                    'capabilities': asset.capabilities,
                    'equipment_data': asset.equipment_data
                }
        except Exception:
            return None

    def get_completion_status(self, obj):
        """Get completion status."""
        try:
            status = InspectionRuntime.calculate_completion_status(obj)
            return status.to_dict()
        except Exception:
            return None


class CreateInspectionSerializer(serializers.Serializer):
    """Serializer for creating new inspection."""

    template_key = serializers.CharField(max_length=100)
    asset_type = serializers.ChoiceField(choices=['VEHICLE', 'EQUIPMENT'])
    asset_id = serializers.UUIDField()
    inspector_name = serializers.CharField(max_length=200, required=False, allow_blank=True)

    def validate(self, data):
        """Validate asset exists."""
        from apps.assets.models import Vehicle, Equipment

        asset_type = data['asset_type']
        asset_id = data['asset_id']

        try:
            if asset_type == 'VEHICLE':
                asset = Vehicle.objects.get(id=asset_id)
            else:
                asset = Equipment.objects.get(id=asset_id)
            data['asset'] = asset
        except (Vehicle.DoesNotExist, Equipment.DoesNotExist):
            raise serializers.ValidationError(
                f"{asset_type} with id {asset_id} not found"
            )

        return data


class SaveStepResponseSerializer(serializers.Serializer):
    """Serializer for saving step response."""

    step_key = serializers.CharField(max_length=100)
    field_data = serializers.JSONField()
    validate = serializers.BooleanField(default=True)


class FinalizeInspectionSerializer(serializers.Serializer):
    """Serializer for finalizing inspection."""

    signature_data = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    force = serializers.BooleanField(default=False)


class InspectionPhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for inspection photos.

    Includes URLs for both full-size image and thumbnail.
    """

    url = serializers.ReadOnlyField()
    thumbnail_url = serializers.ReadOnlyField()
    uploaded_by_name = serializers.ReadOnlyField()

    class Meta:
        model = InspectionPhoto
        fields = [
            'id',
            'inspection',
            'defect',
            'step_key',
            'image',
            'thumbnail',
            'url',
            'thumbnail_url',
            'caption',
            'file_size',
            'width',
            'height',
            'uploaded_by',
            'uploaded_by_name',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'file_size',
            'width',
            'height',
            'created_at',
            'thumbnail',
            'url',
            'thumbnail_url'
        ]


class PhotoUploadSerializer(serializers.Serializer):
    """
    Serializer for photo upload validation.

    Validates:
    - Image file format and size
    - Inspection exists and is editable
    - Step key is valid
    """

    step_key = serializers.CharField(max_length=100)
    defect_id = serializers.UUIDField(required=False, allow_null=True)
    image = serializers.ImageField()
    caption = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_image(self, value):
        """
        Validate image file.

        Checks:
        - File size (max 10MB)
        - Valid image format
        - Image can be opened
        """
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(
                "Image file size cannot exceed 10MB. Please compress the image."
            )

        # Validate image format by attempting to open
        try:
            img = Image.open(value)
            img.verify()
            # Reset file pointer after verify
            value.seek(0)
        except Exception as e:
            raise serializers.ValidationError(
                f"Invalid image file: {str(e)}"
            )

        return value

    def validate(self, data):
        """
        Cross-field validation.

        Ensures defect belongs to same inspection if provided.
        """
        # Get inspection from context
        inspection = self.context.get('inspection')

        if not inspection:
            raise serializers.ValidationError("Inspection context required")

        # Validate inspection is not completed
        if inspection.status == 'COMPLETED':
            raise serializers.ValidationError(
                "Cannot upload photos to completed inspection"
            )

        # Validate defect belongs to inspection
        defect_id = data.get('defect_id')
        if defect_id:
            try:
                defect = InspectionDefect.objects.get(id=defect_id)
                if defect.inspection_run_id != inspection.id:
                    raise serializers.ValidationError(
                        "Defect does not belong to this inspection"
                    )
                data['defect'] = defect
            except InspectionDefect.DoesNotExist:
                raise serializers.ValidationError("Defect not found")

        return data
