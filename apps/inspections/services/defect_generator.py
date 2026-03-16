"""
Defect Generation Service

Creates InspectionDefect records from rule evaluation results.
Implements idempotent defect creation using defect_identity hashing.
"""

from typing import Dict, Any, List, Optional
from django.utils import timezone
from django.db import transaction

from apps.inspections.models import InspectionRun, InspectionDefect
from apps.inspections.services.rule_evaluator import RuleEvaluator, RuleEvaluationResult


class DefectGenerator:
    """
    Service for generating defects from rule evaluation.

    Features:
    - Idempotent defect creation (using defect_identity hash)
    - Severity mapping from template to model
    - Evaluation trace storage for audit
    """

    # Map template severity to model severity
    SEVERITY_MAP = {
        'UNSAFE_OUT_OF_SERVICE': 'CRITICAL',
        'DEGRADED_PERFORMANCE': 'MAJOR',
        'MINOR_ISSUE': 'MINOR',
        'ADVISORY_NOTICE': 'ADVISORY',
        # Direct mappings (if template uses model values)
        'CRITICAL': 'CRITICAL',
        'MAJOR': 'MAJOR',
        'MINOR': 'MINOR',
        'ADVISORY': 'ADVISORY',
        # Defect schema severity values (from ADD_DEFECT_ITEMS mode)
        'SERVICE_REQUIRED': 'MAJOR',
        'SAFE': 'ADVISORY',
    }

    @classmethod
    @transaction.atomic
    def generate_defects_for_inspection(
        cls,
        inspection_run: InspectionRun
    ) -> List[InspectionDefect]:
        """
        Generate defects from both rules and manual defects in step_data.

        This processes two types of defects:
        1. Auto-generated defects from rule evaluation (auto_defect_on)
        2. Manual defects from structured defect capture (ADD_DEFECT_ITEMS mode)

        Args:
            inspection_run: InspectionRun to evaluate

        Returns:
            List of created/updated InspectionDefect objects
        """
        template = inspection_run.template_snapshot
        step_data = inspection_run.step_data or {}

        defects = []

        # 1. Generate defects from rule evaluation (existing logic)
        evaluation_results = RuleEvaluator.evaluate_all_rules(template, step_data)
        for result in evaluation_results:
            if not result.passed:
                # Find rule definition
                rule = cls._find_rule(template, result.rule_id)
                if rule:
                    defect = cls.create_defect_from_rule(
                        inspection_run=inspection_run,
                        rule=rule,
                        evaluation_result=result
                    )
                    if defect:
                        defects.append(defect)

        # 2. Process manual defects from step_data (NEW)
        manual_defects = cls.process_manual_defects(inspection_run, step_data)
        defects.extend(manual_defects)

        return defects

    @classmethod
    def create_defect_from_rule(
        cls,
        inspection_run: InspectionRun,
        rule: Dict[str, Any],
        evaluation_result: RuleEvaluationResult
    ) -> Optional[InspectionDefect]:
        """
        Create or update defect from rule failure.

        Uses defect_identity for idempotency - re-running won't create duplicates.

        Args:
            inspection_run: InspectionRun instance
            rule: Rule definition from template
            evaluation_result: Result of rule evaluation

        Returns:
            InspectionDefect instance (created or existing)
        """
        rule_id = rule.get('rule_id')
        step_key = evaluation_result.step_key
        on_fail = rule.get('on_fail', {})

        # Generate defect identity (idempotency key)
        defect_identity = InspectionDefect.generate_defect_identity(
            inspection_run_id=inspection_run.id,
            module_key='',  # Not using modules in current template format
            step_key=step_key,
            rule_id=rule_id
        )

        # Map severity
        template_severity = on_fail.get('severity', 'ADVISORY_NOTICE')
        model_severity = cls.map_severity(template_severity)

        # Build defect details
        defect_details = {
            'rule_id': rule_id,
            'step_key': step_key,
            'actual_value': evaluation_result.actual_value,
            'expected_value': evaluation_result.expected_value,
            'assertion_type': evaluation_result.assertion_type
        }

        # Build evaluation trace for audit
        evaluation_trace = evaluation_result.to_dict()
        evaluation_trace['evaluated_at'] = timezone.now().isoformat()
        evaluation_trace['rule_definition'] = rule

        # Get or create defect (idempotent)
        defect, created = InspectionDefect.objects.get_or_create(
            defect_identity=defect_identity,
            defaults={
                'inspection_run': inspection_run,
                'module_key': '',  # Not using modules in current format
                'step_key': step_key,
                'rule_id': rule_id,
                'severity': model_severity,
                'status': 'OPEN',
                'title': on_fail.get('defect_title', rule.get('title', 'Rule failed')),
                'description': on_fail.get('defect_description', '') or cls._build_defect_description(rule, evaluation_result),
                'defect_details': defect_details,
                'evaluation_trace': evaluation_trace
            }
        )

        # If defect already exists, update it with latest evaluation
        if not created:
            defect.defect_details = defect_details
            defect.evaluation_trace = evaluation_trace
            defect.save()

        return defect

    @classmethod
    def process_manual_defects(
        cls,
        inspection_run: InspectionRun,
        step_data: Dict[str, Any]
    ) -> List[InspectionDefect]:
        """
        Process manual defects from step_data.

        Converts defects captured via ADD_DEFECT_ITEMS mode into InspectionDefect records.
        Defects are stored in step_data as:
        step_data[step_key]['defects'] = [
            {
                'defect_id': 'uuid',
                'title': '...',
                'severity': 'SERVICE_REQUIRED',
                'description': '...',
                'component': '...',
                'location': '...',
                'photo_evidence': ['photo1.jpg', ...],
                'corrective_action': '...',
                'standard_reference': '...'
            }
        ]

        Args:
            inspection_run: InspectionRun instance
            step_data: Step data dict

        Returns:
            List of created InspectionDefect objects
        """
        defects = []

        # Iterate through all steps in step_data
        for step_key, step_values in step_data.items():
            if not isinstance(step_values, dict):
                continue

            # Check if step has defects array
            step_defects = step_values.get('defects', [])
            if not isinstance(step_defects, list):
                continue

            # Process each defect in the step
            for defect_data in step_defects:
                if not isinstance(defect_data, dict):
                    continue

                try:
                    defect = cls.create_defect_from_manual_data(
                        inspection_run=inspection_run,
                        step_key=step_key,
                        defect_data=defect_data
                    )
                    if defect:
                        defects.append(defect)
                except Exception:
                    # Skip invalid defects and continue processing
                    pass

        return defects

    @classmethod
    def create_defect_from_manual_data(
        cls,
        inspection_run: InspectionRun,
        step_key: str,
        defect_data: Dict[str, Any]
    ) -> Optional[InspectionDefect]:
        """
        Create InspectionDefect from manual defect data.

        Args:
            inspection_run: InspectionRun instance
            step_key: Step where defect was captured
            defect_data: Defect data from step_data.defects array

        Returns:
            InspectionDefect instance
        """
        # Generate defect identity for idempotency
        # Use defect_id from frontend as part of identity
        defect_id = defect_data.get('defect_id', '')
        defect_identity = InspectionDefect.generate_defect_identity(
            inspection_run_id=inspection_run.id,
            module_key='',
            step_key=step_key,
            rule_id=f"manual_{defect_id}"
        )

        # Map severity from defect schema to model
        template_severity = defect_data.get('severity', 'MINOR')
        model_severity = cls.map_severity(template_severity)

        # Build defect_details from defect schema fields
        defect_details = {
            'component': defect_data.get('component'),
            'location': defect_data.get('location'),
            'photos': defect_data.get('photo_evidence', []),
            'corrective_action': defect_data.get('corrective_action'),
            'standard_reference': defect_data.get('standard_reference'),
            'source': 'manual',
            'defect_id': defect_id,
        }

        # Build evaluation trace
        evaluation_trace = {
            'type': 'manual_defect',
            'captured_at': timezone.now().isoformat(),
            'step_key': step_key,
            'defect_data': defect_data
        }

        # Get or create defect (idempotent)
        defect, created = InspectionDefect.objects.get_or_create(
            defect_identity=defect_identity,
            defaults={
                'inspection_run': inspection_run,
                'module_key': '',
                'step_key': step_key,
                'rule_id': None,  # No rule for manual defects
                'severity': model_severity,
                'status': 'OPEN',
                'title': defect_data.get('title', 'Manual defect'),
                'description': defect_data.get('description', ''),
                'defect_details': defect_details,
                'evaluation_trace': evaluation_trace
            }
        )

        # If defect already exists, update it
        if not created:
            defect.title = defect_data.get('title', 'Manual defect')
            defect.description = defect_data.get('description', '')
            defect.severity = model_severity
            defect.defect_details = defect_details
            defect.evaluation_trace = evaluation_trace
            defect.save()

        return defect

    @classmethod
    def map_severity(cls, template_severity: str) -> str:
        """
        Map template severity to model severity.

        Args:
            template_severity: Severity from template (e.g., 'UNSAFE_OUT_OF_SERVICE')

        Returns:
            Model severity (CRITICAL, MAJOR, MINOR, ADVISORY)
        """
        return cls.SEVERITY_MAP.get(template_severity, 'MINOR')

    @classmethod
    def _find_rule(cls, template: Dict[str, Any], rule_id: str) -> Optional[Dict[str, Any]]:
        """Find rule definition by ID in template."""
        rules = template.get('rules', [])
        for rule in rules:
            if rule.get('rule_id') == rule_id:
                return rule
        return None

    @classmethod
    def _build_defect_description(
        cls,
        rule: Dict[str, Any],
        evaluation_result: RuleEvaluationResult
    ) -> str:
        """
        Build default defect description when not provided in template.

        Args:
            rule: Rule definition
            evaluation_result: Evaluation result

        Returns:
            Generated description
        """
        parts = []

        # Add rule title
        title = rule.get('title')
        if title:
            parts.append(title)

        # Add standard reference
        standard_ref = rule.get('standard_reference')
        if standard_ref:
            parts.append(f"Standard: {standard_ref}")

        # Add actual vs expected
        if evaluation_result.actual_value is not None:
            parts.append(f"Actual value: {evaluation_result.actual_value}")
        if evaluation_result.expected_value is not None:
            parts.append(f"Expected value: {evaluation_result.expected_value}")

        return '\n'.join(parts) if parts else 'Rule evaluation failed'

    @classmethod
    def get_defect_summary(cls, inspection_run: InspectionRun) -> Dict[str, Any]:
        """
        Get summary of defects for inspection.

        Args:
            inspection_run: InspectionRun to summarize

        Returns:
            Dict with defect counts by severity and status
        """
        # Use direct queries to avoid caching issues
        from apps.inspections.models import InspectionDefect

        defects_qs = InspectionDefect.objects.filter(inspection_run=inspection_run)

        # Calculate severity counts
        severity_counts = {
            'CRITICAL': defects_qs.filter(severity='CRITICAL').count(),
            'MAJOR': defects_qs.filter(severity='MAJOR').count(),
            'MINOR': defects_qs.filter(severity='MINOR').count(),
            'ADVISORY': defects_qs.filter(severity='ADVISORY').count(),
        }

        # Calculate status counts
        status_counts = {
            'OPEN': defects_qs.filter(status='OPEN').count(),
            'WORK_ORDER_CREATED': defects_qs.filter(status='WORK_ORDER_CREATED').count(),
            'RESOLVED': defects_qs.filter(status='RESOLVED').count(),
        }

        # Total is sum of all severities
        total = sum(severity_counts.values())

        summary = {
            'total_defects': total,
            'by_severity': severity_counts,
            'by_status': status_counts,
        }

        return summary
