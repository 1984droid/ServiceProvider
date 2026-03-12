"""
Asset models for service provider application.

Two asset types:
- Vehicle: VIN-based (trucks, trailers, etc.)
- Equipment: Serial number-based (aerial devices, cranes, generators, etc.)

Design principles:
- Separate models for clarity (not polymorphic)
- Customer-owned (not tenant-owned)
- Simple relationships (FK for mounted equipment)
- Minimal fields to start - add as needed
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


class VINDecodeData(BaseModel):
    """
    VIN decode data from NHTSA vPIC API.

    1:1 relationship with Vehicle. Stores structured decode results.
    NHTSA returns standardized fields - we capture what we can, leave rest null.
    """
    vehicle = models.OneToOneField(
        'Vehicle',
        on_delete=models.CASCADE,
        related_name='vin_decode',
        help_text="Vehicle this decode belongs to"
    )

    # Core Vehicle Info
    vin = models.CharField(max_length=17, db_index=True, help_text="VIN that was decoded")
    model_year = models.IntegerField(null=True, blank=True)
    make = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=200, blank=True, help_text="Full manufacturer name")

    # Classification
    vehicle_type = models.CharField(max_length=100, blank=True, help_text="Truck, Trailer, Passenger Car, etc.")
    body_class = models.CharField(max_length=100, blank=True, help_text="Cab & Chassis, Van, Pickup, etc.")

    # Engine & Drivetrain
    engine_model = models.CharField(max_length=100, blank=True)
    engine_configuration = models.CharField(max_length=50, blank=True)
    engine_cylinders = models.IntegerField(null=True, blank=True)
    displacement_liters = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fuel_type_primary = models.CharField(max_length=50, blank=True, help_text="Diesel, Gasoline, Electric, etc.")
    fuel_type_secondary = models.CharField(max_length=50, blank=True, help_text="For dual-fuel vehicles")

    # Ratings & Capacity
    gvwr = models.CharField(max_length=100, blank=True, help_text="Gross Vehicle Weight Rating")
    gvwr_min_lbs = models.IntegerField(null=True, blank=True, help_text="GVWR minimum in pounds")
    gvwr_max_lbs = models.IntegerField(null=True, blank=True, help_text="GVWR maximum in pounds")

    # Safety & Equipment
    abs = models.CharField(max_length=50, blank=True, help_text="Anti-lock Braking System")
    airbag_locations = models.CharField(max_length=200, blank=True)

    # Manufacturing
    plant_city = models.CharField(max_length=100, blank=True)
    plant_state = models.CharField(max_length=100, blank=True)
    plant_country = models.CharField(max_length=100, blank=True)

    # NHTSA Metadata
    error_code = models.CharField(max_length=10, blank=True, help_text="0 = success, other = error")
    error_text = models.TextField(blank=True, help_text="Any error message from NHTSA")
    decoded_at = models.DateTimeField(auto_now_add=True, help_text="When decode was performed")

    # Raw Response (for any fields we don't explicitly capture)
    raw_response = models.JSONField(
        null=True,
        blank=True,
        help_text="Complete raw JSON response from NHTSA for reference"
    )

    class Meta:
        db_table = 'vin_decode_data'
        verbose_name = 'VIN Decode Data'
        verbose_name_plural = 'VIN Decode Data'
        ordering = ['-decoded_at']
        indexes = [
            models.Index(fields=['vin']),
            models.Index(fields=['make', 'model']),
            models.Index(fields=['decoded_at']),
        ]

    def __str__(self):
        return f"VIN Decode: {self.vin} - {self.model_year} {self.make} {self.model}"


class Vehicle(BaseModel):
    """
    Vehicle asset (VIN-based).

    Examples: Trucks, tractors, trailers, vans, pickups
    """
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='vehicles',
        help_text="Customer that owns this vehicle"
    )

    # Identity
    vin = models.CharField(
        max_length=17,
        unique=True,
        db_index=True,
        help_text="17-character Vehicle Identification Number"
    )
    unit_number = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="Customer's internal unit/fleet number"
    )
    license_plate = models.CharField(
        max_length=20,
        blank=True,
        help_text="Current license plate number"
    )

    # Vehicle Info (from VIN decode or manual entry)
    year = models.IntegerField(null=True, blank=True, help_text="Model year")
    make = models.CharField(max_length=100, blank=True, db_index=True)
    model = models.CharField(max_length=100, blank=True)

    # Body Type (for incomplete vehicles with special bodies)
    BODY_TYPE_CHOICES = [
        ('', 'Standard (No Special Body)'),
        ('AERIAL', 'Aerial Device (Bucket Truck)'),
        # Add more as we create inspection templates for them:
        # ('REFUSE', 'Refuse/Garbage Body'),
        # ('SWEEPER', 'Street Sweeper'),
        # ('SCHOOL_BUS', 'School Bus'),
        # ('DUMP', 'Dump Body'),
        # ('TANK', 'Tank Body'),
        # ('TOW', 'Tow/Wrecker Body'),
    ]
    body_type = models.CharField(
        max_length=20,
        choices=BODY_TYPE_CHOICES,
        blank=True,
        default='',
        db_index=True,
        help_text="Special body type if vehicle is incomplete/upfitted (only add types we have inspection templates for)"
    )

    # Status
    is_active = models.BooleanField(default=True, db_index=True)

    # Operational Meters
    odometer_miles = models.IntegerField(
        null=True,
        blank=True,
        help_text="Current odometer reading in miles"
    )
    engine_hours = models.IntegerField(
        null=True,
        blank=True,
        help_text="Current engine hour meter reading"
    )

    # Capabilities - single source of truth for template applicability and vehicle features
    capabilities = models.JSONField(
        default=list,
        blank=True,
        help_text="Vehicle capabilities and features (e.g., ['UTILITY_TRUCK', 'INSULATED_BOOM', 'DIELECTRIC'])"
    )

    # Notes
    notes = models.TextField(blank=True, help_text="Internal notes")

    class Meta:
        db_table = 'vehicles'
        ordering = ['unit_number', '-year']
        indexes = [
            models.Index(fields=['customer', 'is_active']),
            models.Index(fields=['vin']),
            models.Index(fields=['unit_number']),
            models.Index(fields=['make', 'model']),
        ]

    def clean(self):
        """Validate model fields."""
        from django.core.exceptions import ValidationError
        errors = {}

        # VIN must be exactly 17 characters
        if self.vin and len(self.vin) != 17:
            errors['vin'] = 'VIN must be exactly 17 characters'

        # Odometer must be positive
        if self.odometer_miles is not None and self.odometer_miles < 0:
            errors['odometer_miles'] = 'Odometer reading must be positive'

        # Engine hours must be positive
        if self.engine_hours is not None and self.engine_hours < 0:
            errors['engine_hours'] = 'Engine hours must be positive'

        # Year must be in valid range if provided
        if self.year is not None:
            if self.year < 1900 or self.year > 2100:
                errors['year'] = 'Year must be between 1900 and 2100'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Override save to call full_clean() first."""
        from django.core.exceptions import ValidationError
        from django.db import IntegrityError as DBIntegrityError

        # Skip validation if explicitly disabled
        if not kwargs.pop('skip_validation', False):
            try:
                self.full_clean()
            except ValidationError as e:
                # If it's a uniqueness error, let database handle it (for tests expecting IntegrityError)
                if 'vin' in e.message_dict and 'already exists' in str(e.message_dict.get('vin', '')):
                    pass  # Let database raise IntegrityError
                else:
                    raise
        super().save(*args, **kwargs)

    def __str__(self):
        if self.unit_number:
            return f"#{self.unit_number} - {self.vin}"
        return f"{self.year} {self.make} {self.model} - {self.vin}"

    @property
    def display_name(self):
        """User-friendly display name."""
        parts = []
        if self.unit_number:
            parts.append(f"#{self.unit_number}")
        if self.year and self.make and self.model:
            parts.append(f"{self.year} {self.make} {self.model}")
        elif self.vin:
            parts.append(self.vin)
        return ' - '.join(parts) if parts else f"Vehicle {self.id}"

    @property
    def basic_info(self):
        """Return basic vehicle info string."""
        if self.year and self.make and self.model:
            return f"{self.year} {self.make} {self.model}"
        return "Unknown Vehicle"


class Equipment(BaseModel):
    """
    Equipment asset (serial number-based).

    Examples: Aerial devices, cranes, generators, compressors, test equipment
    Can be mounted on vehicles or standalone.
    """
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='equipment',
        help_text="Customer that owns this equipment"
    )

    # Identity
    serial_number = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Manufacturer serial number"
    )
    asset_number = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="Customer's internal asset/equipment number"
    )

    # Equipment Classification
    equipment_type = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Aerial Device, Crane, Generator, Compressor, etc."
    )
    manufacturer = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    year = models.IntegerField(null=True, blank=True, help_text="Manufacture year")

    # Status
    is_active = models.BooleanField(default=True, db_index=True)

    # Operational Meters
    engine_hours = models.IntegerField(
        null=True,
        blank=True,
        help_text="Current engine/operation hour meter"
    )
    cycles = models.IntegerField(
        null=True,
        blank=True,
        help_text="Current cycle count (for equipment with cycle meters)"
    )

    # Relationship to Vehicle (for mounted equipment)
    mounted_on_vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipment',
        help_text="Vehicle this equipment is mounted on (if applicable)"
    )

    # Capabilities - single source of truth for template applicability and equipment features
    # Combines equipment type (e.g., AERIAL_DEVICE) and specific features (e.g., INSULATING_SYSTEM)
    capabilities = models.JSONField(
        default=list,
        blank=True,
        help_text="Equipment capabilities and features (e.g., ['AERIAL_DEVICE', 'INSULATING_SYSTEM', 'BARE_HAND_WORK_UNIT'])"
    )

    # Equipment-Specific Data (placard info, detailed specs)
    # Populated during inspection setup based on capabilities
    equipment_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Equipment-specific data: placard info, rated capacity, insulation class, etc."
    )

    # Notes
    notes = models.TextField(blank=True, help_text="Internal notes")

    class Meta:
        db_table = 'equipment'
        verbose_name_plural = 'equipment'
        ordering = ['asset_number', 'serial_number']
        indexes = [
            models.Index(fields=['customer', 'is_active']),
            models.Index(fields=['serial_number']),
            models.Index(fields=['asset_number']),
            models.Index(fields=['equipment_type']),
            models.Index(fields=['mounted_on_vehicle']),
        ]

    def clean(self):
        """Validate model fields."""
        from django.core.exceptions import ValidationError
        errors = {}

        # Year must be in valid range if provided
        if self.year is not None:
            if self.year < 1900 or self.year > 2100:
                errors['year'] = 'Year must be between 1900 and 2100'

        # Equipment data must be a dict
        if self.equipment_data is not None and not isinstance(self.equipment_data, dict):
            errors['equipment_data'] = 'Equipment data must be a dictionary'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Override save to call full_clean() first."""
        from django.core.exceptions import ValidationError
        from django.db import IntegrityError as DBIntegrityError

        # Skip validation if explicitly disabled
        if not kwargs.pop('skip_validation', False):
            try:
                self.full_clean()
            except ValidationError as e:
                # If it's a uniqueness error, let database handle it (for tests expecting IntegrityError)
                if 'serial_number' in e.message_dict and 'already exists' in str(e.message_dict.get('serial_number', '')):
                    pass  # Let database raise IntegrityError
                else:
                    raise
        super().save(*args, **kwargs)

    def __str__(self):
        if self.asset_number:
            return f"#{self.asset_number} - {self.serial_number}"
        return f"{self.equipment_type} - SN: {self.serial_number}"

    @property
    def display_name(self):
        """User-friendly display name."""
        parts = []
        if self.asset_number:
            parts.append(f"#{self.asset_number}")
        if self.manufacturer and self.model:
            parts.append(f"{self.manufacturer} {self.model}")
        elif self.equipment_type:
            parts.append(self.equipment_type)
        if self.serial_number:
            parts.append(f"SN: {self.serial_number}")
        return ' - '.join(parts) if parts else f"Equipment {self.id}"

    @property
    def basic_info(self):
        """Return basic equipment info string."""
        if self.manufacturer and self.model:
            return f"{self.manufacturer} {self.model}"
        elif self.equipment_type:
            return self.equipment_type
        return "Unknown Equipment"
