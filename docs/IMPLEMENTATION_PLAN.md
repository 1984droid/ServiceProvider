# Implementation Plan - Inspection & Work Order System

**Goal:** Build the inspection and work order system correctly, methodically, with proper testing at each phase.

**Philosophy:**
- Build incrementally
- Test thoroughly at each step
- No rushing - quality over speed
- Document as we go

---

## Table of Contents

1. [Development Principles](#development-principles)
2. [Phase Overview](#phase-overview)
3. [Phase 1: Database Foundation](#phase-1-database-foundation)
4. [Phase 2: Inspection Template System](#phase-2-inspection-template-system)
5. [Phase 3: Inspection Execution Engine](#phase-3-inspection-execution-engine)
6. [Phase 4: Rule Evaluation System](#phase-4-rule-evaluation-system)
5. [Phase 5: Work Order System](#phase-5-work-order-system)
6. [Phase 6: Integration & Polish](#phase-6-integration--polish)
7. [Testing Strategy](#testing-strategy)
8. [Risk Mitigation](#risk-mitigation)

---

## Development Principles

### 1. Incremental Development
Build in small, testable pieces. Each phase must be:
- Fully tested before moving on
- Documented as complete
- Reviewable in isolation

### 2. Test-Driven Approach
Every feature gets tests:
- Unit tests for models and business logic
- Integration tests for workflows
- API tests for endpoints
- Manual QA testing with real data

### 3. Configuration-Driven
Use our existing test configuration pattern:
- All test data in `tests/config.py`
- No hardcoded values
- Reusable fixtures
- Easy to extend

### 4. Documentation-First
Before coding:
- Write what we're building
- Define the data structures
- Map the workflows
- Document the "why"

### 5. Review Points
After each phase:
- Code review
- Test review
- Documentation review
- Demo/validation

---

## Phase Overview

```
Phase 1: Database Foundation (1-2 weeks)
  ├─ Models: InspectionRun, InspectionDefect, WorkOrder
  ├─ Migrations
  ├─ Admin interfaces
  └─ Model tests

Phase 2: Template System (1-2 weeks)
  ├─ Template data structure (JSON/YAML)
  ├─ Template storage and versioning
  ├─ Template API endpoints
  └─ Template tests

Phase 3: Execution Engine (2-3 weeks)
  ├─ Inspection start/stop flow
  ├─ Step submission logic
  ├─ Status management
  ├─ Immutability enforcement
  └─ Execution tests

Phase 4: Rule System (2-3 weeks)
  ├─ Rule definition structure
  ├─ Rule evaluation engine
  ├─ Defect generation
  ├─ Idempotency handling
  └─ Rule tests

Phase 5: Work Order System (1-2 weeks)
  ├─ Work order CRUD
  ├─ Defect → Work order flow
  ├─ Status management
  ├─ Meter updates
  └─ Work order tests

Phase 6: Integration & Polish (1-2 weeks)
  ├─ Equipment data collection flow
  ├─ End-to-end testing
  ├─ Performance optimization
  └─ Final documentation

Total: 8-14 weeks (2-3.5 months)
```

**Note:** These are realistic estimates for doing it **right**, not rushing.

---

## Phase 1: Database Foundation

**Goal:** Create the core database models for inspections and work orders with proper relationships and constraints.

### 1.1 Models to Create

#### InspectionRun Model

**File:** `apps/inspections/models.py`

```python
class InspectionRun(BaseModel):
    """
    Instance of an inspection performed on an asset.

    Core principles:
    - Polymorphic asset reference (Vehicle or Equipment)
    - Immutable after finalization
    - Denormalized customer for queries
    - Template snapshot for audit trail
    """

    # Polymorphic asset reference
    ASSET_TYPE_CHOICES = [
        ('VEHICLE', 'Vehicle'),
        ('EQUIPMENT', 'Equipment'),
    ]
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    asset_id = models.UUIDField()  # Points to Vehicle.id or Equipment.id

    # Denormalized for queries
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='inspection_runs'
    )

    # Template reference
    template_key = models.CharField(
        max_length=100,
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

    # Timestamps
    started_at = models.DateTimeField()
    finalized_at = models.DateTimeField(null=True, blank=True, db_index=True)

    # Inspector
    inspector_name = models.CharField(max_length=200, blank=True)
    inspector_signature = models.JSONField(
        null=True,
        blank=True,
        help_text="Signature capture data"
    )

    # Data (stored as JSON)
    template_snapshot = models.JSONField(
        help_text="Immutable copy of template at execution time"
    )
    step_data = models.JSONField(
        default=dict,
        help_text="Collected inspection data, keyed by module and step"
    )

    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'inspection_runs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['asset_type', 'asset_id']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['template_key']),
            models.Index(fields=['finalized_at']),
        ]

    def __str__(self):
        return f"Inspection {self.template_key} - {self.asset_type} {self.started_at.date()}"

    @property
    def asset(self):
        """Get the actual asset (Vehicle or Equipment)."""
        if self.asset_type == 'VEHICLE':
            from apps.assets.models import Vehicle
            return Vehicle.objects.get(id=self.asset_id)
        elif self.asset_type == 'EQUIPMENT':
            from apps.assets.models import Equipment
            return Equipment.objects.get(id=self.asset_id)

    @property
    def is_finalized(self):
        """Check if inspection is finalized (immutable)."""
        return self.finalized_at is not None

    def save(self, *args, **kwargs):
        """Enforce immutability after finalization."""
        if self.pk and self.is_finalized:
            # Get old instance
            old = InspectionRun.objects.get(pk=self.pk)

            # Check if protected fields changed
            if (old.step_data != self.step_data or
                old.template_snapshot != self.template_snapshot or
                old.status != self.status):
                raise ValidationError(
                    "Cannot modify step_data, template_snapshot, or status "
                    "after inspection is finalized"
                )

        super().save(*args, **kwargs)
```

#### InspectionDefect Model

```python
class InspectionDefect(BaseModel):
    """
    Defect or finding identified during inspection.

    Core principles:
    - Idempotent creation via defect_identity hash
    - Severity-based prioritization
    - Linkable to work orders
    - Audit trail of rule evaluation
    """

    inspection_run = models.ForeignKey(
        InspectionRun,
        on_delete=models.CASCADE,
        related_name='defects'
    )

    # Idempotency
    defect_identity = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="SHA256 hash: run_id + module_key + step_key + rule_id"
    )

    # Location in inspection
    module_key = models.CharField(max_length=100)
    step_key = models.CharField(max_length=100)
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
        db_index=True
    )

    # Defect details
    title = models.CharField(max_length=500)
    description = models.TextField()
    defect_details = models.JSONField(
        null=True,
        blank=True,
        help_text="Structured defect data (location, photos, measurements, etc.)"
    )

    # Audit trail
    evaluation_trace = models.JSONField(
        null=True,
        blank=True,
        help_text="How this defect was generated (rule evaluation trace)"
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
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.severity}: {self.title}"
```

#### WorkOrder Model

```python
class WorkOrder(BaseModel):
    """
    Service work to be performed on an asset.

    Core principles:
    - Can originate from inspection, customer request, PM, or breakdown
    - Links back to source inspection if applicable
    - Tracks status progression
    - Updates asset meters on completion
    """

    # Unique identifier
    work_order_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Human-readable work order number (e.g., 'WO-2025-00123')"
    )

    # Customer and asset
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='work_orders'
    )

    # Polymorphic asset reference
    ASSET_TYPE_CHOICES = [
        ('VEHICLE', 'Vehicle'),
        ('EQUIPMENT', 'Equipment'),
    ]
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    asset_id = models.UUIDField()

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
        default='MEDIUM'
    )

    # Source
    SOURCE_CHOICES = [
        ('INSPECTION', 'Inspection'),
        ('CUSTOMER_REQUEST', 'Customer Request'),
        ('PM_SCHEDULE', 'PM Schedule'),
        ('BREAKDOWN', 'Breakdown'),
    ]
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES)
    source_inspection_run = models.ForeignKey(
        InspectionRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_orders',
        help_text="Link to inspection if source is INSPECTION"
    )

    # Work details
    description = models.TextField()

    # Scheduling
    scheduled_date = models.DateField(null=True, blank=True)
    assigned_to = models.CharField(
        max_length=200,
        blank=True,
        help_text="Technician name or ID"
    )

    # Execution tracking
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Meter readings at service time
    odometer_at_service = models.IntegerField(null=True, blank=True)
    engine_hours_at_service = models.IntegerField(null=True, blank=True)

    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'work_orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['asset_type', 'asset_id']),
            models.Index(fields=['source_inspection_run']),
            models.Index(fields=['scheduled_date']),
        ]

    def __str__(self):
        return f"{self.work_order_number} - {self.customer.name}"

    @property
    def asset(self):
        """Get the actual asset (Vehicle or Equipment)."""
        if self.asset_type == 'VEHICLE':
            from apps.assets.models import Vehicle
            return Vehicle.objects.get(id=self.asset_id)
        elif self.asset_type == 'EQUIPMENT':
            from apps.assets.models import Equipment
            return Equipment.objects.get(id=self.asset_id)

    def save(self, *args, **kwargs):
        """Auto-generate work order number if not set."""
        if not self.work_order_number:
            self.work_order_number = self.generate_work_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_work_order_number():
        """Generate sequential work order number."""
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
```

#### WorkOrderDefect (Junction Table)

```python
class WorkOrderDefect(models.Model):
    """
    Links work orders to inspection defects (many-to-many).
    One work order can address multiple defects.
    Multiple work orders can address parts of one defect.
    """

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='defect_links'
    )
    defect = models.ForeignKey(
        InspectionDefect,
        on_delete=models.CASCADE,
        related_name='work_order_links'
    )

    # When this link was created
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'work_order_defects'
        unique_together = [['work_order', 'defect']]
        indexes = [
            models.Index(fields=['work_order']),
            models.Index(fields=['defect']),
        ]

    def __str__(self):
        return f"{self.work_order.work_order_number} → {self.defect.title}"
```

### 1.2 Create the App Structure

```bash
# Create inspections app
python manage.py startapp inspections

# Create work_orders app
python manage.py startapp work_orders
```

### 1.3 Update Settings

```python
# config/settings.py
INSTALLED_APPS = [
    # ... existing apps ...
    'apps.inspections',
    'apps.work_orders',
]
```

### 1.4 Admin Interfaces

Create admin interfaces for manual testing:

```python
# apps/inspections/admin.py
from django.contrib import admin
from .models import InspectionRun, InspectionDefect

@admin.register(InspectionRun)
class InspectionRunAdmin(admin.ModelAdmin):
    list_display = ['id', 'template_key', 'asset_type', 'customer', 'status', 'started_at', 'finalized_at']
    list_filter = ['status', 'asset_type', 'template_key']
    search_fields = ['customer__name', 'template_key']
    readonly_fields = ['id', 'created_at', 'updated_at', 'is_finalized']

    fieldsets = [
        ('Asset Information', {
            'fields': ['asset_type', 'asset_id', 'customer']
        }),
        ('Template', {
            'fields': ['template_key', 'program_key', 'template_snapshot']
        }),
        ('Status', {
            'fields': ['status', 'started_at', 'finalized_at', 'is_finalized']
        }),
        ('Inspector', {
            'fields': ['inspector_name', 'inspector_signature']
        }),
        ('Data', {
            'fields': ['step_data', 'notes']
        }),
        ('Metadata', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

@admin.register(InspectionDefect)
class InspectionDefectAdmin(admin.ModelAdmin):
    list_display = ['defect_identity', 'inspection_run', 'severity', 'title', 'status']
    list_filter = ['severity', 'status']
    search_fields = ['title', 'description', 'defect_identity']
    readonly_fields = ['defect_identity', 'created_at', 'updated_at']
```

### 1.5 Migrations

```bash
python manage.py makemigrations inspections
python manage.py makemigrations work_orders
python manage.py migrate
```

### 1.6 Model Tests

Create comprehensive model tests:

**File:** `apps/inspections/tests/test_models.py`

```python
import pytest
from django.core.exceptions import ValidationError
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.customers.models import Customer
from apps.assets.models import Equipment

@pytest.mark.django_db
class TestInspectionRun:

    def test_create_inspection_run(self):
        """Test basic inspection run creation."""
        customer = Customer.objects.create(name="Test Customer")
        equipment = Equipment.objects.create(
            customer=customer,
            serial_number="SN123",
            equipment_type="AERIAL"
        )

        inspection = InspectionRun.objects.create(
            asset_type='EQUIPMENT',
            asset_id=equipment.id,
            customer=customer,
            template_key='test_template',
            status='DRAFT',
            started_at=timezone.now(),
            template_snapshot={'modules': []},
            step_data={}
        )

        assert inspection.asset == equipment
        assert inspection.is_finalized == False
        assert inspection.status == 'DRAFT'

    def test_immutability_after_finalization(self):
        """Test that finalized inspections cannot be modified."""
        # Create and finalize inspection
        inspection = InspectionRun.objects.create(...)
        inspection.finalized_at = timezone.now()
        inspection.save()

        # Try to modify step_data
        inspection.step_data = {'modified': True}

        with pytest.raises(ValidationError):
            inspection.save()

    # More tests...
```

### 1.7 Phase 1 Deliverables

**Checklist:**
- [ ] Models created with proper fields and constraints
- [ ] Migrations applied successfully
- [ ] Admin interfaces working
- [ ] Model tests passing (>90% coverage)
- [ ] Documentation updated
- [ ] Code reviewed

**Review Point:** Demo the admin interface, show test coverage, walk through model relationships.

---

## Phase 2: Inspection Template System

**Goal:** Create a flexible, versioned system for defining inspection templates.

### 2.1 Template Data Structure

**Decision:** Store templates as JSON files in the repository for version control.

**Location:** `apps/inspections/templates/inspection_templates/`

**Example Template Structure:**

```json
{
  "key": "ansi_a92_2_periodic",
  "version": "1.0",
  "title": "ANSI A92.2 Periodic Inspection",
  "description": "Periodic inspection for mobile elevating work platforms per ANSI A92.2",
  "applicable_tags": ["AERIAL_DEVICE"],
  "required_equipment_data": ["placard", "dielectric"],
  "modules": [
    {
      "key": "visual_inspection",
      "title": "Visual Inspection",
      "description": "Comprehensive visual inspection of all components",
      "steps": [
        {
          "key": "boom_condition",
          "title": "Boom Structure Condition",
          "description": "Inspect the boom structure for cracks, bends, deformations, corrosion, missing fasteners, and damaged welds",
          "type": "condition_check",
          "required": true,
          "options": ["good", "fair", "poor", "critical"],
          "allows_photos": true,
          "allows_notes": true
        },
        {
          "key": "hydraulic_leaks",
          "title": "Check for Hydraulic Leaks",
          "description": "Inspect hydraulic system for leaks at cylinder seals, hose connections, pump, valves, and reservoir",
          "type": "pass_fail",
          "required": true,
          "fail_prompts": ["location", "severity"],
          "allows_photos": true
        }
      ]
    },
    {
      "key": "function_tests",
      "title": "Function Tests",
      "description": "Test all operational functions",
      "steps": [...]
    }
  ]
}
```

### 2.2 Template Loader

Create a service to load and validate templates:

```python
# apps/inspections/services/template_service.py

import json
from pathlib import Path
from django.conf import settings

class TemplateService:
    """Service for loading and managing inspection templates."""

    TEMPLATE_DIR = Path(settings.BASE_DIR) / 'apps' / 'inspections' / 'templates' / 'inspection_templates'

    @classmethod
    def load_template(cls, template_key):
        """Load template by key."""
        template_file = cls.TEMPLATE_DIR / f"{template_key}.json"

        if not template_file.exists():
            raise ValueError(f"Template {template_key} not found")

        with open(template_file, 'r') as f:
            template_data = json.load(f)

        # Validate template structure
        cls.validate_template(template_data)

        return template_data

    @classmethod
    def validate_template(cls, template_data):
        """Validate template has required fields."""
        required_fields = ['key', 'version', 'title', 'modules']

        for field in required_fields:
            if field not in template_data:
                raise ValueError(f"Template missing required field: {field}")

        # Validate modules
        for module in template_data['modules']:
            if 'key' not in module or 'steps' not in module:
                raise ValueError(f"Module missing required fields")

        return True

    @classmethod
    def get_applicable_templates(cls, equipment):
        """Get templates applicable to equipment based on tags."""
        templates = []

        # Load all templates
        for template_file in cls.TEMPLATE_DIR.glob("*.json"):
            template = cls.load_template(template_file.stem)

            # Check if equipment tags match template requirements
            applicable_tags = template.get('applicable_tags', [])
            if any(tag in equipment.tags for tag in applicable_tags):
                templates.append(template)

        return templates
```

### 2.3 Template API Endpoints

```python
# apps/inspections/views.py

from rest_framework.decorators import action
from rest_framework.response import Response
from .services.template_service import TemplateService

class InspectionViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def templates(self, request):
        """List all available templates."""
        # Implementation
        pass

    @action(detail=False, methods=['get'])
    def templates_for_equipment(self, request):
        """Get templates applicable to specific equipment."""
        equipment_id = request.query_params.get('equipment_id')
        # Implementation
        pass
```

### 2.4 Phase 2 Deliverables

**Checklist:**
- [ ] Template JSON structure defined
- [ ] Template loader service created
- [ ] Template validation working
- [ ] API endpoints for templates
- [ ] At least 2 sample templates created
- [ ] Template tests passing
- [ ] Documentation updated

---

## Phase 3: Inspection Execution Engine

**Goal:** Build the core engine for starting, executing, and finalizing inspections.

### 3.1 Inspection Start Flow

```python
# apps/inspections/services/inspection_service.py

class InspectionService:

    @staticmethod
    def start_inspection(equipment, template_key, inspector_name):
        """
        Start a new inspection on equipment.

        Steps:
        1. Validate equipment data completeness
        2. Load template
        3. Create InspectionRun
        4. Return inspection ID
        """
        # Implementation in this phase
        pass
```

### 3.2 Step Submission Logic

```python
def submit_step(inspection_run, module_key, step_key, response_data):
    """
    Submit a step response during inspection.

    Steps:
    1. Validate inspection not finalized
    2. Validate step exists in template
    3. Update step_data
    4. Update status to IN_PROGRESS if first step
    5. Trigger rule evaluation (Phase 4)
    """
    # Implementation
    pass
```

### 3.3 Finalization Logic

```python
def finalize_inspection(inspection_run, signature_data):
    """
    Finalize an inspection (make immutable).

    Steps:
    1. Validate all required steps completed
    2. Set finalized_at timestamp
    3. Set status to COMPLETED
    4. Save signature
    5. Lock the record
    """
    # Implementation
    pass
```

### 3.4 Phase 3 Deliverables

**Checklist:**
- [ ] Inspection start service implemented
- [ ] Step submission working
- [ ] Finalization working
- [ ] Status transitions validated
- [ ] Immutability enforced
- [ ] API endpoints created
- [ ] Integration tests passing
- [ ] Can complete full inspection flow manually

---

## Phase 4: Rule Evaluation System

**Goal:** Build the system that automatically generates defects based on inspection responses.

### 4.1 Rule Definition Structure

```json
{
  "rule_id": "hydraulic_leak_fail",
  "template_key": "ansi_a92_2_periodic",
  "module_key": "visual_inspection",
  "step_key": "hydraulic_leaks",
  "condition": "response.result == 'fail'",
  "defect": {
    "severity": "MAJOR",
    "title": "Hydraulic Leak Detected",
    "description_template": "Hydraulic leak found during inspection. Location: {response.location}",
    "recommended_action": "Repair or replace leaking component"
  }
}
```

### 4.2 Rule Evaluation Engine

```python
class RuleEngine:

    @staticmethod
    def evaluate_step(inspection_run, module_key, step_key, response):
        """
        Evaluate rules for a step submission.

        Steps:
        1. Load applicable rules
        2. Evaluate each rule condition
        3. Create defects for matching rules
        4. Return created defects
        """
        # Implementation
        pass

    @staticmethod
    def evaluate_condition(condition, response):
        """Safely evaluate rule condition against response."""
        # Implementation with sandboxing
        pass
```

### 4.3 Defect Generation with Idempotency

```python
def create_defect_from_rule(inspection_run, rule, module_key, step_key, response):
    """
    Create or update defect based on rule.

    Uses defect_identity hash for idempotency.
    """
    import hashlib

    # Compute defect identity
    identity_string = f"{inspection_run.id}{module_key}{step_key}{rule['rule_id']}"
    defect_identity = hashlib.sha256(identity_string.encode()).hexdigest()

    # Get or create defect
    defect, created = InspectionDefect.objects.get_or_create(
        defect_identity=defect_identity,
        defaults={
            'inspection_run': inspection_run,
            'module_key': module_key,
            'step_key': step_key,
            'rule_id': rule['rule_id'],
            'severity': rule['defect']['severity'],
            'title': rule['defect']['title'],
            'description': format_description(rule['defect']['description_template'], response),
            'defect_details': response,
            'evaluation_trace': {...},
            'status': 'OPEN'
        }
    )

    return defect
```

### 4.4 Phase 4 Deliverables

**Status:** ✅ **COMPLETE** (March 12, 2026)

**Checklist:**
- [x] Rule definition structure finalized (14 assertion types)
- [x] Rule evaluation engine working (RuleEvaluator service)
- [x] Defect generation with idempotency (SHA256 hash-based)
- [x] Multiple test rules created (ANSI A92.2-2021 templates)
- [x] Rule tests passing (92 tests, 100%)
- [x] Can trigger defects during inspection (API endpoints + runtime)
- [x] Documentation updated (PHASE_4_COMPLETION.md)

**Key Achievements:**
- 14 assertion types implemented
- Path resolution (simple, nested, array indices)
- Idempotent defect creation via SHA256 identity
- Comprehensive audit trails (evaluation_trace)
- API endpoints: `/evaluate_rules/`, `/defects/`
- Admin UI with color-coded defects
- 92 tests passing (100%)

See [PHASE_4_COMPLETION.md](PHASE_4_COMPLETION.md) for complete report.

---

## Phase 5: Inspection-to-Work Order Integration

**Goal:** Build automated bridge between inspection defects and work order generation.

**Status:** 🔄 **IN PROGRESS**

### 5.1 Work Order Core Enhancement

**Objective:** Extend WorkOrder model with work order lines and enhanced fields.

**New Models:**

#### WorkOrderLine
Individual repair/maintenance tasks within a work order.

```python
class WorkOrderLine(models.Model):
    """Work order line item - single task."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    work_order = models.ForeignKey(WorkOrder, related_name='lines')
    line_number = models.IntegerField()  # Ordering within WO

    # Vocabulary-based task description
    verb = models.CharField(max_length=50)  # e.g., "Replace", "Inspect"
    noun = models.CharField(max_length=100)  # e.g., "Hydraulic Hose"
    service_location = models.CharField(max_length=100)  # e.g., "Boom Assembly"
    description = models.TextField()  # Generated or manual

    # Time tracking
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    # Parts
    parts_required = models.JSONField(default=list)  # List of part numbers

    # Status
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ])

    assigned_to = models.ForeignKey(Employee, null=True)
```

#### WorkOrder Enhancements
```python
# Additional fields
source_type = models.CharField(max_length=30, choices=[
    ('INSPECTION_DEFECT', 'Inspection Defect'),
    ('MAINTENANCE_SCHEDULE', 'Maintenance Schedule'),
    ('CUSTOMER_REQUEST', 'Customer Request'),
    ('MANUAL', 'Manual'),
])
source_id = models.UUIDField(null=True)  # Polymorphic reference
priority = models.CharField(max_length=20)  # Derived from defect severity
approval_status = models.CharField(max_length=20)
approved_by = models.ForeignKey(Employee, null=True)
approved_at = models.DateTimeField(null=True)
```

**Tests:** ~15 tests
- Model creation/validation
- Relationship integrity
- Status transitions
- Approval workflows

### 5.2 Defect-to-Work Order Service

**Objective:** Automate work order generation from inspection defects.

**Service:** `apps/inspections/services/defect_to_work_order_service.py`

```python
class DefectToWorkOrderService:
    """Bridge between inspection defects and work orders."""

    @classmethod
    def generate_work_order_from_defect(
        cls,
        defect: InspectionDefect,
        **options
    ) -> WorkOrder:
        """
        Generate work order from single defect.

        Steps:
        1. Check if defect already has work order
        2. Map defect to vocabulary (verb/noun/location)
        3. Create work order with appropriate priority
        4. Generate work order lines
        5. Update defect status to WORK_ORDER_CREATED

        Returns:
            Created work order
        """
        pass

    @classmethod
    def generate_work_orders_from_inspection(
        cls,
        inspection_run: InspectionRun,
        severity_threshold: str = 'MINOR',
        grouping: str = 'BY_SEVERITY'
    ) -> List[WorkOrder]:
        """
        Batch generate work orders for inspection defects.

        Args:
            severity_threshold: Only create WOs for defects >= this severity
            grouping: 'BY_SEVERITY', 'BY_LOCATION', 'ONE_PER_DEFECT'

        Returns:
            List of created work orders
        """
        pass

    @classmethod
    def map_defect_to_vocabulary(
        cls,
        defect: InspectionDefect
    ) -> Dict[str, str]:
        """
        Map defect to work order vocabulary.

        Uses:
        1. Direct mapping from catalog
        2. Rule-based extraction from defect metadata
        3. Fallback to generic values

        Returns:
            {'verb': '...', 'noun': '...', 'location': '...'}
        """
        pass
```

**Mapping Strategy:**
1. **Direct Catalog Mapping:** Use `inspection_defect_to_work_order_seed_map_ansi_a92_2_2021.json`
2. **Rule-Based:** Extract from step_key, defect title/description
3. **AI-Assisted:** (Future) NLP for custom defects

**Tests:** ~25 tests
- Single defect → work order
- Batch generation with different groupings
- Vocabulary mapping accuracy
- Idempotency (re-running doesn't duplicate)
- Priority mapping (CRITICAL→URGENT, MAJOR→HIGH, etc.)
- Status synchronization

### 5.3 Work Order Vocabulary Service

**Objective:** Load and validate work order vocabulary catalog.

**Service:** `apps/work_orders/services/vocabulary_service.py`

```python
class VocabularyService:
    """Work order vocabulary management."""

    _vocabulary_cache = None

    @classmethod
    def load_vocabulary(cls) -> Dict[str, Any]:
        """
        Load vocabulary from JSON files.

        Returns:
            {
                'verbs': [...],
                'nouns': [...],
                'service_locations': [...],
                'noun_categories': [...],
                'location_categories': [...]
            }
        """
        pass

    @classmethod
    def validate_line_vocabulary(
        cls,
        verb: str,
        noun: str,
        location: str
    ) -> bool:
        """Validate vocabulary combination exists."""
        pass

    @classmethod
    def suggest_vocabulary(
        cls,
        description: str
    ) -> Dict[str, List[str]]:
        """
        Suggest verb/noun/location from description.

        Args:
            description: Free-text description

        Returns:
            {'verbs': [...], 'nouns': [...], 'locations': [...]}
        """
        pass

    @classmethod
    def get_verbs(cls) -> List[Dict]:
        """Get all verbs."""
        pass

    @classmethod
    def get_nouns(cls, category: str = None) -> List[Dict]:
        """Get nouns, optionally filtered by category."""
        pass

    @classmethod
    def get_service_locations(cls) -> List[Dict]:
        """Get all service locations."""
        pass
```

**Data Sources:**
- `asset_templates_v2_3/work_order_vocabulary/verbs.json`
- `asset_templates_v2_3/work_order_vocabulary/nouns.json`
- `asset_templates_v2_3/work_order_vocabulary/service_locations.json`

**Tests:** ~10 tests
- Vocabulary loading
- Validation
- Suggestion accuracy (basic keyword matching)

### 5.4 API Endpoints

**Objective:** Expose work order functionality via REST API.

**New Endpoints:**

#### Work Order Management
```
POST   /api/work-orders/                        # Create work order
GET    /api/work-orders/                        # List work orders
GET    /api/work-orders/{id}/                   # Work order detail
PATCH  /api/work-orders/{id}/                   # Update work order
DELETE /api/work-orders/{id}/                   # Delete work order
POST   /api/work-orders/{id}/approve/           # Approve work order
POST   /api/work-orders/{id}/start/             # Start work
POST   /api/work-orders/{id}/complete/          # Complete work order
```

#### Work Order Lines
```
POST   /api/work-orders/{id}/lines/             # Add line
GET    /api/work-orders/{id}/lines/             # List lines
PATCH  /api/work-orders/{id}/lines/{line_id}/   # Update line
DELETE /api/work-orders/{id}/lines/{line_id}/   # Delete line
```

#### Defect Integration
```
POST   /api/inspections/{id}/generate-work-orders/  # Generate WOs from inspection
POST   /api/defects/{id}/create-work-order/         # Create WO from single defect
```

**Tests:** ~20 tests
- CRUD operations
- Approval workflows
- Line management
- Defect integration endpoints

### 5.5 Admin Interface Enhancements

**Objective:** Update admin UI for work order management.

**WorkOrderAdmin:**
- Inline work order lines display
- Color-coded priority/status badges
- Source defect link (if applicable)
- Approval actions
- Bulk operations (approve multiple, assign to tech)

**WorkOrderLineAdmin:**
- Vocabulary autocomplete
- Time tracking display
- Status badges
- Parts list display

**InspectionDefect Updates:**
- Display linked work order (if exists)
- "Create Work Order" admin action
- Status change to WORK_ORDER_CREATED when WO linked

**Tests:** Admin functionality tested via integration tests

### 5.6 Status Synchronization

**Objective:** Bi-directional status sync between defects and work orders.

**Signal Handlers:** `apps/work_orders/signals.py`

```python
@receiver(post_save, sender=WorkOrder)
def sync_defect_status(sender, instance, created, **kwargs):
    """
    Update defect status when work order changes:
    - WO created → defect.status = WORK_ORDER_CREATED
    - WO completed → defect.status = RESOLVED
    - WO cancelled → defect.status = OPEN (reopen)
    """
    pass

@receiver(post_save, sender=InspectionDefect)
def sync_work_order_defects(sender, instance, created, **kwargs):
    """
    Handle defect status changes affecting work orders.
    - Defect resolved manually → update WO if all defects resolved
    """
    pass
```

**Tests:** ~8 tests
- Status propagation defect→WO
- Status propagation WO→defect
- Edge cases (multiple defects per WO)
- Reopening defects

### 5.7 Phase 5 Deliverables

**Target:** 85+ new tests

**Checklist:**
- [ ] WorkOrderLine model created
- [ ] WorkOrder enhancements completed
- [ ] DefectToWorkOrderService implemented
- [ ] VocabularyService implemented
- [ ] API endpoints created
- [ ] Admin UI enhanced
- [ ] Status synchronization working
- [ ] 85+ tests passing
- [ ] Documentation updated
- [ ] Can generate WO from defect via API
- [ ] Can generate WOs from entire inspection
- [ ] Vocabulary mapping accurate for ANSI A92.2 rules

**Timeline:** 12-15 hours
- Models & migrations: 2-3 hours
- Services: 5-6 hours
- API: 2 hours
- Admin: 2 hours
- Testing: 3-4 hours

---

## Phase 6: Integration & Polish

**Goal:** Tie everything together and optimize.

### 6.1 Equipment Data Collection Flow

Implement the tag-based equipment data collection UI flow.

### 6.2 End-to-End Testing

Create tests that cover the entire journey:
- Create equipment
- Start inspection
- Complete steps
- Generate defects
- Create work order
- Complete work
- Verify meters updated

### 6.3 Performance Optimization

- Query optimization
- Indexing review
- Caching strategy

### 6.4 Final Documentation

- API documentation
- User workflows
- Admin guides
- Developer docs

### 6.5 Phase 6 Deliverables

**Checklist:**
- [ ] Equipment data collection UI
- [ ] End-to-end tests passing
- [ ] Performance acceptable
- [ ] All documentation complete
- [ ] System demo ready
- [ ] Production deployment plan

---

## Testing Strategy

### Unit Tests
- Every model method
- Every service function
- Every validation rule

### Integration Tests
- Complete inspection flow
- Complete work order flow
- Defect → Work order flow

### API Tests
- All endpoints
- Error cases
- Edge cases

### Manual QA Tests
- Real-world scenarios
- User acceptance testing
- Performance testing

### Test Coverage Goals
- Models: 100%
- Services: >95%
- Views: >90%
- Overall: >90%

---

## Risk Mitigation

### Risk 1: Rule Engine Complexity
**Mitigation:** Start simple, use safe expression evaluation, extensive testing

### Risk 2: Template Versioning
**Mitigation:** Include version in template, snapshot template at inspection start

### Risk 3: Performance at Scale
**Mitigation:** Proper indexing, query optimization, caching strategy

### Risk 4: Data Integrity
**Mitigation:** Database constraints, validation at multiple layers, audit trails

### Risk 5: UI Complexity
**Mitigation:** Progressive disclosure, clear workflows, user testing

---

## Success Criteria

**Phase Complete When:**
1. All tests passing
2. Documentation complete
3. Code reviewed
4. Demo successful
5. No critical bugs
6. Team consensus to proceed

**Project Complete When:**
1. All 6 phases complete
2. End-to-end tests passing
3. Performance acceptable
4. Documentation complete
5. Production deployment successful
6. First real inspection completed successfully

---

## Next Steps

**Immediate:**
1. Review this implementation plan
2. Adjust timeline if needed
3. Set up project tracking (Jira, GitHub Projects, etc.)
4. Begin Phase 1: Database Foundation

**First Deliverable:**
- Complete Phase 1 models
- All model tests passing
- Admin interfaces working
- Ready for code review

---

**Let's build this right. No rushing. Quality first.**
