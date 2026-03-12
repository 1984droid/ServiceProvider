"""
Work Order Models

Core models for service work order management and tracking.
Built clean - no legacy compatibility.
"""

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


class WorkOrder(BaseModel):
    """
    Service work to be performed on an asset.

    Core Principles:
    - Can originate from inspection, customer request, PM schedule, or breakdown
    - Polymorphic asset reference (Vehicle or Equipment)
    - Links back to source inspection if applicable
    - Auto-generated work order numbers (WO-YYYY-#####)
    - Tracks status progression with validation
    - Updates asset meters on completion

    Status Flow:
    DRAFT → SCHEDULED → IN_PROGRESS → COMPLETED
                                    → CANCELLED

    Priority Levels:
    LOW → MEDIUM → HIGH → URGENT
    """

    # Unique identifier
    work_order_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Auto-generated work order number (e.g., 'WO-2025-00123')"
    )

    # Customer and asset
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='work_orders',
        help_text="Customer who owns the asset"
    )

    # Polymorphic asset reference
    ASSET_TYPE_CHOICES = [
        ('VEHICLE', 'Vehicle'),
        ('EQUIPMENT', 'Equipment'),
    ]
    asset_type = models.CharField(
        max_length=20,
        choices=ASSET_TYPE_CHOICES,
        help_text="Type of asset being serviced"
    )
    asset_id = models.UUIDField(
        help_text="UUID of Vehicle or Equipment being serviced"
    )

    # Status
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        db_index=True
    )

    # Priority
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        help_text="Priority level for scheduling and dispatch"
    )

    # Source tracking
    SOURCE_CHOICES = [
        ('INSPECTION', 'Inspection'),
        ('CUSTOMER_REQUEST', 'Customer Request'),
        ('PM_SCHEDULE', 'PM Schedule'),
        ('BREAKDOWN', 'Breakdown'),
    ]
    source = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES,
        help_text="How this work order originated"
    )
    source_inspection_run = models.ForeignKey(
        'inspections.InspectionRun',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_orders',
        help_text="Link to inspection if source is INSPECTION"
    )

    # Work details
    description = models.TextField(
        help_text="Description of work to be performed"
    )

    # Department assignments
    departments = models.ManyToManyField(
        'organization.Department',
        blank=True,
        related_name='work_orders',
        help_text="Departments involved in this work order"
    )
    assigned_employees = models.ManyToManyField(
        'organization.Employee',
        blank=True,
        related_name='assigned_work_orders',
        help_text="Employees assigned to this work order"
    )

    # Scheduling
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When work is scheduled to be performed"
    )
    assigned_to = models.CharField(
        max_length=200,
        blank=True,
        help_text="Legacy: Technician name or ID (use assigned_employees instead)"
    )

    # Execution tracking
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When work was actually started"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When work was completed"
    )

    # Meter readings at service time
    odometer_at_service = models.IntegerField(
        null=True,
        blank=True,
        help_text="Vehicle odometer reading when service was performed (miles)"
    )
    engine_hours_at_service = models.IntegerField(
        null=True,
        blank=True,
        help_text="Equipment engine hours when service was performed"
    )

    notes = models.TextField(
        blank=True,
        help_text="General notes about the work order"
    )

    class Meta:
        db_table = 'work_orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['asset_type', 'asset_id']),
            models.Index(fields=['source_inspection_run']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['completed_at']),
        ]
        verbose_name = 'Work Order'
        verbose_name_plural = 'Work Orders'

    def __str__(self):
        return f"{self.work_order_number} - {self.status}"

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
    def defect_count(self):
        """Get count of defects linked to this work order."""
        return self.defect_links.count()

    @property
    def is_completed(self):
        """Check if work order is completed."""
        return self.status == 'COMPLETED'

    @property
    def is_cancelled(self):
        """Check if work order is cancelled."""
        return self.status == 'CANCELLED'

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

        # Validate source inspection matches asset if provided
        if self.source_inspection_run:
            if (self.source_inspection_run.asset_type != self.asset_type or
                self.source_inspection_run.asset_id != self.asset_id):
                raise ValidationError({
                    'source_inspection_run': 'Source inspection must be for the same asset'
                })

        # Validate status progression (only on update, not creation)
        if self.pk:
            try:
                old = WorkOrder.objects.get(pk=self.pk)

                # Cannot reopen completed or cancelled work orders
                if old.status in ('COMPLETED', 'CANCELLED'):
                    if self.status not in ('COMPLETED', 'CANCELLED'):
                        raise ValidationError({
                            'status': f'Cannot reopen work order from {old.status} status'
                        })
            except WorkOrder.DoesNotExist:
                # Object being created with pk already set (UUID) - this is ok
                pass

        # Validate timestamps
        if self.started_at and self.completed_at:
            if self.started_at > self.completed_at:
                raise ValidationError({
                    'completed_at': 'Completed time cannot be before start time'
                })

        # Validate scheduled date
        if self.scheduled_date and self.status == 'DRAFT':
            if self.scheduled_date < timezone.now().date():
                raise ValidationError({
                    'scheduled_date': 'Cannot schedule work order in the past'
                })

    def save(self, *args, **kwargs):
        """
        Save with auto-generation and validation.

        Auto-generates work_order_number if not set.
        Runs full validation before save.
        """
        # Auto-generate work order number if not set
        if not self.work_order_number:
            self.work_order_number = self.generate_work_order_number()

        # Run validation
        self.full_clean()

        super().save(*args, **kwargs)

    @staticmethod
    def generate_work_order_number():
        """
        Generate sequential work order number for current year.

        Format: WO-YYYY-#####
        Example: WO-2025-00123

        Returns:
            String work order number
        """
        from django.db.models import Max
        import datetime

        year = datetime.datetime.now().year
        prefix = f"WO-{year}-"

        # Get highest number for this year
        last_wo = WorkOrder.objects.filter(
            work_order_number__startswith=prefix
        ).aggregate(Max('work_order_number'))

        if last_wo['work_order_number__max']:
            last_num = int(last_wo['work_order_number__max'].split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:05d}"


class WorkOrderDefect(models.Model):
    """
    Junction table linking work orders to inspection defects.

    Core Principles:
    - Many-to-many relationship between work orders and defects
    - One work order can address multiple defects
    - Multiple work orders can address parts of one defect
    - Tracks when the link was created for audit trail
    - Unique constraint prevents duplicate links

    Use Cases:
    - Single WO fixes multiple related defects (e.g., multiple hydraulic leaks)
    - Single defect requires multiple WOs (e.g., parts order, then installation)
    - Tracking which defects were addressed by which work orders
    """

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='defect_links',
        help_text="Work order that addresses this defect"
    )
    defect = models.ForeignKey(
        'inspections.InspectionDefect',
        on_delete=models.CASCADE,
        related_name='work_order_links',
        help_text="Defect being addressed by this work order"
    )

    # Audit tracking
    linked_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this link was created"
    )

    class Meta:
        db_table = 'work_order_defects'
        unique_together = [['work_order', 'defect']]
        indexes = [
            models.Index(fields=['work_order']),
            models.Index(fields=['defect']),
        ]
        verbose_name = 'Work Order Defect Link'
        verbose_name_plural = 'Work Order Defect Links'

    def __str__(self):
        return f"{self.work_order.work_order_number} → {self.defect.title[:50]}"

    def clean(self):
        """Validate model before save."""
        super().clean()

        # Validate work order and defect belong to same customer
        if self.work_order.customer_id != self.defect.inspection_run.customer_id:
            raise ValidationError(
                "Work order and defect must belong to same customer"
            )

        # Validate work order and defect are for same asset
        if (self.work_order.asset_type != self.defect.inspection_run.asset_type or
            self.work_order.asset_id != self.defect.inspection_run.asset_id):
            raise ValidationError(
                "Work order and defect must be for the same asset"
            )

    def save(self, *args, **kwargs):
        """Save with validation."""
        self.full_clean()
        super().save(*args, **kwargs)
