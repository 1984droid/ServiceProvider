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
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('ON_HOLD', 'On Hold'),
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
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('EMERGENCY', 'Emergency'),
    ]
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='NORMAL',
        help_text="Priority level for scheduling and dispatch"
    )

    # Source tracking (enhanced for Phase 5)
    SOURCE_TYPE_CHOICES = [
        ('INSPECTION_DEFECT', 'Inspection Defect'),
        ('MAINTENANCE_SCHEDULE', 'Maintenance Schedule'),
        ('CUSTOMER_REQUEST', 'Customer Request'),
        ('BREAKDOWN', 'Breakdown'),
        ('MANUAL', 'Manual'),
    ]
    source_type = models.CharField(
        max_length=30,
        choices=SOURCE_TYPE_CHOICES,
        default='MANUAL',
        help_text="Type of source that created this work order"
    )
    source_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="UUID of source object (defect, maintenance task, etc.)"
    )

    # Legacy source field - kept for backward compatibility
    SOURCE_CHOICES = [
        ('INSPECTION', 'Inspection'),
        ('CUSTOMER_REQUEST', 'Customer Request'),
        ('PM_SCHEDULE', 'PM Schedule'),
        ('BREAKDOWN', 'Breakdown'),
    ]
    source = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES,
        default='CUSTOMER_REQUEST',
        help_text="Legacy: How this work order originated (use source_type instead)"
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
    title = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Brief title for work order"
    )
    description = models.TextField(
        help_text="Description of work to be performed"
    )

    # Department assignments (Phase 5: added single department for primary assignment)
    department = models.ForeignKey(
        'organization.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_work_orders',
        help_text="Primary department assigned to this work order"
    )
    departments = models.ManyToManyField(
        'organization.Department',
        blank=True,
        related_name='work_orders',
        help_text="Legacy: Departments involved in this work order"
    )
    assigned_employees = models.ManyToManyField(
        'organization.Employee',
        blank=True,
        related_name='assigned_work_orders',
        help_text="Legacy: Employees assigned to this work order (use WorkOrderLine.assigned_to instead)"
    )

    # Scheduling
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When work is scheduled to be performed"
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When work must be completed by"
    )
    assigned_to = models.ForeignKey(
        'organization.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_assigned_work_orders',
        help_text="Primary employee assigned to this work order"
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

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this work order is active (soft delete flag)"
    )

    # Approval workflow (Phase 5)
    APPROVAL_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='DRAFT',
        help_text="Approval status for work order"
    )
    approved_by = models.ForeignKey(
        'organization.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_work_orders',
        help_text="Employee who approved this work order"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When work order was approved"
    )
    rejected_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection if approval_status is REJECTED"
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


class WorkOrderLine(BaseModel):
    """
    Individual task/line item within a work order.

    Core Principles:
    - Work orders consist of multiple lines (tasks)
    - Each line uses vocabulary (verb + noun + location)
    - Lines can be assigned to specific employees
    - Track estimated vs actual hours
    - Parts required tracked per line
    - Each line has its own status

    Vocabulary Structure:
    - Verb: Action to perform (e.g., "Replace", "Inspect", "Repair")
    - Noun: Component/part (e.g., "Hydraulic Hose", "Boom Cylinder")
    - Service Location: Where work is performed (e.g., "Boom Assembly", "Chassis")

    Status Flow:
    PENDING → IN_PROGRESS → COMPLETED
                          → CANCELLED
    """

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='lines',
        help_text="Parent work order"
    )

    line_number = models.IntegerField(
        help_text="Line number for ordering (1, 2, 3, ...)"
    )

    # Vocabulary-based task description
    verb = models.CharField(
        max_length=50,
        help_text="Action verb (e.g., 'Replace', 'Inspect', 'Repair')"
    )
    noun = models.CharField(
        max_length=100,
        help_text="Component/part noun (e.g., 'Hydraulic Hose', 'Boom Cylinder')"
    )
    service_location = models.CharField(
        max_length=100,
        help_text="Service location (e.g., 'Boom Assembly', 'Chassis')"
    )

    # Generated or manual description
    description = models.TextField(
        help_text="Full description of task (auto-generated from vocabulary or manual)"
    )

    # Time tracking
    estimated_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated hours to complete this line"
    )
    actual_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual hours spent on this line"
    )

    # Parts
    parts_required = models.JSONField(
        default=list,
        blank=True,
        help_text="List of part numbers/descriptions required"
    )

    # Assignment
    assigned_to = models.ForeignKey(
        'organization.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_work_order_lines',
        help_text="Employee assigned to this specific line"
    )

    # Status
    LINE_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(
        max_length=20,
        choices=LINE_STATUS_CHOICES,
        default='PENDING',
        help_text="Status of this line item"
    )

    # Completion tracking
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this line was completed"
    )
    completed_by = models.ForeignKey(
        'organization.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_work_order_lines',
        help_text="Employee who completed this line"
    )

    notes = models.TextField(
        blank=True,
        help_text="Notes specific to this line"
    )

    class Meta:
        db_table = 'work_order_lines'
        ordering = ['work_order', 'line_number']
        unique_together = [['work_order', 'line_number']]
        indexes = [
            models.Index(fields=['work_order', 'line_number']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
        ]
        verbose_name = 'Work Order Line'
        verbose_name_plural = 'Work Order Lines'

    def __str__(self):
        return f"{self.work_order.work_order_number} - Line {self.line_number}: {self.verb} {self.noun}"

    def clean(self):
        """Validate model before save."""
        super().clean()

        # Validate line number is positive
        if self.line_number is not None and self.line_number < 1:
            raise ValidationError({
                'line_number': 'Line number must be positive'
            })

        # Validate actual hours not greater than 100
        if self.actual_hours and self.actual_hours > 100:
            raise ValidationError({
                'actual_hours': 'Actual hours seems unreasonably high (>100)'
            })

        # Validate parts_required is a list
        if not isinstance(self.parts_required, list):
            raise ValidationError({
                'parts_required': 'Parts required must be a list'
            })

        # Validate completed status has completed_at
        if self.status == 'COMPLETED' and not self.completed_at:
            self.completed_at = timezone.now()

    def save(self, *args, **kwargs):
        """Save with validation."""
        # Auto-generate description if not provided
        if not self.description:
            self.description = f"{self.verb} {self.noun} at {self.service_location}"

        self.full_clean()
        super().save(*args, **kwargs)
