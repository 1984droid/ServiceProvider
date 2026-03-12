"""
Pydantic schemas for inspection template validation.

These schemas validate the AF_INSPECTION_TEMPLATE format from asset_templates_v2_3.
Ensures templates are properly structured before being loaded into the system.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Literal, Union
from enum import Enum


class FieldType(str, Enum):
    """Valid field types for template fields."""
    BOOLEAN = "BOOLEAN"
    TEXT = "TEXT"
    TEXTAREA = "TEXTAREA"
    NUMBER = "NUMBER"
    ENUM = "ENUM"
    CHOICE_MULTI = "CHOICE_MULTI"
    ATTACHMENTS = "ATTACHMENTS"


class StepType(str, Enum):
    """Valid step types for inspection procedures."""
    SETUP = "SETUP"
    DEFECT_CAPTURE = "DEFECT_CAPTURE"
    MEASUREMENT = "MEASUREMENT"
    VISUAL_INSPECTION = "VISUAL_INSPECTION"
    FUNCTION_TEST = "FUNCTION_TEST"


class TemplateStatus(str, Enum):
    """Template publication status."""
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    PUBLISHED = "PUBLISHED"
    DEPRECATED = "DEPRECATED"


# ============================================================================
# Template Metadata Schemas
# ============================================================================

class StandardReference(BaseModel):
    """Reference to inspection standard."""
    code: str = Field(..., description="Standard code (e.g., 'ANSI/SAIA A92.2')")
    revision: str = Field(..., description="Standard revision/year (e.g., '2021')")

    class Config:
        frozen = True


class TemplateIntent(BaseModel):
    """Template intent and applicability indicators."""
    inspection_kind: str = Field(..., description="Type of inspection (PERIODIC, POST_REPAIR, etc.)")
    domain: str = Field(..., description="Equipment domain (AERIAL_DEVICE, CRANE, etc.)")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")

    class Config:
        frozen = True


class ApplicabilityRules(BaseModel):
    """Rules for determining if template applies to an asset."""
    asset_types: Optional[List[str]] = Field(default=None, description="Applicable asset types")
    required_capabilities: Optional[List[str]] = Field(default=None, description="Required capabilities")
    optional_capabilities: Optional[List[str]] = Field(default=None, description="Optional capabilities")
    notes: Optional[str] = Field(default=None, description="Additional applicability notes")

    class Config:
        frozen = True


class EvidenceRules(BaseModel):
    """Rules for evidence collection (photos, notes)."""
    photo_required_if_severity_at_least: Optional[str] = None
    notes_required_on_fail: bool = False
    block_finalize_if_required_steps_incomplete: bool = True

    class Config:
        frozen = True


class HashingPolicy(BaseModel):
    """Policy for template hashing."""
    canonicalization: str = "JSON_CANONICAL_SORT_KEYS_UTF8_NO_WHITESPACE"
    hash_algorithm: str = "SHA256"

    class Config:
        frozen = True


class TemplatePolicy(BaseModel):
    """Template execution policies."""
    evidence_rules: EvidenceRules
    hashing: HashingPolicy

    class Config:
        frozen = True


class TemplateMetadata(BaseModel):
    """Template metadata and configuration."""
    template_key: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Human-readable template name")
    status: TemplateStatus = Field(..., description="Publication status")
    standard: StandardReference = Field(..., description="Standard reference")
    intent: TemplateIntent = Field(..., description="Template intent")
    applicability: Optional[ApplicabilityRules] = Field(default=None, description="Applicability rules")
    policy: TemplatePolicy = Field(..., description="Template policies")

    class Config:
        frozen = True


# ============================================================================
# Schema Definitions (for fields, defects, measurements)
# ============================================================================

class SchemaField(BaseModel):
    """Field definition in a schema."""
    field_id: str
    label: Optional[str] = None
    type: Union[FieldType, str]  # Allow string for flexibility
    required: bool = False
    enum_ref: Optional[str] = None
    values: Optional[List[str]] = None
    precision: Optional[int] = None
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None
    help_text: Optional[str] = None

    class Config:
        use_enum_values = True


class MeasurementSet(BaseModel):
    """Measurement set definition."""
    measurement_set_id: str
    title: str
    fields: List[SchemaField]


class DefectSchema(BaseModel):
    """Schema for defect recording."""
    defect_id_format: str = "UUID"
    fields: List[SchemaField]


class TemplateSchemas(BaseModel):
    """All schema definitions for a template."""
    measurement_sets: Optional[List[MeasurementSet]] = None
    defect_schema: Optional[DefectSchema] = None


# ============================================================================
# Procedure Definitions (steps, inputs, validations)
# ============================================================================

class ConditionWhen(BaseModel):
    """Condition for when something applies."""
    path: Optional[str] = None
    equals: Optional[Any] = None
    in_: Optional[List[Any]] = Field(default=None, alias="in")
    all: Optional[List[Dict]] = None
    any: Optional[List[Dict]] = None

    class Config:
        allow_population_by_field_name = True


class AutoDefect(BaseModel):
    """Auto-generated defect definition."""
    when: ConditionWhen
    defect: Dict[str, Any]  # Title, severity, standard_reference, etc.


class StepValidation(BaseModel):
    """Validation rule for a step."""
    validation_id: str
    type: str
    rule: str


class UIGuidance(BaseModel):
    """UI guidance for a step."""
    mode: Optional[str] = None
    guidance: Optional[List[str]] = None


class ProcedureInput(BaseModel):
    """Input field for procedure initialization."""
    input_id: str
    label: Optional[str] = None
    type: Union[FieldType, str]
    required: bool = False
    enum_ref: Optional[str] = None
    help_text: Optional[str] = None


class ProcedureStep(BaseModel):
    """A single step in an inspection procedure."""
    step_key: str = Field(..., description="Unique step identifier within template")
    type: Union[StepType, str] = Field(..., description="Step type")
    title: str = Field(..., description="Step title")
    standard_reference: Optional[str] = Field(default=None, description="Reference to standard section")
    required: bool = Field(default=True, description="Whether step is required")
    blocking_fail: Optional[bool] = Field(default=None, description="Blocks inspection if failed")
    defect_schema_ref: Optional[str] = None
    ui: Optional[UIGuidance] = None
    fields: List[SchemaField] = Field(default_factory=list)
    validations: Optional[List[StepValidation]] = None
    auto_defect_on: Optional[List[AutoDefect]] = None

    class Config:
        use_enum_values = True

    @validator('step_key')
    def step_key_valid_format(cls, v):
        """Validate step key format."""
        if not v or not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('step_key must be alphanumeric with underscores/hyphens')
        return v


class Procedure(BaseModel):
    """Inspection procedure definition."""
    inputs: Optional[List[ProcedureInput]] = Field(default_factory=list)
    steps: List[ProcedureStep] = Field(..., min_items=1)

    @validator('steps')
    def steps_have_unique_keys(cls, v):
        """Validate step keys are unique."""
        keys = [step.step_key for step in v]
        if len(keys) != len(set(keys)):
            duplicates = [k for k in keys if keys.count(k) > 1]
            raise ValueError(f'Duplicate step keys found: {duplicates}')
        return v


# ============================================================================
# Rule Definitions (automated defect generation)
# ============================================================================

class RuleAssertion(BaseModel):
    """Assertion to evaluate in a rule."""
    type: str
    left: Optional[Dict[str, Any]] = None
    right: Optional[Any] = None
    right_formula: Optional[str] = None


class RuleOnFail(BaseModel):
    """Action when rule fails."""
    severity: str
    defect_title: str
    defect_description: Optional[str] = None
    standard_reference: Optional[str] = None


class InspectionRule(BaseModel):
    """Automated rule for defect generation."""
    rule_id: str
    title: str
    standard_reference: Optional[str] = None
    when: Optional[Union[Dict[str, Any], ConditionWhen]] = None
    assert_: Optional[RuleAssertion] = Field(default=None, alias="assert")
    on_fail: RuleOnFail

    class Config:
        allow_population_by_field_name = True


# ============================================================================
# Complete Template Schema
# ============================================================================

class InspectionTemplate(BaseModel):
    """
    Complete inspection template validation schema.

    This validates the AF_INSPECTION_TEMPLATE format used by asset_templates_v2_3.
    """
    format: Literal["AF_INSPECTION_TEMPLATE"] = Field(..., description="Template format identifier")
    format_version: int = Field(..., description="Format version number")
    template: TemplateMetadata = Field(..., description="Template metadata")
    enums: Dict[str, List[str]] = Field(default_factory=dict, description="Enumerated value definitions")
    schemas: Optional[TemplateSchemas] = Field(default=None, description="Schema definitions")
    procedure: Procedure = Field(..., description="Inspection procedure")
    rules: Optional[List[InspectionRule]] = Field(default_factory=list, description="Automated rules")

    class Config:
        validate_assignment = True

    @validator('format_version')
    def format_version_supported(cls, v):
        """Validate format version is supported."""
        if v != 1:
            raise ValueError(f'Unsupported format version: {v}. Only version 1 is supported.')
        return v

    def get_enum_values(self, enum_ref: str) -> Optional[List[str]]:
        """Get enum values by reference."""
        return self.enums.get(enum_ref)

    def get_step(self, step_key: str) -> Optional[ProcedureStep]:
        """Get step by key."""
        for step in self.procedure.steps:
            if step.step_key == step_key:
                return step
        return None

    def get_required_steps(self) -> List[ProcedureStep]:
        """Get all required steps."""
        return [step for step in self.procedure.steps if step.required]

    def get_blocking_steps(self) -> List[ProcedureStep]:
        """Get steps that block inspection if failed."""
        return [step for step in self.procedure.steps if step.blocking_fail]

    def count_steps(self) -> int:
        """Count total steps in procedure."""
        return len(self.procedure.steps)

    def count_rules(self) -> int:
        """Count automated rules."""
        return len(self.rules) if self.rules else 0


# ============================================================================
# Template Summary (for listing templates)
# ============================================================================

class TemplateSummary(BaseModel):
    """
    Lightweight template summary for listing.

    Used when returning lists of templates without full details.
    """
    template_key: str
    name: str
    status: TemplateStatus
    standard_code: str
    standard_revision: str
    inspection_kind: str
    domain: str
    tags: List[str]
    step_count: int
    rule_count: int
    required_capabilities: Optional[List[str]] = None

    class Config:
        frozen = True

    @classmethod
    def from_template(cls, template: InspectionTemplate) -> "TemplateSummary":
        """Create summary from full template."""
        return cls(
            template_key=template.template.template_key,
            name=template.template.name,
            status=template.template.status,
            standard_code=template.template.standard.code,
            standard_revision=template.template.standard.revision,
            inspection_kind=template.template.intent.inspection_kind,
            domain=template.template.intent.domain,
            tags=template.template.intent.tags,
            step_count=template.count_steps(),
            rule_count=template.count_rules(),
            required_capabilities=(
                template.template.applicability.required_capabilities
                if template.template.applicability
                else None
            )
        )
