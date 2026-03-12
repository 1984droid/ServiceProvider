"""
Inspection Admin Interfaces

Django admin configuration for inspection models.
Built clean - no legacy compatibility.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from .models import InspectionRun, InspectionDefect
from .services.runtime_service import InspectionRuntime
import json


class InspectionDefectInline(admin.TabularInline):
    """Inline defect display on InspectionRun detail page."""
    model = InspectionDefect
    extra = 0
    can_delete = False
    show_change_link = True

    fields = ['severity_badge', 'status', 'title', 'step_key', 'rule_id', 'created_at']
    readonly_fields = ['severity_badge', 'status', 'title', 'step_key', 'rule_id', 'created_at']

    def severity_badge(self, obj):
        """Display severity with color coding."""
        colors = {
            'CRITICAL': '#dc3545',  # Red
            'MAJOR': '#fd7e14',     # Orange
            'MINOR': '#ffc107',     # Yellow
            'ADVISORY': '#17a2b8'   # Teal
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'

    def has_add_permission(self, request, obj=None):
        """Prevent manual defect creation - only through rules."""
        return False


@admin.register(InspectionRun)
class InspectionRunAdmin(admin.ModelAdmin):
    """Admin interface for InspectionRun model."""

    inlines = [InspectionDefectInline]

    list_display = [
        'id',
        'template_key',
        'asset_display',
        'customer',
        'status_badge',
        'completion_display',
        'defects_badge',
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
        'defect_summary_display',
        'completion_status_display',
        'template_snapshot',
        'step_data',
    ]

    actions = ['evaluate_rules_action']

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'created_at', 'updated_at')
        }),
        ('Asset Reference', {
            'fields': ('asset_type', 'asset_id', 'customer')
        }),
        ('Template', {
            'fields': ('template_key', 'program_key')
        }),
        ('Status', {
            'fields': ('status', 'started_at', 'finalized_at', 'completion_status_display')
        }),
        ('Inspector', {
            'fields': ('inspector_name', 'inspector_signature')
        }),
        ('Data', {
            'fields': ('step_data', 'template_snapshot', 'notes'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('defect_summary_display',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Make fields read-only if inspection is finalized."""
        readonly = list(self.readonly_fields)
        if obj and obj.is_finalized:
            # All fields readonly when finalized
            readonly.extend(['asset_type', 'asset_id', 'customer', 'template_key',
                           'program_key', 'status', 'inspector_name', 'inspector_signature', 'notes'])
        return readonly

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of finalized inspections."""
        if obj and obj.is_finalized:
            return False
        return super().has_delete_permission(request, obj)

    def asset_display(self, obj):
        """Display asset information."""
        try:
            asset = obj.asset
            if obj.asset_type == 'VEHICLE':
                return f"Vehicle: {asset.vin} ({asset.year} {asset.make} {asset.model})"
            else:
                return f"Equipment: {asset.serial_number} ({asset.equipment_type})"
        except Exception:
            return f"{obj.asset_type}: {obj.asset_id}"
    asset_display.short_description = 'Asset'

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'DRAFT': 'gray',
            'IN_PROGRESS': 'blue',
            'COMPLETED': 'green'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def completion_display(self, obj):
        """Display completion percentage."""
        try:
            completion = InspectionRuntime.calculate_completion_status(obj)
            percentage = completion.completion_percentage
            color = 'green' if percentage == 100 else 'orange' if percentage >= 50 else 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}%</span>',
                color,
                int(percentage)
            )
        except Exception:
            return '—'
    completion_display.short_description = 'Progress'

    def completion_status_display(self, obj):
        """Display detailed completion status."""
        try:
            completion = InspectionRuntime.calculate_completion_status(obj)
            return format_html(
                '<strong>Progress:</strong> {}/{} steps completed ({}%)<br>'
                '<strong>Required:</strong> {}/{} required steps<br>'
                '<strong>Ready to finalize:</strong> {}<br>'
                '<strong>Missing:</strong> {}',
                completion.completed_steps,
                completion.total_steps,
                int(completion.completion_percentage),
                completion.required_completed,
                completion.required_steps,
                'Yes' if completion.ready_to_finalize else 'No',
                ', '.join(completion.missing_required_steps) if completion.missing_required_steps else 'None'
            )
        except Exception as e:
            return format_html('<span style="color: red;">Error: {}</span>', str(e))
    completion_status_display.short_description = 'Completion Status'

    def defect_count(self, obj):
        """Display defect count."""
        return obj.defect_count
    defect_count.short_description = 'Total Defects'

    def defects_badge(self, obj):
        """Display defect summary badge."""
        total = obj.defect_count
        critical = obj.critical_defect_count

        if total == 0:
            return format_html('<span style="color: green;">✓ None</span>')

        if critical > 0:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">{} total ({} critical)</span>',
                total, critical
            )
        return format_html('<span style="color: orange;">{} total</span>', total)
    defects_badge.short_description = 'Defects'

    def defect_summary_display(self, obj):
        """Display detailed defect summary."""
        from .services.defect_generator import DefectGenerator
        try:
            summary = DefectGenerator.get_defect_summary(obj)

            if summary['total_defects'] == 0:
                return format_html('<p style="color: green; font-weight: bold;">✓ No defects found</p>')

            severity_rows = []
            severity_order = ['CRITICAL', 'MAJOR', 'MINOR', 'ADVISORY']
            colors = {
                'CRITICAL': '#dc3545',
                'MAJOR': '#fd7e14',
                'MINOR': '#ffc107',
                'ADVISORY': '#17a2b8'
            }

            for severity in severity_order:
                count = summary['by_severity'].get(severity, 0)
                if count > 0:
                    color = colors.get(severity, 'gray')
                    severity_rows.append(
                        f'<span style="background-color: {color}; color: white; '
                        f'padding: 2px 8px; border-radius: 3px; font-size: 11px; '
                        f'margin-right: 5px;">{severity}: {count}</span>'
                    )

            return format_html(
                '<p><strong>Total Defects:</strong> {}</p>'
                '<p>{}</p>'
                '<p><strong>Open:</strong> {} | <strong>Work Order Created:</strong> {} | <strong>Resolved:</strong> {}</p>',
                summary['total_defects'],
                format_html(' '.join(severity_rows)),
                summary['by_status'].get('OPEN', 0),
                summary['by_status'].get('WORK_ORDER_CREATED', 0),
                summary['by_status'].get('RESOLVED', 0)
            )
        except Exception as e:
            return format_html('<span style="color: red;">Error loading defect summary: {}</span>', str(e))
    defect_summary_display.short_description = 'Defect Summary'

    def evaluate_rules_action(self, request, queryset):
        """Admin action to re-evaluate rules for selected inspections."""
        success_count = 0
        defect_count = 0

        for inspection in queryset:
            if inspection.is_finalized:
                self.message_user(
                    request,
                    f"Cannot re-evaluate finalized inspection {inspection.id}",
                    level=messages.WARNING
                )
                continue

            try:
                defects = InspectionRuntime.evaluate_rules(inspection)
                success_count += 1
                defect_count += len(defects)
            except Exception as e:
                self.message_user(
                    request,
                    f"Error evaluating {inspection.id}: {str(e)}",
                    level=messages.ERROR
                )

        if success_count > 0:
            self.message_user(
                request,
                f"Successfully evaluated {success_count} inspection(s), generated/updated {defect_count} defect(s)",
                level=messages.SUCCESS
            )
    evaluate_rules_action.short_description = "Re-evaluate rules for selected inspections"


@admin.register(InspectionDefect)
class InspectionDefectAdmin(admin.ModelAdmin):
    """Admin interface for InspectionDefect model."""

    list_display = [
        'id',
        'inspection_run',
        'severity_badge',
        'status_badge',
        'title',
        'step_key',
        'rule_id',
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
        'severity_badge',
        'status_badge',
        'evaluation_trace_display',
        'defect_details_display',
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
            'fields': ('severity', 'severity_badge', 'status', 'status_badge')
        }),
        ('Details', {
            'fields': ('title', 'description', 'defect_details_display')
        }),
        ('Audit Trail', {
            'fields': ('evaluation_trace_display',),
            'classes': ('collapse',)
        }),
    )

    def severity_badge(self, obj):
        """Display severity with color coding."""
        colors = {
            'CRITICAL': '#dc3545',
            'MAJOR': '#fd7e14',
            'MINOR': '#ffc107',
            'ADVISORY': '#17a2b8'
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; '
            'border-radius: 3px; font-size: 12px; font-weight: bold;">{}</span>',
            color,
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'

    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            'OPEN': '#6c757d',
            'WORK_ORDER_CREATED': '#007bff',
            'RESOLVED': '#28a745'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def evaluation_trace_display(self, obj):
        """Display evaluation trace as formatted JSON."""
        if not obj.evaluation_trace:
            return format_html('<p style="color: gray; font-style: italic;">No evaluation trace available</p>')

        try:
            trace_json = json.dumps(obj.evaluation_trace, indent=2)
            return format_html(
                '<details>'
                '<summary style="cursor: pointer; font-weight: bold; color: #007bff;">Click to view evaluation trace</summary>'
                '<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 4px; '
                'border: 1px solid #dee2e6; overflow-x: auto; font-size: 12px;">{}</pre>'
                '</details>',
                trace_json
            )
        except Exception as e:
            return format_html('<span style="color: red;">Error formatting trace: {}</span>', str(e))
    evaluation_trace_display.short_description = 'Evaluation Trace'

    def defect_details_display(self, obj):
        """Display defect details as formatted JSON."""
        if not obj.defect_details:
            return format_html('<p style="color: gray; font-style: italic;">No additional details</p>')

        try:
            details_json = json.dumps(obj.defect_details, indent=2)
            return format_html(
                '<details>'
                '<summary style="cursor: pointer; font-weight: bold; color: #007bff;">Click to view details</summary>'
                '<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 4px; '
                'border: 1px solid #dee2e6; overflow-x: auto; font-size: 12px;">{}</pre>'
                '</details>',
                details_json
            )
        except Exception as e:
            return format_html('<span style="color: red;">Error formatting details: {}</span>', str(e))
    defect_details_display.short_description = 'Defect Details'
