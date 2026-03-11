from django.contrib import admin
from .models import Vehicle, Equipment


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'customer', 'vin', 'unit_number', 'year', 'make', 'model', 'is_active', 'created_at']
    list_filter = ['is_active', 'vehicle_type', 'make', 'year', 'created_at']
    search_fields = ['vin', 'unit_number', 'make', 'model', 'customer__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'vin_decode_date']
    autocomplete_fields = ['customer']

    fieldsets = (
        ('Identity', {
            'fields': ('customer', 'vin', 'unit_number', 'is_active')
        }),
        ('Vehicle Info', {
            'fields': ('year', 'make', 'model', 'vehicle_type')
        }),
        ('Meters', {
            'fields': ('odometer_miles', 'engine_hours')
        }),
        ('VIN Decode', {
            'fields': ('vin_decode_data', 'vin_decode_date'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'customer', 'serial_number', 'asset_number', 'equipment_type', 'mounted_on_vehicle', 'is_active', 'created_at']
    list_filter = ['is_active', 'equipment_type', 'manufacturer', 'created_at']
    search_fields = ['serial_number', 'asset_number', 'equipment_type', 'manufacturer', 'model', 'customer__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['customer', 'mounted_on_vehicle']

    fieldsets = (
        ('Identity', {
            'fields': ('customer', 'serial_number', 'asset_number', 'is_active')
        }),
        ('Classification', {
            'fields': ('equipment_type', 'manufacturer', 'model', 'year')
        }),
        ('Meters', {
            'fields': ('engine_hours', 'cycles')
        }),
        ('Vehicle Relationship', {
            'fields': ('mounted_on_vehicle', 'mount_date'),
            'description': 'For equipment mounted on vehicles (aerial devices, cranes, etc.)'
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
