"""
Response Validation Service

Validates inspection step responses against template field schemas.
Ensures data integrity and enforces required field rules.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from decimal import Decimal, InvalidOperation


class ValidationError(Exception):
    """Validation error with details."""
    def __init__(self, field_id: str, message: str, value: Any = None):
        self.field_id = field_id
        self.message = message
        self.value = value
        super().__init__(f"{field_id}: {message}")


class FieldValidationResult:
    """Result of validating a single field."""
    def __init__(self, valid: bool, field_id: str, errors: List[str] = None):
        self.valid = valid
        self.field_id = field_id
        self.errors = errors or []

    def __bool__(self):
        return self.valid


class StepValidationResult:
    """Result of validating an entire step."""
    def __init__(self, valid: bool, step_key: str, field_results: Dict[str, FieldValidationResult] = None, errors: List[str] = None):
        self.valid = valid
        self.step_key = step_key
        self.field_results = field_results or {}
        self.errors = errors or []

    def __bool__(self):
        return self.valid

    @property
    def all_errors(self) -> List[str]:
        """Get all errors from step and fields."""
        errors = list(self.errors)
        for field_result in self.field_results.values():
            errors.extend(field_result.errors)
        return errors


class ResponseValidator:
    """
    Validates inspection responses against template schemas.

    Supported field types:
    - BOOLEAN: true/false values
    - TEXT: String values
    - TEXTAREA: Multi-line text
    - NUMBER: Numeric values (int or float)
    - ENUM: Single selection from predefined values
    - CHOICE_MULTI: Multiple selections from predefined values
    - ATTACHMENTS: File attachments (array of attachment objects)
    """

    SUPPORTED_FIELD_TYPES = [
        'BOOLEAN',
        'TEXT',
        'TEXTAREA',
        'NUMBER',
        'ENUM',
        'CHOICE_MULTI',
        'ATTACHMENTS'
    ]

    @classmethod
    def validate_step_response(cls, template_step: Dict[str, Any], field_data: Dict[str, Any]) -> StepValidationResult:
        """
        Validate complete step response against template.

        Args:
            template_step: Step definition from template
            field_data: Field responses to validate

        Returns:
            StepValidationResult with validation status and errors
        """
        step_key = template_step.get('step_key')
        fields = template_step.get('fields', [])
        errors = []
        field_results = {}

        # Check for required fields
        for field in fields:
            field_id = field.get('field_id')
            required = field.get('required', False)

            if required and field_id not in field_data:
                field_results[field_id] = FieldValidationResult(
                    valid=False,
                    field_id=field_id,
                    errors=[f"Required field '{field_id}' is missing"]
                )
            elif field_id in field_data:
                # Validate field value
                field_result = cls.validate_field(field, field_data[field_id])
                field_results[field_id] = field_result

        # Check for unknown fields
        known_field_ids = {f.get('field_id') for f in fields}
        for field_id in field_data.keys():
            if field_id not in known_field_ids:
                errors.append(f"Unknown field '{field_id}' not in template")

        # Overall validity
        valid = all(fr.valid for fr in field_results.values()) and len(errors) == 0

        return StepValidationResult(
            valid=valid,
            step_key=step_key,
            field_results=field_results,
            errors=errors
        )

    @classmethod
    def validate_field(cls, field_schema: Dict[str, Any], value: Any) -> FieldValidationResult:
        """
        Validate single field value against schema.

        Args:
            field_schema: Field definition from template
            value: Value to validate

        Returns:
            FieldValidationResult with validation status and errors
        """
        field_id = field_schema.get('field_id')
        field_type = field_schema.get('type')
        errors = []

        # Handle None/null values
        if value is None:
            if field_schema.get('required', False):
                errors.append("Value is required but was None")
            return FieldValidationResult(valid=len(errors) == 0, field_id=field_id, errors=errors)

        # Validate by type
        if field_type == 'BOOLEAN':
            errors.extend(cls._validate_boolean(field_id, value))
        elif field_type in ('TEXT', 'TEXTAREA'):
            errors.extend(cls._validate_text(field_id, value, field_schema))
        elif field_type == 'NUMBER':
            errors.extend(cls._validate_number(field_id, value, field_schema))
        elif field_type == 'ENUM':
            errors.extend(cls._validate_enum(field_id, value, field_schema))
        elif field_type == 'CHOICE_MULTI':
            errors.extend(cls._validate_choice_multi(field_id, value, field_schema))
        elif field_type == 'ATTACHMENTS':
            errors.extend(cls._validate_attachments(field_id, value))
        else:
            errors.append(f"Unsupported field type '{field_type}'")

        return FieldValidationResult(
            valid=len(errors) == 0,
            field_id=field_id,
            errors=errors
        )

    @classmethod
    def _validate_boolean(cls, field_id: str, value: Any) -> List[str]:
        """Validate boolean field."""
        if not isinstance(value, bool):
            return [f"Expected boolean, got {type(value).__name__}"]
        return []

    @classmethod
    def _validate_text(cls, field_id: str, value: Any, schema: Dict[str, Any]) -> List[str]:
        """Validate text/textarea field."""
        errors = []

        if not isinstance(value, str):
            return [f"Expected string, got {type(value).__name__}"]

        # Check min/max length if specified
        min_length = schema.get('min_length')
        max_length = schema.get('max_length')

        if min_length is not None and len(value) < min_length:
            errors.append(f"Text must be at least {min_length} characters (got {len(value)})")

        if max_length is not None and len(value) > max_length:
            errors.append(f"Text must be at most {max_length} characters (got {len(value)})")

        return errors

    @classmethod
    def _validate_number(cls, field_id: str, value: Any, schema: Dict[str, Any]) -> List[str]:
        """Validate numeric field."""
        errors = []

        # Accept int, float, or Decimal
        if not isinstance(value, (int, float, Decimal)):
            # Try to convert string to number
            if isinstance(value, str):
                try:
                    value = Decimal(value)
                except (InvalidOperation, ValueError):
                    return [f"Expected number, got string that cannot be converted: '{value}'"]
            else:
                return [f"Expected number, got {type(value).__name__}"]

        # Convert to Decimal for consistent comparison
        try:
            num_value = Decimal(str(value))
        except (InvalidOperation, ValueError):
            return [f"Cannot convert {value} to number"]

        # Check min/max if specified
        min_value = schema.get('min')
        max_value = schema.get('max')

        if min_value is not None:
            try:
                if num_value < Decimal(str(min_value)):
                    errors.append(f"Value must be at least {min_value} (got {value})")
            except (InvalidOperation, ValueError):
                pass

        if max_value is not None:
            try:
                if num_value > Decimal(str(max_value)):
                    errors.append(f"Value must be at most {max_value} (got {value})")
            except (InvalidOperation, ValueError):
                pass

        return errors

    @classmethod
    def _validate_enum(cls, field_id: str, value: Any, schema: Dict[str, Any]) -> List[str]:
        """Validate enum field (single selection)."""
        if not isinstance(value, str):
            return [f"Expected string enum value, got {type(value).__name__}"]

        allowed_values = schema.get('values', [])
        if not allowed_values:
            return ["Enum field has no allowed values defined"]

        if value not in allowed_values:
            return [f"Value '{value}' not in allowed values: {allowed_values}"]

        return []

    @classmethod
    def _validate_choice_multi(cls, field_id: str, value: Any, schema: Dict[str, Any]) -> List[str]:
        """Validate multi-choice field."""
        errors = []

        if not isinstance(value, list):
            return [f"Expected array for multi-choice, got {type(value).__name__}"]

        allowed_values = schema.get('values', [])
        if not allowed_values:
            return ["Multi-choice field has no allowed values defined"]

        for item in value:
            if not isinstance(item, str):
                errors.append(f"All choices must be strings, got {type(item).__name__}")
            elif item not in allowed_values:
                errors.append(f"Value '{item}' not in allowed values: {allowed_values}")

        # Check min/max selections if specified
        min_selections = schema.get('min_selections')
        max_selections = schema.get('max_selections')

        if min_selections is not None and len(value) < min_selections:
            errors.append(f"Must select at least {min_selections} options (got {len(value)})")

        if max_selections is not None and len(value) > max_selections:
            errors.append(f"Must select at most {max_selections} options (got {len(value)})")

        return errors

    @classmethod
    def _validate_attachments(cls, field_id: str, value: Any) -> List[str]:
        """Validate attachments field."""
        errors = []

        if not isinstance(value, list):
            return [f"Expected array for attachments, got {type(value).__name__}"]

        for idx, attachment in enumerate(value):
            if not isinstance(attachment, dict):
                errors.append(f"Attachment {idx} must be an object, got {type(attachment).__name__}")
                continue

            # Check for required attachment fields
            if 'filename' not in attachment:
                errors.append(f"Attachment {idx} missing 'filename'")
            if 'url' not in attachment and 'file_data' not in attachment:
                errors.append(f"Attachment {idx} missing 'url' or 'file_data'")

        return errors

    @classmethod
    def check_required_steps(cls, template: Dict[str, Any], step_data: Dict[str, Any]) -> List[str]:
        """
        Check which required steps are missing or incomplete.

        Args:
            template: Full template dict
            step_data: Current step data from InspectionRun

        Returns:
            List of step_keys for required steps that are missing/incomplete
        """
        missing_steps = []
        steps = template.get('procedure', {}).get('steps', [])

        for step in steps:
            step_key = step.get('step_key')
            required = step.get('required', False)

            if required and step_key not in step_data:
                missing_steps.append(step_key)
            elif required and step_key in step_data:
                # Check if any required fields are missing
                fields = step.get('fields', [])
                step_responses = step_data[step_key]

                for field in fields:
                    field_id = field.get('field_id')
                    field_required = field.get('required', False)

                    if field_required and field_id not in step_responses:
                        missing_steps.append(step_key)
                        break  # Only add step once

        return missing_steps
