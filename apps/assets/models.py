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

    # Vehicle Info (from VIN decode or manual entry)
    year = models.IntegerField(null=True, blank=True, help_text="Model year")
    make = models.CharField(max_length=100, blank=True, db_index=True)
    model = models.CharField(max_length=100, blank=True)
    vehicle_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Truck, Trailer, Van, etc."
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

    # VIN Decode Data (store complete NHTSA response)
    vin_decode_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Complete VIN decode data from NHTSA vPIC API"
    )
    vin_decode_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When VIN was last decoded"
    )

    # Tags for inspection applicability and filtering
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for inspection applicability (e.g., ['INSULATED_BOOM', 'DIELECTRIC'])"
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
        related_name='mounted_equipment',
        help_text="Vehicle this equipment is mounted on (if applicable)"
    )
    mount_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date equipment was mounted on current vehicle"
    )

    # Tags for inspection applicability and filtering
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for inspection applicability (e.g., ['AERIAL_DEVICE', 'INSULATED_BOOM', 'DIELECTRIC'])"
    )

    # Equipment-Specific Data (placard info, capabilities)
    # Populated during inspection setup based on tags
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
