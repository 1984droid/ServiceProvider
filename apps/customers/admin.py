from django.contrib import admin
from django.utils.html import format_html
from .models import Customer, Contact, USDOTProfile


class ContactInline(admin.TabularInline):
    """Inline for managing contacts under customer"""
    model = Contact
    extra = 0
    fields = ['first_name', 'last_name', 'title', 'email', 'phone', 'is_active', 'is_automated']
    readonly_fields = []
    classes = ['collapse']


class USDOTProfileInline(admin.StackedInline):
    """Inline for USDOT profile under customer"""
    model = USDOTProfile
    extra = 0
    fields = [
        'usdot_number', 'mc_number', 'legal_name', 'dba_name',
        'phone', 'email', 'safety_rating', 'safety_rating_date'
    ]
    classes = ['collapse']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'usdot_number', 'mc_number', 'city', 'state', 'primary_contact_link', 'contact_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'state', 'created_at']
    search_fields = ['name', 'legal_name', 'usdot_number', 'mc_number', 'city']
    readonly_fields = ['id', 'created_at', 'updated_at', 'contact_count_display']
    autocomplete_fields = ['primary_contact']
    inlines = [ContactInline, USDOTProfileInline]

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
        ('Primary Contact', {
            'fields': ('primary_contact', 'contact_count_display'),
            'description': 'Set the primary contact for this customer. Contact must belong to this customer.'
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def contact_count(self, obj):
        """Display contact count in list"""
        count = obj.contacts.count()
        return count
    contact_count.short_description = 'Contacts'

    def contact_count_display(self, obj):
        """Display contact count in detail view"""
        if obj.pk:
            count = obj.contacts.count()
            active_count = obj.contacts.filter(is_active=True).count()
            return f"{active_count} active / {count} total"
        return "Save customer first to add contacts"
    contact_count_display.short_description = 'Contact Count'

    def primary_contact_link(self, obj):
        """Display primary contact with link"""
        if obj.primary_contact:
            return format_html(
                '<a href="/admin/customers/contact/{}/change/">{}</a>',
                obj.primary_contact.id,
                obj.primary_contact.full_name
            )
        return '-'
    primary_contact_link.short_description = 'Primary Contact'


@admin.register(USDOTProfile)
class USDOTProfileAdmin(admin.ModelAdmin):
    list_display = ['customer', 'usdot_number', 'legal_name', 'safety_rating', 'created_at']
    list_filter = ['safety_rating', 'created_at']
    search_fields = ['usdot_number', 'legal_name', 'dba_name', 'customer__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['customer']

    fieldsets = (
        ('Customer Link', {
            'fields': ('customer',)
        }),
        ('FMCSA Identity', {
            'fields': ('usdot_number', 'legal_name', 'dba_name')
        }),
        ('Physical Address', {
            'fields': ('physical_address_line1', 'physical_address_line2', 'physical_city', 'physical_state', 'physical_postal_code')
        }),
        ('Mailing Address', {
            'fields': ('mailing_address_line1', 'mailing_address_line2', 'mailing_city', 'mailing_state', 'mailing_postal_code')
        }),
        ('Contact Info', {
            'fields': ('phone', 'email')
        }),
        ('Safety Data', {
            'fields': ('safety_rating', 'safety_rating_date', 'total_power_units', 'total_drivers')
        }),
        ('Raw Data', {
            'fields': ('raw_fmcsa_data',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'customer', 'title', 'email', 'phone', 'is_primary', 'is_automated', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_automated', 'receive_invoices', 'receive_service_updates', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'customer__name']
    readonly_fields = ['id', 'is_primary', 'created_at', 'updated_at']
    autocomplete_fields = ['customer']

    fieldsets = (
        ('Personal Info', {
            'fields': ('customer', 'first_name', 'last_name', 'title')
        }),
        ('Contact Methods', {
            'fields': ('email', 'phone', 'phone_extension', 'mobile')
        }),
        ('Status', {
            'fields': ('is_active', 'is_automated'),
            'description': 'Note: is_primary is set at the Customer level (Customer.primary_contact)'
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
            'fields': ('id', 'is_primary', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
