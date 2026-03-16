"""
Inspection Models

Core models for inspection execution and defect tracking.
Built clean - no legacy compatibility.
"""

import hashlib
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class BaseModel(models.Model):
    """Base model with UUID primary key and timestamps."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class InspectionRun(BaseModel):
    """
    Instance of an inspection performed on an asset.

    Core Principles:
    - Polymorphic asset reference (Vehicle or Equipment)
    - Immutable after finalization (finalized_at set)
    - Denormalized customer for fast queries
    - Template snapshot for audit trail
    - step_data stores all inspection responses

    Status Flow:
    DRAFT → IN_PROGRESS → COMPLETED

    Immutability:
    Once finalized_at is set, step_data, template_snapshot, and status
    cannot be modified. This ensures audit compliance.
    """

    # Polymorphic asset reference
    ASSET_TYPE_CHOICES = [
        ('VEHICLE', 'Vehicle'),
        ('EQUIPMENT', 'Equipment'),
    ]
    asset_type = models.CharField(
        max_length=20,
        choices=ASSET_TYPE_CHOICES,
        help_text="Type of asset being inspected"
    )
    asset_id = models.UUIDField(
        help_text="UUID of Vehicle or Equipment being inspected"
    )

    # Denormalized customer for queries
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='inspection_runs',
        help_text="Customer who owns the asset (denormalized for queries)"
    )

    # Template reference
    template_key = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Key of inspection template used (e.g., 'ansi_a92_2_periodic')"
    )
    program_key = models.CharField(
        max_length=100,
        blank=True,
        help_text="Inspection program this fulfills (e.g., 'ANSI_A92_2')"
    )

    # Status
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        db_index=True
    )

    # Inspection Outcome (auto-calculated at finalization)
    OUTCOME_CHOICES = [
        ('PASS', 'Pass - Equipment safe for operation'),
        ('PASS_WITH_REPAIRS', 'Pass - Repairs required before next inspection'),
        ('FAIL', 'Fail - Equipment unsafe, tagged out of service'),
    ]
    inspection_outcome = models.CharField(
        max_length=30,
        choices=OUTCOME_CHOICES,
        null=True,
        blank=True,
        db_index=True,
        help_text="Auto-calculated outcome based on defects and blocking failures"
    )
    outcome_summary = models.JSONField(
        null=True,
        blank=True,
        help_text="Summary data: defect counts by severity, blocking failures, etc."
    )

    # Timestamps
    started_at = models.DateTimeField(
        help_text="When inspection was started"
    )
    finalized_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When inspection was finalized (becomes immutable)"
    )

    # Inspector
    inspector_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of inspector performing inspection"
    )
    inspector_signature = models.JSONField(
        null=True,
        blank=True,
        help_text="Digital signature data: {signature_data, signed_at, signed_by, ip_address}"
    )

    # Data (stored as JSON)
    template_snapshot = models.JSONField(
        help_text="Immutable copy of template at execution time"
    )
    step_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Collected inspection data, keyed by module_key.step_key"
    )

    notes = models.TextField(
        blank=True,
        help_text="General notes about the inspection"
    )

    class Meta:
        db_table = 'inspection_runs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['asset_type', 'asset_id']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['template_key']),
            models.Index(fields=['finalized_at']),
            models.Index(fields=['started_at']),
        ]
        verbose_name = 'Inspection Run'
        verbose_name_plural = 'Inspection Runs'

    def __str__(self):
        asset_display = f"{self.asset_type}"
        date_display = self.started_at.strftime('%Y-%m-%d')
        return f"{self.template_key} - {asset_display} - {date_display}"

    @property
    def asset(self):
        """
        Get the actual asset (Vehicle or Equipment).

        Returns:
            Vehicle or Equipment instance

        Raises:
            DoesNotExist: If asset not found
        """
        if self.asset_type == 'VEHICLE':
            from apps.assets.models import Vehicle
            return Vehicle.objects.get(id=self.asset_id)
        elif self.asset_type == 'EQUIPMENT':
            from apps.assets.models import Equipment
            return Equipment.objects.get(id=self.asset_id)
        else:
            raise ValueError(f"Invalid asset_type: {self.asset_type}")

    @property
    def is_finalized(self):
        """Check if inspection is finalized (immutable)."""
        return self.finalized_at is not None

    @property
    def defect_count(self):
        """Get count of defects for this inspection."""
        return self.defects.count()

    @property
    def critical_defect_count(self):
        """Get count of critical defects."""
        return self.defects.filter(severity='CRITICAL').count()

    def clean(self):
        """Validate model before save."""
        super().clean()

        # Validate asset exists and customer matches
        if self.asset_id and self.customer_id:
            try:
                asset = self.asset
                # Validate customer matches asset customer
                if asset.customer_id != self.customer_id:
                    raise ValidationError({
                        'customer': 'Customer must match asset customer'
                    })
            except (ValueError, KeyError) as e:
                # Invalid asset_type or asset doesn't exist
                raise ValidationError({
                    'asset_id': f'Invalid asset: {e}'
                })
            except ValidationError:
                # Re-raise validation errors
                raise
            except Exception:
                # Asset not found - this is ok during initial creation
                # The database FK will catch any real issues
                pass

        # Validate status progression (only on update, not creation)
        if self.pk:
            try:
                old = InspectionRun.objects.get(pk=self.pk)

                # Cannot go backwards in status
                status_order = {'DRAFT': 0, 'IN_PROGRESS': 1, 'COMPLETED': 2}
                if status_order.get(self.status, 0) < status_order.get(old.status, 0):
                    raise ValidationError({
                        'status': f'Cannot change status from {old.status} to {self.status}'
                    })
            except InspectionRun.DoesNotExist:
                # Object being created with pk already set (UUID) - this is ok
                pass

        # Validate template_snapshot structure
        if not isinstance(self.template_snapshot, dict):
            raise ValidationError({
                'template_snapshot': 'Must be a dictionary'
            })

        # Check for required keys (either 'modules' for old format or 'procedure' for new format)
        if 'modules' not in self.template_snapshot and 'procedure' not in self.template_snapshot:
            raise ValidationError({
                'template_snapshot': 'Must contain "modules" or "procedure" key'
            })

    def save(self, *args, **kwargs):
        """
        Save with immutability enforcement.

        Raises:
            ValidationError: If trying to modify immutable fields after finalization
        """
        # Run validation
        self.full_clean()

        # Enforce immutability after finalization (only on update, not insert)
        if self.pk:
            try:
                old = InspectionRun.objects.get(pk=self.pk)

                # Only enforce immutability if it was ALREADY finalized
                # (Don't block the act of finalizing itself)
                if old.finalized_at is not None:
                    # Protected fields that cannot change after finalization
                    protected_fields = {
                        'step_data': (old.step_data, self.step_data),
                        'template_snapshot': (old.template_snapshot, self.template_snapshot),
                        'status': (old.status, self.status),
                    }

                    changed_fields = []
                    for field_name, (old_value, new_value) in protected_fields.items():
                        if old_value != new_value:
                            changed_fields.append(field_name)

                    if changed_fields:
                        raise ValidationError(
                            f"Cannot modify {', '.join(changed_fields)} after inspection is finalized"
                        )
            except InspectionRun.DoesNotExist:
                # Object being created with pk already set (UUID) - this is ok
                pass

        super().save(*args, **kwargs)


class InspectionDefect(BaseModel):
    """
    Defect or finding identified during inspection.

    Core Principles:
    - Idempotent creation via defect_identity hash
    - Severity-based prioritization (CRITICAL, MAJOR, MINOR, ADVISORY)
    - Linkable to work orders via WorkOrderDefect junction
    - Audit trail via evaluation_trace

    Idempotency:
    defect_identity = SHA256(run_id + module_key + step_key + rule_id)
    Re-running rules updates existing defect rather than creating duplicates.

    Status Flow:
    OPEN → WORK_ORDER_CREATED → RESOLVED
    """

    inspection_run = models.ForeignKey(
        InspectionRun,
        on_delete=models.CASCADE,
        related_name='defects',
        help_text="Inspection that generated this defect"
    )

    # Idempotency
    defect_identity = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="SHA256 hash for idempotency: run_id + module_key + step_key + rule_id"
    )

    # Location in inspection
    module_key = models.CharField(
        max_length=100,
        blank=True,
        help_text="Module where defect was found (e.g., 'visual_inspection')"
    )
    step_key = models.CharField(
        max_length=100,
        help_text="Step where defect was found (e.g., 'hydraulic_leaks')"
    )
    rule_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Rule that generated this defect (null for manual defects)"
    )

    # Severity
    SEVERITY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('MAJOR', 'Major'),
        ('MINOR', 'Minor'),
        ('ADVISORY', 'Advisory'),
    ]
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        db_index=True,
        help_text="CRITICAL: unsafe to operate, MAJOR: significant issue, "
                  "MINOR: maintenance needed, ADVISORY: informational"
    )

    # Defect details
    title = models.CharField(
        max_length=500,
        help_text="Short description of defect"
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text="Detailed description of defect"
    )
    defect_details = models.JSONField(
        null=True,
        blank=True,
        help_text="Structured defect data: {location, photos, measurements, etc.}"
    )

    # Audit trail
    evaluation_trace = models.JSONField(
        null=True,
        blank=True,
        help_text="How this defect was generated: {rule_id, condition, evaluated_at, response_data}"
    )

    # Status
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('WORK_ORDER_CREATED', 'Work Order Created'),
        ('RESOLVED', 'Resolved'),
    ]
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='OPEN',
        db_index=True
    )

    class Meta:
        db_table = 'inspection_defects'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inspection_run', 'severity']),
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['module_key', 'step_key']),
        ]
        verbose_name = 'Inspection Defect'
        verbose_name_plural = 'Inspection Defects'

    def __str__(self):
        return f"{self.severity}: {self.title}"

    @staticmethod
    def generate_defect_identity(inspection_run_id, module_key, step_key, rule_id):
        """
        Generate idempotent defect identity hash.

        Args:
            inspection_run_id: UUID of inspection run
            module_key: Module key where defect found
            step_key: Step key where defect found
            rule_id: Rule ID that generated defect

        Returns:
            SHA256 hash string (64 characters)
        """
        identity_string = f"{inspection_run_id}{module_key}{step_key}{rule_id or ''}"
        return hashlib.sha256(identity_string.encode()).hexdigest()

    def clean(self):
        """Validate model before save."""
        super().clean()

        # Validate defect_identity format
        if len(self.defect_identity) != 64:
            raise ValidationError({
                'defect_identity': 'Must be 64-character SHA256 hash'
            })

        # Validate defect_details structure if present
        if self.defect_details and not isinstance(self.defect_details, dict):
            raise ValidationError({
                'defect_details': 'Must be a dictionary'
            })

    def save(self, *args, **kwargs):
        """Save with validation."""
        self.full_clean()
        super().save(*args, **kwargs)


def inspection_photo_upload_path(instance, filename):
    """
    Generate upload path for inspection photos.

    Pattern: inspections/{inspection_id}/photos/{photo_id}_{filename}

    Args:
        instance: InspectionPhoto instance
        filename: Original filename

    Returns:
        Upload path string
    """
    import os
    ext = os.path.splitext(filename)[1].lower()
    safe_filename = f"{instance.id}{ext}"
    return f'inspections/{instance.inspection.id}/photos/{safe_filename}'


class InspectionPhoto(BaseModel):
    """
    Photo attached to an inspection or defect.

    Photos are stored in local/network filesystem and served via Nginx.
    Automatic thumbnail generation for fast preview loading.

    Storage Location:
    - Production: /var/www/serviceprovider/media/inspections/{id}/photos/
    - Development: {BASE_DIR}/media/inspections/{id}/photos/

    File Naming:
    - Original: {photo_uuid}.jpg
    - Thumbnail: thumb_{photo_uuid}.jpg
    """

    inspection = models.ForeignKey(
        'InspectionRun',
        on_delete=models.CASCADE,
        related_name='photos',
        help_text='Inspection this photo belongs to'
    )

    defect = models.ForeignKey(
        'InspectionDefect',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='photos',
        help_text='Defect this photo is evidence for (optional)'
    )

    step_key = models.CharField(
        max_length=100,
        db_index=True,
        help_text='Step where photo was captured'
    )

    image = models.ImageField(
        upload_to=inspection_photo_upload_path,
        help_text='Original photo file'
    )

    thumbnail = models.ImageField(
        upload_to=inspection_photo_upload_path,
        null=True,
        blank=True,
        help_text='Auto-generated thumbnail (300x300)'
    )

    caption = models.CharField(
        max_length=255,
        blank=True,
        help_text='Optional photo caption or description'
    )

    file_size = models.IntegerField(
        help_text='File size in bytes'
    )

    width = models.IntegerField(
        null=True,
        blank=True,
        help_text='Image width in pixels'
    )

    height = models.IntegerField(
        null=True,
        blank=True,
        help_text='Image height in pixels'
    )

    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_inspection_photos',
        help_text='User who uploaded the photo'
    )

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['inspection', 'step_key']),
            models.Index(fields=['defect']),
            models.Index(fields=['inspection', 'created_at']),
        ]
        verbose_name = 'Inspection Photo'
        verbose_name_plural = 'Inspection Photos'

    def __str__(self):
        return f"Photo for {self.inspection} - {self.step_key}"

    def save(self, *args, **kwargs):
        """
        Save photo with automatic thumbnail generation.

        Process:
        1. Extract image dimensions
        2. Calculate file size
        3. Generate thumbnail if not exists
        4. Save to filesystem
        """
        # Check if this is a new photo (not yet saved to database)
        is_new = self._state.adding

        if self.image and (is_new or not self.file_size):  # New upload or missing metadata
            # Extract image metadata
            from PIL import Image

            # Seek to beginning to ensure we can read the file
            if hasattr(self.image, 'seek'):
                self.image.seek(0)

            img = Image.open(self.image)
            self.width, self.height = img.size

            # Get file size - handle different file types
            if hasattr(self.image, 'size'):
                self.file_size = self.image.size
            elif hasattr(self.image, 'file'):
                # For InMemoryUploadedFile
                self.image.file.seek(0, 2)  # Seek to end
                self.file_size = self.image.file.tell()
                self.image.file.seek(0)  # Seek back to beginning
            else:
                # Fallback: read the entire file
                self.image.seek(0)
                self.file_size = len(self.image.read())
                self.image.seek(0)

            # Generate thumbnail
            if not self.thumbnail:
                self.thumbnail = self._create_thumbnail()

        super().save(*args, **kwargs)

    def _create_thumbnail(self, size=(300, 300)):
        """
        Create thumbnail from original image.

        Args:
            size: Tuple of (width, height) for thumbnail

        Returns:
            InMemoryUploadedFile for thumbnail
        """
        from PIL import Image
        from io import BytesIO
        from django.core.files.uploadedfile import InMemoryUploadedFile
        import os

        # Open original image
        img = Image.open(self.image)

        # Resize maintaining aspect ratio
        img.thumbnail(size, Image.Resampling.LANCZOS)

        # Convert RGBA/LA/P to RGB (for JPEG compatibility)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background

        # Save to BytesIO
        thumb_io = BytesIO()
        img.save(thumb_io, format='JPEG', quality=85, optimize=True)
        thumb_io.seek(0)

        # Generate thumbnail filename
        original_name = os.path.basename(self.image.name)
        thumb_name = f'thumb_{original_name}'.replace(
            os.path.splitext(original_name)[1], '.jpg'
        )

        # Create InMemoryUploadedFile
        return InMemoryUploadedFile(
            thumb_io,
            None,
            thumb_name,
            'image/jpeg',
            thumb_io.getbuffer().nbytes,
            None
        )

    def delete(self, *args, **kwargs):
        """
        Delete photo and clean up files.

        Ensures both original and thumbnail are deleted from filesystem.
        """
        # Delete files from storage
        if self.image:
            self.image.delete(save=False)
        if self.thumbnail:
            self.thumbnail.delete(save=False)

        super().delete(*args, **kwargs)

    @property
    def url(self):
        """Get URL for full-size image."""
        return self.image.url if self.image else None

    @property
    def thumbnail_url(self):
        """Get URL for thumbnail image."""
        return self.thumbnail.url if self.thumbnail else None

    @property
    def uploaded_by_name(self):
        """Get name of user who uploaded photo."""
        if self.uploaded_by:
            return self.uploaded_by.get_full_name() or self.uploaded_by.username
        return None
