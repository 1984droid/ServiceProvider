"""
DRF Serializers for Customer Management

Serializers for:
- Customer (with nested contacts)
- Contact (standalone and nested)
- USDOTProfile (for FMCSA lookup data)
"""

from rest_framework import serializers
from .models import Customer, Contact, USDOTProfile


class ContactListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing contacts"""
    is_primary = serializers.BooleanField(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Contact
        fields = [
            'id',
            'full_name',
            'first_name',
            'last_name',
            'title',
            'email',
            'phone',
            'mobile',
            'is_primary',
            'is_automated',
            'is_active',
        ]
        read_only_fields = ['id', 'is_primary', 'full_name']


class ContactDetailSerializer(serializers.ModelSerializer):
    """Full serializer for contact CRUD operations"""
    is_primary = serializers.BooleanField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = Contact
        fields = [
            'id',
            'customer',
            'customer_name',
            'full_name',
            'first_name',
            'last_name',
            'title',
            'email',
            'phone',
            'phone_extension',
            'mobile',
            'is_active',
            'is_automated',
            'is_primary',
            'receive_invoices',
            'receive_estimates',
            'receive_service_updates',
            'receive_inspection_reports',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'is_primary', 'full_name', 'customer_name', 'created_at', 'updated_at']

    def validate_email(self, value):
        """Ensure email is valid and lowercase"""
        if value:
            return value.lower().strip()
        return value

    def validate(self, data):
        """
        Business logic validation:
        - Automated contacts should have email
        - At least one correspondence preference should be enabled for non-automated contacts
        """
        if data.get('is_automated') and not data.get('email'):
            raise serializers.ValidationError({
                'email': 'Automated contacts must have an email address'
            })

        # Check if at least one correspondence preference is enabled
        if not data.get('is_automated'):
            correspondence_fields = [
                'receive_invoices',
                'receive_estimates',
                'receive_service_updates',
                'receive_inspection_reports'
            ]
            if not any(data.get(field) for field in correspondence_fields):
                raise serializers.ValidationError({
                    'correspondence': 'At least one correspondence preference should be enabled'
                })

        return data


class USDOTProfileSerializer(serializers.ModelSerializer):
    """Serializer for FMCSA carrier lookup data"""

    class Meta:
        model = USDOTProfile
        fields = [
            'id',
            'customer',
            'usdot_number',
            'mc_number',
            'legal_name',
            'dba_name',
            'physical_address_line1',
            'physical_address_line2',
            'physical_city',
            'physical_state',
            'physical_postal_code',
            'mailing_address_line1',
            'mailing_address_line2',
            'mailing_city',
            'mailing_state',
            'mailing_postal_code',
            'phone',
            'email',
            'safety_rating',
            'safety_rating_date',
            'total_power_units',
            'total_drivers',
            'raw_fmcsa_data',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_usdot_number(self, value):
        """Ensure USDOT number is clean"""
        if value:
            # Remove any non-alphanumeric characters
            return ''.join(c for c in value if c.isalnum())
        return value


class CustomerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing customers"""
    primary_contact_name = serializers.SerializerMethodField()
    contact_count = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id',
            'name',
            'legal_name',
            'city',
            'state',
            'usdot_number',
            'mc_number',
            'is_active',
            'primary_contact_name',
            'contact_count',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_primary_contact_name(self, obj):
        """Get primary contact full name"""
        if obj.primary_contact:
            return obj.primary_contact.full_name
        return None

    def get_contact_count(self, obj):
        """Get total contact count"""
        return obj.contacts.count()


class CustomerDetailSerializer(serializers.ModelSerializer):
    """Full serializer for customer CRUD operations with nested contacts"""
    contacts = ContactListSerializer(many=True, read_only=True)
    primary_contact_name = serializers.SerializerMethodField()
    usdot_profile = USDOTProfileSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id',
            'name',
            'legal_name',
            'address_line1',
            'address_line2',
            'city',
            'state',
            'postal_code',
            'country',
            'usdot_number',
            'mc_number',
            'is_active',
            'notes',
            'primary_contact',
            'primary_contact_name',
            'contacts',
            'usdot_profile',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'primary_contact_name', 'created_at', 'updated_at']

    def get_primary_contact_name(self, obj):
        """Get primary contact full name"""
        if obj.primary_contact:
            return obj.primary_contact.full_name
        return None

    def validate_primary_contact(self, value):
        """Ensure primary contact belongs to this customer"""
        if value:
            # For creation, we can't validate yet
            if not self.instance:
                return value

            # For updates, validate that contact belongs to customer
            if value.customer_id != self.instance.id:
                raise serializers.ValidationError(
                    'Primary contact must belong to this customer'
                )
        return value

    def validate_usdot_number(self, value):
        """Ensure USDOT number is clean and unique"""
        if value:
            # Remove any non-alphanumeric characters
            clean_value = ''.join(c for c in value if c.isalnum())

            # Check uniqueness
            qs = Customer.objects.filter(usdot_number=clean_value)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)

            if qs.exists():
                raise serializers.ValidationError(
                    f'Customer with USDOT number {clean_value} already exists'
                )

            return clean_value
        return value

    def validate_mc_number(self, value):
        """Ensure MC number is clean"""
        if value:
            return ''.join(c for c in value if c.isalnum())
        return value

    def validate(self, data):
        """
        Business logic validation:
        - Must have either name or legal_name
        - If setting primary_contact, it must exist and belong to customer
        """
        # Check that we have at least a name
        if not data.get('name') and not data.get('legal_name'):
            raise serializers.ValidationError({
                'name': 'Either name or legal_name must be provided'
            })

        # Auto-fill name from legal_name if not provided
        if not data.get('name') and data.get('legal_name'):
            data['name'] = data['legal_name']

        return data


class CustomerCreateSerializer(serializers.ModelSerializer):
    """
    Specialized serializer for customer creation
    Allows creating customer with initial contacts
    """
    initial_contact = ContactDetailSerializer(write_only=True, required=False)

    class Meta:
        model = Customer
        fields = [
            'id',
            'name',
            'legal_name',
            'address_line1',
            'address_line2',
            'city',
            'state',
            'postal_code',
            'country',
            'usdot_number',
            'mc_number',
            'is_active',
            'notes',
            'initial_contact',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create customer and optionally create initial contact"""
        initial_contact_data = validated_data.pop('initial_contact', None)

        # Create customer
        customer = Customer.objects.create(**validated_data)

        # Create initial contact if provided
        if initial_contact_data:
            contact = Contact.objects.create(
                customer=customer,
                **initial_contact_data
            )
            # Set as primary contact
            customer.primary_contact = contact
            customer.save(update_fields=['primary_contact', 'updated_at'])

        return customer
