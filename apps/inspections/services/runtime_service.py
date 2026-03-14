"""
Inspection Runtime Service

Manages inspection execution lifecycle:
- Creating inspections from templates
- Saving step responses
- Tracking completion
- Finalizing inspections
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from apps.inspections.models import InspectionRun, InspectionDefect
from apps.inspections.services.template_service import TemplateService
from apps.inspections.services.validation_service import ResponseValidator, StepValidationResult
from apps.inspections.services.defect_generator import DefectGenerator


class InspectionRuntimeError(Exception):
    """Base exception for runtime errors."""
    pass


class InspectionAlreadyFinalizedException(InspectionRuntimeError):
    """Raised when trying to modify a finalized inspection."""
    pass


class InspectionNotReadyException(InspectionRuntimeError):
    """Raised when trying to finalize an incomplete inspection."""
    pass


class CompletionStatus:
    """Inspection completion status."""
    def __init__(
        self,
        total_steps: int,
        completed_steps: int,
        required_steps: int,
        required_completed: int,
        completion_percentage: float,
        missing_required_steps: List[str],
        ready_to_finalize: bool
    ):
        self.total_steps = total_steps
        self.completed_steps = completed_steps
        self.required_steps = required_steps
        self.required_completed = required_completed
        self.completion_percentage = completion_percentage
        self.missing_required_steps = missing_required_steps
        self.ready_to_finalize = ready_to_finalize

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_steps': self.total_steps,
            'completed_steps': self.completed_steps,
            'required_steps': self.required_steps,
            'required_completed': self.required_completed,
            'completion_percentage': round(self.completion_percentage, 1),
            'missing_required_steps': self.missing_required_steps,
            'ready_to_finalize': self.ready_to_finalize
        }


class InspectionRuntime:
    """
    Service for managing inspection execution.

    Handles:
    - Creating inspections from templates
    - Saving/retrieving step responses
    - Validating responses
    - Tracking completion
    - Finalizing inspections
    """

    @classmethod
    @transaction.atomic
    def create_inspection(
        cls,
        template_key: str,
        asset,
        inspector_name: str = '',
        started_at: Optional[datetime] = None
    ) -> InspectionRun:
        """
        Create new inspection run from template.

        Args:
            template_key: Template to use
            asset: Vehicle or Equipment instance
            inspector_name: Name of inspector
            started_at: When inspection started (defaults to now)

        Returns:
            InspectionRun instance (status=DRAFT)

        Raises:
            TemplateNotFoundError: If template doesn't exist
            ValidationError: If asset validation fails
        """
        # Load template
        template = TemplateService.load_template(template_key)

        # Determine asset type
        from apps.assets.models import Vehicle, Equipment
        if isinstance(asset, Vehicle):
            asset_type = 'VEHICLE'
        elif isinstance(asset, Equipment):
            asset_type = 'EQUIPMENT'
        else:
            raise ValueError(f"Asset must be Vehicle or Equipment, got {type(asset)}")

        # Create inspection run
        inspection = InspectionRun(
            asset_type=asset_type,
            asset_id=asset.id,
            customer=asset.customer,
            template_key=template_key,
            program_key=template.get('template', {}).get('program_key', ''),
            status='DRAFT',
            started_at=started_at or timezone.now(),
            inspector_name=inspector_name,
            template_snapshot=template,  # Immutable copy
            step_data={}
        )

        # Validate and save
        inspection.save()

        return inspection

    @classmethod
    @transaction.atomic
    def save_step_response(
        cls,
        inspection_run: InspectionRun,
        step_key: str,
        field_data: Dict[str, Any],
        validate: bool = True
    ) -> StepValidationResult:
        """
        Save step response data.

        Args:
            inspection_run: InspectionRun to update
            step_key: Step key being responded to
            field_data: Field responses
            validate: Whether to validate before saving

        Returns:
            StepValidationResult

        Raises:
            InspectionAlreadyFinalizedException: If inspection is finalized
            ValidationError: If validation fails
        """
        # Check if finalized
        if inspection_run.is_finalized:
            raise InspectionAlreadyFinalizedException(
                f"Cannot modify finalized inspection {inspection_run.id}"
            )

        # Find step in template
        template_step = cls._find_template_step(inspection_run.template_snapshot, step_key)
        if not template_step:
            raise ValueError(f"Step '{step_key}' not found in template")

        # Validate if requested
        validation_result = None
        if validate:
            validation_result = ResponseValidator.validate_step_response(template_step, field_data)
            if not validation_result.valid:
                raise DjangoValidationError(
                    f"Validation failed for step '{step_key}': {validation_result.all_errors}"
                )

        # Save response
        if inspection_run.step_data is None:
            inspection_run.step_data = {}

        inspection_run.step_data[step_key] = {
            **field_data,
            'completed_at': timezone.now().isoformat()
        }

        # Update status to IN_PROGRESS if still DRAFT
        if inspection_run.status == 'DRAFT':
            inspection_run.status = 'IN_PROGRESS'

        inspection_run.save()

        return validation_result or StepValidationResult(valid=True, step_key=step_key)

    @classmethod
    def get_step_response(cls, inspection_run: InspectionRun, step_key: str) -> Optional[Dict[str, Any]]:
        """
        Get saved response for a step.

        Args:
            inspection_run: InspectionRun to query
            step_key: Step key to retrieve

        Returns:
            Dict of field responses or None if not found
        """
        if not inspection_run.step_data:
            return None

        return inspection_run.step_data.get(step_key)

    @classmethod
    def calculate_completion_status(cls, inspection_run: InspectionRun) -> CompletionStatus:
        """
        Calculate inspection completion status.

        Args:
            inspection_run: InspectionRun to check

        Returns:
            CompletionStatus with detailed progress
        """
        template = inspection_run.template_snapshot
        steps = template.get('procedure', {}).get('steps', [])
        step_data = inspection_run.step_data or {}

        total_steps = len(steps)
        completed_steps = len(step_data)
        required_steps = sum(1 for step in steps if step.get('required', False))
        required_completed = 0
        missing_required_steps = []

        # Check each required step
        for step in steps:
            step_key = step.get('step_key')
            required = step.get('required', False)

            if required:
                if step_key in step_data:
                    # Check if all required fields are present
                    fields = step.get('fields', [])
                    step_responses = step_data[step_key]
                    all_required_fields_present = True

                    for field in fields:
                        field_id = field.get('field_id')
                        field_required = field.get('required', False)

                        if field_required and field_id not in step_responses:
                            all_required_fields_present = False
                            break

                    if all_required_fields_present:
                        required_completed += 1
                    else:
                        missing_required_steps.append(step_key)
                else:
                    missing_required_steps.append(step_key)

        # Calculate percentage
        completion_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0

        # Ready to finalize if all required steps complete
        ready_to_finalize = len(missing_required_steps) == 0

        return CompletionStatus(
            total_steps=total_steps,
            completed_steps=completed_steps,
            required_steps=required_steps,
            required_completed=required_completed,
            completion_percentage=completion_percentage,
            missing_required_steps=missing_required_steps,
            ready_to_finalize=ready_to_finalize
        )

    @classmethod
    @transaction.atomic
    def finalize_inspection(
        cls,
        inspection_run: InspectionRun,
        signature_data: Optional[Dict[str, Any]] = None,
        force: bool = False
    ) -> InspectionRun:
        """
        Finalize inspection, making it immutable.

        Args:
            inspection_run: InspectionRun to finalize
            signature_data: Optional digital signature data
            force: Allow finalizing even if incomplete (use with caution)

        Returns:
            Updated InspectionRun

        Raises:
            InspectionAlreadyFinalizedException: If already finalized
            InspectionNotReadyException: If required steps incomplete
        """
        # Check if already finalized
        if inspection_run.is_finalized:
            raise InspectionAlreadyFinalizedException(
                f"Inspection {inspection_run.id} is already finalized"
            )

        # Check completion status
        if not force:
            completion = cls.calculate_completion_status(inspection_run)
            if not completion.ready_to_finalize:
                raise InspectionNotReadyException(
                    f"Cannot finalize: missing required steps: {completion.missing_required_steps}"
                )

        # Update inspection
        inspection_run.status = 'COMPLETED'
        inspection_run.finalized_at = timezone.now()

        if signature_data:
            # Handle both string (base64 image) and dict signature data
            if isinstance(signature_data, str):
                inspection_run.inspector_signature = {
                    'signature': signature_data,
                    'signed_at': timezone.now().isoformat()
                }
            else:
                inspection_run.inspector_signature = {
                    **signature_data,
                    'signed_at': timezone.now().isoformat()
                }

        inspection_run.save()

        return inspection_run

    @classmethod
    def _find_template_step(cls, template: Dict[str, Any], step_key: str) -> Optional[Dict[str, Any]]:
        """
        Find step definition in template.

        Args:
            template: Template dict
            step_key: Step key to find

        Returns:
            Step dict or None
        """
        steps = template.get('procedure', {}).get('steps', [])
        for step in steps:
            if step.get('step_key') == step_key:
                return step
        return None

    @classmethod
    def get_next_incomplete_step(cls, inspection_run: InspectionRun) -> Optional[Dict[str, Any]]:
        """
        Get the next incomplete step in the inspection.

        Args:
            inspection_run: InspectionRun to check

        Returns:
            Step dict or None if all complete
        """
        template = inspection_run.template_snapshot
        steps = template.get('procedure', {}).get('steps', [])
        step_data = inspection_run.step_data or {}

        for step in steps:
            step_key = step.get('step_key')
            if step_key not in step_data:
                return step

        return None

    @classmethod
    def clear_step_response(cls, inspection_run: InspectionRun, step_key: str):
        """
        Clear a step's response data.

        Args:
            inspection_run: InspectionRun to update
            step_key: Step key to clear

        Raises:
            InspectionAlreadyFinalizedException: If inspection is finalized
        """
        if inspection_run.is_finalized:
            raise InspectionAlreadyFinalizedException(
                f"Cannot modify finalized inspection {inspection_run.id}"
            )

        if inspection_run.step_data and step_key in inspection_run.step_data:
            del inspection_run.step_data[step_key]
            inspection_run.save()

    @classmethod
    @transaction.atomic
    def evaluate_rules(
        cls,
        inspection_run: InspectionRun
    ) -> List[InspectionDefect]:
        """
        Evaluate rules and generate defects for inspection.

        Can be called before finalization to preview defects,
        or automatically during finalization.

        Args:
            inspection_run: InspectionRun to evaluate

        Returns:
            List of InspectionDefect objects (created or updated)
        """
        return DefectGenerator.generate_defects_for_inspection(inspection_run)

    @classmethod
    @transaction.atomic
    def finalize_with_rules(
        cls,
        inspection_run: InspectionRun,
        signature_data: Optional[Dict[str, Any]] = None,
        force: bool = False,
        evaluate_rules: bool = True
    ) -> tuple[InspectionRun, List[InspectionDefect]]:
        """
        Finalize inspection with optional rule evaluation.

        Args:
            inspection_run: InspectionRun to finalize
            signature_data: Optional digital signature data
            force: Allow finalizing even if incomplete
            evaluate_rules: Whether to evaluate rules and generate defects

        Returns:
            Tuple of (finalized_inspection, generated_defects)

        Raises:
            InspectionAlreadyFinalizedException: If already finalized
            InspectionNotReadyException: If required steps incomplete (and not forced)
        """
        # Finalize the inspection first
        cls.finalize_inspection(inspection_run, signature_data, force)

        # Evaluate rules if requested
        defects = []
        if evaluate_rules:
            defects = cls.evaluate_rules(inspection_run)

        return (inspection_run, defects)
