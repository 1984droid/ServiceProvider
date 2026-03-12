"""
Customer and Contact models for service provider application.

Design principles:
- Customer: Business entity only (NO contact info on customer directly)
- Contact: All communication details (multiple contacts per customer)
- USDOTProfile: 1:1 with Customer for FMCSA lookup data (pre-populated, then copied to Customer)
- Simple, focused, single-tenant
"""
from django.db import models
import uuid


class BaseModel(models.Model):
    """Abstract base model with UUID primary key and timestamps."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Customer(BaseModel):
    """
    Customer organization - the business entity we service.

    NO contact information on this model - use Contact model instead.
    This allows multiple contacts per customer with proper correspondence routing.
    """
    # Business Identity
    name = models.CharField(max_length=255, db_index=True, help_text="Business name (DBA)")
    legal_name = models.CharField(max_length=255, blank=True, help_text="Legal registered name")

    # Primary Contact (replaces Contact.is_primary boolean)
    primary_contact = models.ForeignKey(
        'Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_for_customers',
        help_text="Primary contact for this customer"
    )

    # Status
    is_active = models.BooleanField(default=True, db_index=True)

    # Business Address (physical location)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=2, blank=True, help_text="US state code")
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=2, default='US', help_text="ISO country code")

    # Regulatory Identifiers (transportation industry)
    usdot_number = models.CharField(
        max_length=20,
        blank=True,
        default='',
        db_index=True,
        help_text="US DOT Number"
    )
    mc_number = models.CharField(
        max_length=20,
        blank=True,
        default='',
        db_index=True,
        help_text="Motor Carrier Number"
    )

    # Internal Notes
    notes = models.TextField(blank=True, help_text="Internal notes about this customer")

    class Meta:
        db_table = 'customers'
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active', 'name']),
            models.Index(fields=['usdot_number']),
            models.Index(fields=['mc_number']),
            models.Index(fields=['primary_contact']),
        ]

    def clean(self):
        """Validate model fields."""
        from django.core.exceptions import ValidationError
        errors = {}

        # Name is required and has max length
        if not self.name:
            errors['name'] = 'This field is required'
        elif len(self.name) > 255:
            errors['name'] = 'Ensure this value has at most 255 characters'

        # State must be valid if provided
        if self.state:
            from tests.config import CONSTRAINTS
            valid_states = CONSTRAINTS.get('customer', {}).get('state', {}).get('valid_choices', [])
            if valid_states and self.state not in valid_states:
                errors['state'] = f'Invalid state: {self.state}'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Override save to call full_clean() first."""
        from django.core.exceptions import ValidationError

        # Skip validation if explicitly disabled
        if not kwargs.pop('skip_validation', False):
            try:
                self.full_clean()
            except ValidationError as e:
                # If it's a uniqueness error, let database handle it
                if any('already exists' in str(v) for v in e.message_dict.values()):
                    pass
                else:
                    raise
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def display_name(self):
        """Return name or legal_name for display."""
        return self.name or self.legal_name

    @property
    def full_address(self):
        """Return formatted full address."""
        parts = [self.address_line1, self.address_line2, self.city, self.state, self.postal_code]
        return ', '.join(filter(None, parts))


class USDOTProfile(BaseModel):
    """
    FMCSA carrier lookup data (1:1 with Customer).

    Workflow:
    1. User enters USDOT number
    2. Lookup FMCSA data → populate this model
    3. User reviews and creates Customer → copy data from USDOTProfile to Customer
    4. User can override any field during Customer creation

    This keeps lookup data separate from verified customer data.
    """
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='usdot_profile',
        help_text="Customer this profile belongs to"
    )

    # FMCSA Identifiers
    usdot_number = models.CharField(max_length=20, db_index=True, help_text="US DOT Number")
    mc_number = models.CharField(max_length=20, blank=True, help_text="Motor Carrier Number")

    # Business Info (from FMCSA)
    legal_name = models.CharField(max_length=255, blank=True)
    dba_name = models.CharField(max_length=255, blank=True, help_text="Doing Business As")
    entity_type = models.CharField(max_length=100, blank=True, help_text="LLC, Corporation, etc.")

    # Address (from FMCSA)
    physical_address = models.CharField(max_length=500, blank=True, default='')
    physical_city = models.CharField(max_length=100, blank=True, default='')
    physical_state = models.CharField(max_length=2, blank=True, default='')
    physical_zip = models.CharField(max_length=20, blank=True, default='')

    mailing_address = models.CharField(max_length=500, blank=True, default='')
    mailing_city = models.CharField(max_length=100, blank=True, default='')
    mailing_state = models.CharField(max_length=2, blank=True, default='')
    mailing_zip = models.CharField(max_length=20, blank=True, default='')

    # Contact from FMCSA
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)

    # Operational Data
    carrier_operation = models.CharField(max_length=100, blank=True, help_text="Interstate, Intrastate")
    cargo_carried = models.TextField(blank=True, help_text="Types of cargo")
    operation_classification = models.JSONField(
        default=list,
        blank=True,
        help_text="Authorized For Hire, Private, etc."
    )

    # Safety Data
    safety_rating = models.CharField(max_length=50, blank=True)
    out_of_service_date = models.DateField(null=True, blank=True)
    total_power_units = models.IntegerField(null=True, blank=True)
    total_drivers = models.IntegerField(null=True, blank=True)

    # Complete Raw FMCSA Response
    raw_fmcsa_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Complete FMCSA API response for reference"
    )

    # Lookup Metadata
    lookup_date = models.DateTimeField(auto_now=True, help_text="Last time FMCSA data was fetched")

    class Meta:
        db_table = 'usdot_profiles'
        indexes = [
            models.Index(fields=['usdot_number']),
            models.Index(fields=['mc_number']),
        ]

    def __str__(self):
        return f"USDOT Profile: {self.usdot_number} ({self.legal_name or 'Unknown'})"


class Contact(BaseModel):
    """
    Person at customer organization with communication preferences.

    This is where ALL contact information lives - phone, email, correspondence prefs.
    Multiple contacts per customer with role-based routing.

    Primary contact is designated at Customer.primary_contact_id FK (not boolean here).
    """
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='contacts',
        help_text="Customer organization this contact belongs to"
    )

    # Personal Info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True, help_text="Job title")

    # Contact Methods
    email = models.EmailField(blank=True, help_text="Email address")
    phone = models.CharField(max_length=50, blank=True, help_text="Primary phone")
    phone_extension = models.CharField(max_length=20, blank=True, help_text="Extension")
    mobile = models.CharField(max_length=50, blank=True, help_text="Mobile/cell phone")

    # Status and Type
    is_active = models.BooleanField(default=True, db_index=True)
    is_automated = models.BooleanField(
        default=False,
        help_text="Contact is an automated system (API, email processor, webhook, etc.)"
    )

    # Correspondence Preferences (what they should receive)
    receive_invoices = models.BooleanField(
        default=False,
        help_text="Receives invoices and billing statements"
    )
    receive_estimates = models.BooleanField(
        default=False,
        help_text="Receives quotes and estimates"
    )
    receive_service_updates = models.BooleanField(
        default=False,
        help_text="Receives work order and inspection updates"
    )
    receive_inspection_reports = models.BooleanField(
        default=False,
        help_text="Receives inspection reports and compliance notifications"
    )

    # Notes
    notes = models.TextField(blank=True, help_text="Notes about this contact")

    class Meta:
        db_table = 'contacts'
        ordering = ['customer', 'last_name', 'first_name']
        indexes = [
            models.Index(fields=['customer', 'is_active']),
            models.Index(fields=['email']),
            models.Index(fields=['is_automated']),
        ]

    def clean(self):
        """Validate model fields."""
        from django.core.exceptions import ValidationError
        errors = {}

        # Email required for automated contacts
        if self.is_automated and not self.email:
            errors['email'] = 'Automated contacts must have an email address'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Override save to call full_clean() first."""
        from django.core.exceptions import ValidationError

        # Skip validation if explicitly disabled
        if not kwargs.pop('skip_validation', False):
            try:
                self.full_clean()
            except ValidationError as e:
                # If it's a uniqueness error, let database handle it
                if any('already exists' in str(v) for v in e.message_dict.values()):
                    pass
                else:
                    raise
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.customer.name})"

    @property
    def full_name(self):
        """Return formatted full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def display_name_with_title(self):
        """Return name with title if available."""
        if self.title:
            return f"{self.full_name}, {self.title}"
        return self.full_name

    @property
    def is_primary(self):
        """Check if this contact is the primary contact for their customer."""
        return self.customer.primary_contact_id == self.id
