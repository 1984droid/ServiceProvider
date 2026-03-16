"""
Work Order Admin Interfaces

Django admin configuration for work order models (Phase 5).
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import WorkOrder, WorkOrderLine


class WorkOrderLineInline(admin.TabularInline):
    """Inline work order line display on WorkOrder detail page."""
    model = WorkOrderLine
    extra = 0
    can_delete = True
    show_change_link = True

    fields = [
        'line_number',
        'status_badge',
        'verb',
        'noun',
        'service_location',
        'description',
        'estimated_hours',
        'actual_hours',
        'assigned_to',
    ]
    readonly_fields = ['status_badge']

    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            'PENDING': 'gray',
            'IN_PROGRESS': 'blue',
            'COMPLETED': 'green',
            'ON_HOLD': 'orange',
            'CANCELLED': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 10px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    """Admin interface for WorkOrder model (Phase 5 enhanced)."""

    inlines = [WorkOrderLineInline]

    list_display = [
        'work_order_number',
        'customer',
        'asset_display',
        'status_badge',
        'approval_badge',
        'priority_badge',
        'source_type',
        'line_count',
        'scheduled_date',
        'assigned_to',
    ]

    list_filter = [
        'status',
        'priority',
        'approval_status',
        'source_type',
        'asset_type',
        'scheduled_date',
        'created_at',
    ]

    search_fields = [
        'work_order_number',
        'customer__name',
        'title',
        'description',
        'notes',
        'source_type',
    ]

    readonly_fields = [
        'id',
        'work_order_number',
        'created_at',
        'updated_at',
        'source_link',
        'line_count',
        'total_hours_display',
    ]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'work_order_number', 'created_at', 'updated_at')
        }),
        ('Asset Reference', {
            'fields': ('customer', 'asset_type', 'asset_id', 'department')
        }),
        ('Work Order Details', {
            'fields': ('title', 'description', 'notes')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Approval Workflow', {
            'fields': ('approval_status', 'approved_by', 'approved_at', 'rejected_reason')
        }),
        ('Source Tracking', {
            'fields': ('source_type', 'source_id', 'source_link')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'due_date', 'assigned_to')
        }),
        ('Execution', {
            'fields': ('started_at', 'completed_at')
        }),
        ('Meter Readings', {
            'fields': ('odometer_at_service', 'engine_hours_at_service')
        }),
        ('Statistics', {
            'fields': ('line_count', 'total_hours_display')
        }),
        ('Metadata', {
            'fields': ('is_active',)
        }),
    )

    def asset_display(self, obj):
        """Display asset information."""
        try:
            asset = obj.asset
            if obj.asset_type == 'VEHICLE':
                return f"Vehicle: {asset.vin}"
            else:
                return f"Equipment: {asset.serial_number}"
        except Exception:
            return f"{obj.asset_type}: {obj.asset_id}"
    asset_display.short_description = 'Asset'

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'DRAFT': 'gray',
            'PENDING': 'orange',
            'IN_PROGRESS': 'blue',
            'ON_HOLD': 'purple',
            'COMPLETED': 'green',
            'CANCELLED': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def approval_badge(self, obj):
        """Display approval status as colored badge."""
        colors = {
            'DRAFT': 'gray',
            'PENDING_APPROVAL': 'orange',
            'APPROVED': 'green',
            'REJECTED': 'red'
        }
        color = colors.get(obj.approval_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_approval_status_display()
        )
    approval_badge.short_description = 'Approval'

    def priority_badge(self, obj):
        """Display priority as colored badge."""
        colors = {
            'LOW': '#28a745',
            'NORMAL': '#17a2b8',
            'HIGH': '#ffc107',
            'EMERGENCY': '#dc3545'
        }
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'

    def source_link(self, obj):
        """Display clickable link to source object."""
        if not obj.source_id:
            return '—'

        if obj.source_type == 'INSPECTION_DEFECT':
            # Try to link to defect or inspection
            from apps.inspections.models import InspectionDefect, InspectionRun

            try:
                defect = InspectionDefect.objects.get(id=obj.source_id)
                url = reverse('admin:inspections_inspectiondefect_change', args=[defect.id])
                return format_html('<a href="{}">Defect: {}</a>', url, defect.title[:50])
            except InspectionDefect.DoesNotExist:
                pass

            try:
                inspection = InspectionRun.objects.get(id=obj.source_id)
                url = reverse('admin:inspections_inspectionrun_change', args=[inspection.id])
                return format_html('<a href="{}">Inspection: {}</a>', url, inspection.template_key)
            except InspectionRun.DoesNotExist:
                pass

        return format_html('<span style="color: gray;">{}: {}</span>', obj.source_type, obj.source_id)
    source_link.short_description = 'Source Link'

    def line_count(self, obj):
        """Display line count."""
        return obj.lines.count()
    line_count.short_description = 'Lines'

    def total_hours_display(self, obj):
        """Display total estimated and actual hours."""
        estimated = sum(line.estimated_hours or 0 for line in obj.lines.all())
        actual = sum(line.actual_hours or 0 for line in obj.lines.all())

        return format_html(
            '<strong>Estimated:</strong> {} hrs<br><strong>Actual:</strong> {} hrs',
            float(estimated),
            float(actual)
        )
    total_hours_display.short_description = 'Total Hours'


@admin.register(WorkOrderLine)
class WorkOrderLineAdmin(admin.ModelAdmin):
    """Admin interface for WorkOrderLine model."""

    list_display = [
        'id',
        'work_order',
        'line_number',
        'status_badge',
        'verb',
        'noun',
        'service_location',
        'estimated_hours',
        'actual_hours',
        'assigned_to',
    ]

    list_filter = [
        'status',
        'verb',
        'service_location',
        'created_at',
    ]

    search_fields = [
        'verb',
        'noun',
        'service_location',
        'description',
        'notes',
        'work_order__work_order_number',
    ]

    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'vocabulary_validation',
    ]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'created_at', 'updated_at')
        }),
        ('Work Order Link', {
            'fields': ('work_order', 'line_number')
        }),
        ('Task Definition (Vocabulary)', {
            'fields': ('verb', 'noun', 'service_location', 'description', 'vocabulary_validation')
        }),
        ('Time Tracking', {
            'fields': ('estimated_hours', 'actual_hours')
        }),
        ('Parts & Assignment', {
            'fields': ('parts_required', 'assigned_to')
        }),
        ('Status', {
            'fields': ('status', 'completed_at', 'completed_by')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            'PENDING': 'gray',
            'IN_PROGRESS': 'blue',
            'COMPLETED': 'green',
            'ON_HOLD': 'orange',
            'CANCELLED': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def vocabulary_validation(self, obj):
        """Display vocabulary validation status."""
        from apps.work_orders.services.vocabulary_service import VocabularyService

        try:
            is_valid = VocabularyService.validate_line_vocabulary(
                obj.verb,
                obj.noun,
                obj.service_location
            )

            if is_valid:
                return format_html('<span style="color: green; font-weight: bold;">✓ Valid</span>')
            else:
                return format_html(
                    '<span style="color: orange;">⚠ Not found in catalog '
                    '(verb: {}, noun: {}, location: {})</span>',
                    obj.verb,
                    obj.noun,
                    obj.service_location
                )
        except Exception as e:
            return format_html('<span style="color: red;">Error: {}</span>', str(e))
    vocabulary_validation.short_description = 'Vocabulary Validation'
