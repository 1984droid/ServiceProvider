from django.contrib import admin
from .models import Customer, Contact


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'usdot_number', 'mc_number', 'city', 'state', 'is_active', 'created_at']
    list_filter = ['is_active', 'state', 'created_at']
    search_fields = ['name', 'legal_name', 'usdot_number', 'mc_number', 'city']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Business Identity', {
            'fields': ('name', 'legal_name', 'is_active')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Regulatory', {
            'fields': ('usdot_number', 'mc_number')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'customer', 'title', 'email', 'phone', 'is_primary', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_primary', 'receive_invoices', 'receive_service_updates', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'customer__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['customer']

    fieldsets = (
        ('Personal Info', {
            'fields': ('customer', 'first_name', 'last_name', 'title')
        }),
        ('Contact Methods', {
            'fields': ('email', 'phone', 'phone_extension', 'mobile')
        }),
        ('Status', {
            'fields': ('is_active', 'is_primary')
        }),
        ('Correspondence Preferences', {
            'fields': (
                'receive_invoices',
                'receive_estimates',
                'receive_service_updates',
                'receive_inspection_reports'
            )
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
