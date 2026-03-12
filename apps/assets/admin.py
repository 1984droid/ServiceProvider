from django.contrib import admin
from django.utils.html import format_html
from .models import Vehicle, Equipment, VINDecodeData


class VINDecodeDataInline(admin.StackedInline):
    """Inline for VIN decode data under vehicle"""
    model = VINDecodeData
    extra = 0
    can_delete = False
    fields = [
        'vin', 'model_year', 'make', 'model', 'manufacturer',
        'vehicle_type', 'body_class',
        'engine_model', 'fuel_type_primary',
        'gvwr', 'decoded_at', 'error_code'
    ]
    readonly_fields = ['vin', 'decoded_at']
    classes = ['collapse']


class EquipmentInline(admin.TabularInline):
    """Inline for equipment mounted on vehicle"""
    model = Equipment
    extra = 0
    fk_name = 'mounted_on_vehicle'
    fields = ['serial_number', 'asset_number', 'equipment_type', 'manufacturer', 'is_active']
    readonly_fields = []
    classes = ['collapse']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['unit_or_vin', 'customer', 'year', 'make', 'model', 'body_type', 'license_plate', 'equipment_count', 'capability_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'body_type', 'make', 'year', 'created_at']
    search_fields = ['vin', 'unit_number', 'make', 'model', 'license_plate', 'customer__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'equipment_count_display', 'vin_decode_status']
    autocomplete_fields = ['customer']
    inlines = [VINDecodeDataInline, EquipmentInline]

    fieldsets = (
        ('Identity', {
            'fields': ('customer', 'vin', 'unit_number', 'is_active')
        }),
        ('Vehicle Info', {
            'fields': ('year', 'make', 'model', 'body_type', 'license_plate')
        }),
        ('Meters', {
            'fields': ('odometer_miles', 'engine_hours')
        }),
        ('Capabilities', {
            'fields': ('capabilities',),
            'description': 'Vehicle capabilities (usually from VIN decode) - only set if affects inspection/maintenance'
        }),
        ('VIN Decode', {
            'fields': ('vin_decode_status',),
            'description': 'VIN decode data is managed in the VIN Decode Data section below'
        }),
        ('Equipment', {
            'fields': ('equipment_count_display',),
            'description': 'Equipment mounted on this vehicle'
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def unit_or_vin(self, obj):
        """Display unit number or VIN"""
        return obj.unit_number or obj.vin[:8] + '...' if obj.vin else '-'
    unit_or_vin.short_description = 'Unit/VIN'

    def equipment_count(self, obj):
        """Display equipment count in list"""
        return obj.equipment.count()
    equipment_count.short_description = 'Equipment'

    def equipment_count_display(self, obj):
        """Display equipment count in detail view"""
        if obj.pk:
            count = obj.equipment.count()
            active_count = obj.equipment.filter(is_active=True).count()
            return f"{active_count} active / {count} total mounted equipment"
        return "Save vehicle first to add equipment"
    equipment_count_display.short_description = 'Equipment Count'

    def capability_display(self, obj):
        """Display capabilities as comma-separated list"""
        if obj.capabilities:
            return ', '.join(obj.capabilities[:3]) + ('...' if len(obj.capabilities) > 3 else '')
        return '-'
    capability_display.short_description = 'Capabilities'

    def vin_decode_status(self, obj):
        """Display VIN decode status"""
        if hasattr(obj, 'vin_decode') and obj.vin_decode:
            decode = obj.vin_decode
            if decode.error_code and decode.error_code != '0':
                return format_html('<span style="color: red;">Error: {}</span>', decode.error_text or 'Unknown error')
            return format_html(
                '<span style="color: green;">✓ Decoded</span> - {} {} {} ({})',
                decode.model_year or '?',
                decode.make or '?',
                decode.model or '?',
                decode.decoded_at.strftime('%Y-%m-%d') if decode.decoded_at else '?'
            )
        return format_html('<span style="color: orange;">Not decoded</span>')
    vin_decode_status.short_description = 'VIN Decode Status'


@admin.register(VINDecodeData)
class VINDecodeDataAdmin(admin.ModelAdmin):
    list_display = ['vin', 'vehicle_link', 'model_year', 'make', 'model', 'vehicle_type', 'decoded_at', 'error_indicator']
    list_filter = ['decoded_at', 'make', 'model_year', 'vehicle_type', 'fuel_type_primary']
    search_fields = ['vin', 'make', 'model', 'manufacturer', 'vehicle__unit_number']
    readonly_fields = ['id', 'decoded_at', 'created_at', 'updated_at']
    autocomplete_fields = ['vehicle']

    fieldsets = (
        ('Vehicle', {
            'fields': ('vehicle', 'vin')
        }),
        ('Core Info', {
            'fields': ('model_year', 'make', 'model', 'manufacturer')
        }),
        ('Classification', {
            'fields': ('vehicle_type', 'body_class')
        }),
        ('Engine & Drivetrain', {
            'fields': ('engine_model', 'engine_configuration', 'engine_cylinders', 'displacement_liters', 'fuel_type_primary', 'fuel_type_secondary'),
            'classes': ('collapse',)
        }),
        ('Ratings & Capacity', {
            'fields': ('gvwr', 'gvwr_min_lbs', 'gvwr_max_lbs'),
            'classes': ('collapse',)
        }),
        ('Safety & Equipment', {
            'fields': ('abs', 'airbag_locations'),
            'classes': ('collapse',)
        }),
        ('Manufacturing', {
            'fields': ('plant_city', 'plant_state', 'plant_country'),
            'classes': ('collapse',)
        }),
        ('Decode Status', {
            'fields': ('error_code', 'error_text', 'decoded_at')
        }),
        ('Raw Data', {
            'fields': ('raw_response',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def vehicle_link(self, obj):
        """Display vehicle with link"""
        if obj.vehicle:
            unit = obj.vehicle.unit_number or obj.vehicle.vin[:8]
            return format_html(
                '<a href="/admin/assets/vehicle/{}/change/">{}</a>',
                obj.vehicle.id,
                unit
            )
        return '-'
    vehicle_link.short_description = 'Vehicle'

    def error_indicator(self, obj):
        """Display error status"""
        if obj.error_code and obj.error_code != '0':
            return format_html('<span style="color: red;">✗ Error</span>')
        return format_html('<span style="color: green;">✓ OK</span>')
    error_indicator.short_description = 'Status'


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['asset_or_serial', 'customer', 'equipment_type', 'manufacturer', 'model', 'mounted_on_link', 'capability_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'equipment_type', 'manufacturer', 'created_at']
    search_fields = ['serial_number', 'asset_number', 'equipment_type', 'manufacturer', 'model', 'customer__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'required_data_display']
    autocomplete_fields = ['customer', 'mounted_on_vehicle']

    fieldsets = (
        ('Identity', {
            'fields': ('customer', 'serial_number', 'asset_number', 'is_active')
        }),
        ('Classification', {
            'fields': ('equipment_type', 'manufacturer', 'model', 'year')
        }),
        ('Vehicle Relationship', {
            'fields': ('mounted_on_vehicle',),
            'description': 'For equipment mounted on vehicles (aerial devices, cranes, etc.)'
        }),
        ('Capabilities & Data', {
            'fields': ('capabilities', 'equipment_data', 'required_data_display'),
            'description': 'Capabilities determine which inspections/tests are required and what data needs to be collected'
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def asset_or_serial(self, obj):
        """Display asset number or serial"""
        return obj.asset_number or obj.serial_number[:12] + '...' if len(obj.serial_number) > 12 else obj.serial_number
    asset_or_serial.short_description = 'Asset/Serial'

    def mounted_on_link(self, obj):
        """Display mounted vehicle with link"""
        if obj.mounted_on_vehicle:
            unit = obj.mounted_on_vehicle.unit_number or obj.mounted_on_vehicle.vin[:8]
            return format_html(
                '<a href="/admin/assets/vehicle/{}/change/">{}</a>',
                obj.mounted_on_vehicle.id,
                unit
            )
        return '-'
    mounted_on_link.short_description = 'Mounted On'

    def capability_display(self, obj):
        """Display capabilities as comma-separated list"""
        if obj.capabilities:
            return ', '.join(obj.capabilities[:3]) + ('...' if len(obj.capabilities) > 3 else '')
        return '-'
    capability_display.short_description = 'Capabilities'

    def required_data_display(self, obj):
        """Display what data fields are required based on capabilities"""
        if not obj.capabilities:
            return "No capabilities set - no additional data required"

        required = []
        if 'DIELECTRIC' in obj.capabilities:
            required.append("Dielectric test data (rating, test dates, certificate)")
        if 'HYDRAULIC' in obj.capabilities:
            required.append("Hydraulic data (fluid type, reservoir capacity, service dates)")
        if 'PNEUMATIC' in obj.capabilities:
            required.append("Pneumatic data (max pressure, compressor type)")

        if required:
            return format_html('<br>'.join(required))
        return "No additional data required for current capabilities"
    required_data_display.short_description = 'Required Data Fields'
