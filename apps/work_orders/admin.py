"""
Work Order Admin Interfaces

Django admin configuration for work order models.
Built clean - no legacy compatibility.
"""

from django.contrib import admin
from .models import WorkOrder, WorkOrderDefect


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    """Admin interface for WorkOrder model."""

    list_display = [
        'work_order_number',
        'customer',
        'asset_type',
        'status',
        'priority',
        'source',
        'scheduled_date',
        'assigned_to',
    ]

    list_filter = [
        'status',
        'priority',
        'source',
        'asset_type',
        'scheduled_date',
        'created_at',
    ]

    search_fields = [
        'work_order_number',
        'customer__name',
        'description',
        'assigned_to',
        'notes',
    ]

    readonly_fields = [
        'id',
        'work_order_number',
        'created_at',
        'updated_at',
        'defect_count',
    ]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'work_order_number', 'created_at', 'updated_at')
        }),
        ('Asset Reference', {
            'fields': ('customer', 'asset_type', 'asset_id')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Source', {
            'fields': ('source', 'source_inspection_run')
        }),
        ('Work Details', {
            'fields': ('description', 'notes')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'assigned_to')
        }),
        ('Execution', {
            'fields': ('started_at', 'completed_at')
        }),
        ('Meter Readings', {
            'fields': ('odometer_at_service', 'engine_hours_at_service')
        }),
        ('Statistics', {
            'fields': ('defect_count',)
        }),
    )

    def defect_count(self, obj):
        """Display linked defect count."""
        return obj.defect_count
    defect_count.short_description = 'Linked Defects'


@admin.register(WorkOrderDefect)
class WorkOrderDefectAdmin(admin.ModelAdmin):
    """Admin interface for WorkOrderDefect junction model."""

    list_display = [
        'work_order',
        'defect',
        'linked_at',
    ]

    list_filter = [
        'linked_at',
    ]

    search_fields = [
        'work_order__work_order_number',
        'defect__title',
    ]

    readonly_fields = [
        'linked_at',
    ]

    fieldsets = (
        ('Link', {
            'fields': ('work_order', 'defect')
        }),
        ('Audit', {
            'fields': ('linked_at',)
        }),
    )
