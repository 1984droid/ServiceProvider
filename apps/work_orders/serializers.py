"""
Work Order Serializers

REST API serializers for work order models.
"""

from rest_framework import serializers
from apps.work_orders.models import WorkOrder, WorkOrderLine
from apps.organization.models import Employee, Department
from apps.customers.models import Customer
from apps.work_orders.services.vocabulary_service import VocabularyService


class WorkOrderLineSerializer(serializers.ModelSerializer):
    """Serializer for WorkOrderLine model."""

    assigned_to_name = serializers.SerializerMethodField()
    completed_by_name = serializers.SerializerMethodField()
    vocabulary_valid = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrderLine
        fields = [
            'id',
            'work_order',
            'line_number',
            'verb',
            'noun',
            'service_location',
            'description',
            'estimated_hours',
            'actual_hours',
            'parts_required',
            'assigned_to',
            'assigned_to_name',
            'status',
            'completed_at',
            'completed_by',
            'completed_by_name',
            'notes',
            'vocabulary_valid',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_assigned_to_name(self, obj):
        """Get assigned employee full name."""
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None

    def get_completed_by_name(self, obj):
        """Get completed by employee full name."""
        if obj.completed_by:
            return f"{obj.completed_by.first_name} {obj.completed_by.last_name}"
        return None

    def get_vocabulary_valid(self, obj):
        """Check if vocabulary is valid."""
        try:
            return VocabularyService.validate_line_vocabulary(
                obj.verb,
                obj.noun,
                obj.service_location
            )
        except Exception:
            return False

    def validate(self, data):
        """Validate work order line data."""
        # Validate vocabulary if provided
        if all(k in data for k in ['verb', 'noun', 'service_location']):
            is_valid = VocabularyService.validate_line_vocabulary(
                data['verb'],
                data['noun'],
                data['service_location']
            )
            if not is_valid:
                # Allow invalid vocabulary but add warning
                data['_vocabulary_warning'] = (
                    f"Vocabulary combination not found in catalog: "
                    f"{data['verb']} + {data['noun']} + {data['service_location']}"
                )

        # Validate status transitions
        if self.instance and 'status' in data:
            old_status = self.instance.status
            new_status = data['status']

            if old_status == 'COMPLETED' and new_status != 'COMPLETED':
                raise serializers.ValidationError(
                    "Cannot change status of completed line item"
                )

        return data


class WorkOrderLineCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating work order lines."""

    class Meta:
        model = WorkOrderLine
        fields = [
            'line_number',
            'verb',
            'noun',
            'service_location',
            'description',
            'estimated_hours',
            'parts_required',
            'assigned_to',
            'notes',
        ]


class WorkOrderSerializer(serializers.ModelSerializer):
    """Serializer for WorkOrder model."""

    lines = WorkOrderLineSerializer(many=True, read_only=True)
    customer_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    asset_display = serializers.SerializerMethodField()
    line_count = serializers.SerializerMethodField()
    total_estimated_hours = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = [
            'id',
            'customer',
            'customer_name',
            'asset_type',
            'asset_id',
            'asset_display',
            'department',
            'department_name',
            'title',
            'description',
            'priority',
            'status',
            'source_type',
            'source_id',
            'source',
            'approval_status',
            'approved_by',
            'approved_by_name',
            'approved_at',
            'rejected_reason',
            'scheduled_date',
            'due_date',
            'started_at',
            'completed_at',
            'assigned_to',
            'assigned_to_name',
            'lines',
            'line_count',
            'total_estimated_hours',
            'is_active',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_customer_name(self, obj):
        """Get customer name."""
        return obj.customer.name if obj.customer else None

    def get_department_name(self, obj):
        """Get department name."""
        return obj.department.name if obj.department else None

    def get_assigned_to_name(self, obj):
        """Get assigned employee full name."""
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None

    def get_approved_by_name(self, obj):
        """Get approved by employee full name."""
        if obj.approved_by:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}"
        return None

    def get_asset_display(self, obj):
        """Get asset display string."""
        try:
            asset = obj.asset
            if obj.asset_type == 'VEHICLE':
                return f"{asset.year} {asset.make} {asset.model} (VIN: {asset.vin})"
            else:
                return f"{asset.equipment_type} - {asset.manufacturer} {asset.model} (S/N: {asset.serial_number})"
        except Exception:
            return f"{obj.asset_type}: {obj.asset_id}"

    def get_line_count(self, obj):
        """Get number of work order lines."""
        return obj.lines.count()

    def get_total_estimated_hours(self, obj):
        """Get total estimated hours from all lines."""
        total = sum(
            line.estimated_hours or 0
            for line in obj.lines.all()
        )
        return float(total) if total else None

    def validate(self, data):
        """Validate work order data."""
        # Validate approval status transitions
        if self.instance and 'approval_status' in data:
            old_status = self.instance.approval_status
            new_status = data['approval_status']

            if old_status == 'APPROVED' and new_status != 'APPROVED':
                raise serializers.ValidationError(
                    "Cannot change approval status of approved work order"
                )

            if new_status == 'APPROVED':
                if 'approved_by' not in data and not self.instance.approved_by:
                    raise serializers.ValidationError(
                        "approved_by is required when approving work order"
                    )

        # Validate status transitions
        if self.instance and 'status' in data:
            old_status = self.instance.status
            new_status = data['status']

            if old_status == 'COMPLETED' and new_status != 'COMPLETED':
                raise serializers.ValidationError(
                    "Cannot change status of completed work order"
                )

        return data


class WorkOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating work orders with initial lines."""

    initial_lines = WorkOrderLineCreateSerializer(many=True, required=False)

    class Meta:
        model = WorkOrder
        fields = [
            'customer',
            'asset_type',
            'asset_id',
            'department',
            'title',
            'description',
            'priority',
            'source_type',
            'source_id',
            'source',
            'scheduled_date',
            'due_date',
            'assigned_to',
            'notes',
            'initial_lines',
        ]

    def create(self, validated_data):
        """Create work order with initial lines."""
        initial_lines = validated_data.pop('initial_lines', [])

        # Create work order
        work_order = WorkOrder.objects.create(**validated_data)

        # Create initial lines
        for idx, line_data in enumerate(initial_lines, start=1):
            WorkOrderLine.objects.create(
                work_order=work_order,
                line_number=idx,
                **line_data
            )

        return work_order


class DefectToWorkOrderSerializer(serializers.Serializer):
    """Serializer for converting defect to work order."""

    defect_id = serializers.UUIDField(required=True)
    department_id = serializers.UUIDField(required=False, allow_null=True)
    auto_approve = serializers.BooleanField(default=False)

    def validate_defect_id(self, value):
        """Validate defect exists."""
        from apps.inspections.models import InspectionDefect

        try:
            InspectionDefect.objects.get(id=value)
        except InspectionDefect.DoesNotExist:
            raise serializers.ValidationError(f"Defect {value} not found")

        return value

    def validate_department_id(self, value):
        """Validate department exists if provided."""
        if value:
            try:
                Department.objects.get(id=value)
            except Department.DoesNotExist:
                raise serializers.ValidationError(f"Department {value} not found")

        return value


class InspectionToWorkOrdersSerializer(serializers.Serializer):
    """Serializer for generating work orders from inspection."""

    inspection_id = serializers.UUIDField(required=True)
    group_by_location = serializers.BooleanField(default=True)
    min_severity = serializers.ChoiceField(
        choices=['ADVISORY', 'MINOR', 'MAJOR', 'CRITICAL'],
        required=False,
        allow_null=True
    )
    department_id = serializers.UUIDField(required=False, allow_null=True)
    auto_approve = serializers.BooleanField(default=False)

    def validate_inspection_id(self, value):
        """Validate inspection exists."""
        from apps.inspections.models import InspectionRun

        try:
            InspectionRun.objects.get(id=value)
        except InspectionRun.DoesNotExist:
            raise serializers.ValidationError(f"Inspection {value} not found")

        return value

    def validate_department_id(self, value):
        """Validate department exists if provided."""
        if value:
            try:
                Department.objects.get(id=value)
            except Department.DoesNotExist:
                raise serializers.ValidationError(f"Department {value} not found")

        return value


class VocabularySerializer(serializers.Serializer):
    """Serializer for vocabulary catalog."""

    verbs = serializers.ListField(child=serializers.DictField(), read_only=True)
    nouns = serializers.ListField(child=serializers.DictField(), read_only=True)
    service_locations = serializers.ListField(child=serializers.DictField(), read_only=True)
    noun_categories = serializers.ListField(child=serializers.DictField(), read_only=True)
    location_categories = serializers.ListField(child=serializers.DictField(), read_only=True)


class VocabularySuggestionSerializer(serializers.Serializer):
    """Serializer for vocabulary suggestion request."""

    description = serializers.CharField(required=True)

    def validate_description(self, value):
        """Validate description is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty")
        return value
