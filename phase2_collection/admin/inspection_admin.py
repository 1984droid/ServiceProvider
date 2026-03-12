"""
Inspection Admin Interfaces

Django admin configuration for inspection models.
Built clean - no legacy compatibility.
"""

from django.contrib import admin
from .models import InspectionRun, InspectionDefect


@admin.register(InspectionRun)
class InspectionRunAdmin(admin.ModelAdmin):
    """Admin interface for InspectionRun model."""

    list_display = [
        'id',
        'template_key',
        'asset_type',
        'customer',
        'status',
        'started_at',
        'finalized_at',
        'inspector_name',
    ]

    list_filter = [
        'status',
        'asset_type',
        'template_key',
        'started_at',
        'finalized_at',
    ]

    search_fields = [
        'id',
        'template_key',
        'customer__name',
        'inspector_name',
        'notes',
    ]

    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'defect_count',
        'critical_defect_count',
    ]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'created_at', 'updated_at')
        }),
        ('Asset Reference', {
            'fields': ('asset_type', 'asset_id', 'customer')
        }),
        ('Template', {
            'fields': ('template_key', 'program_key', 'template_snapshot')
        }),
        ('Status', {
            'fields': ('status', 'started_at', 'finalized_at')
        }),
        ('Inspector', {
            'fields': ('inspector_name', 'inspector_signature')
        }),
        ('Data', {
            'fields': ('step_data', 'notes')
        }),
        ('Statistics', {
            'fields': ('defect_count', 'critical_defect_count')
        }),
    )

    def defect_count(self, obj):
        """Display defect count."""
        return obj.defect_count
    defect_count.short_description = 'Total Defects'

    def critical_defect_count(self, obj):
        """Display critical defect count."""
        return obj.critical_defect_count
    critical_defect_count.short_description = 'Critical Defects'


@admin.register(InspectionDefect)
class InspectionDefectAdmin(admin.ModelAdmin):
    """Admin interface for InspectionDefect model."""

    list_display = [
        'id',
        'inspection_run',
        'severity',
        'status',
        'title',
        'module_key',
        'step_key',
        'created_at',
    ]

    list_filter = [
        'severity',
        'status',
        'module_key',
        'created_at',
    ]

    search_fields = [
        'id',
        'defect_identity',
        'title',
        'description',
        'module_key',
        'step_key',
        'rule_id',
    ]

    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'defect_identity',
    ]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'created_at', 'updated_at', 'defect_identity')
        }),
        ('Inspection Link', {
            'fields': ('inspection_run',)
        }),
        ('Location', {
            'fields': ('module_key', 'step_key', 'rule_id')
        }),
        ('Classification', {
            'fields': ('severity', 'status')
        }),
        ('Details', {
            'fields': ('title', 'description', 'defect_details')
        }),
        ('Audit', {
            'fields': ('evaluation_trace',)
        }),
    )
