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
    }

    @classmethod
    @transaction.atomic
    def generate_defects_for_inspection(
        cls,
        inspection_run: InspectionRun
    ) -> List[InspectionDefect]:
        """
        Evaluate all rules and generate defects for failed rules.

        Args:
            inspection_run: InspectionRun to evaluate

        Returns:
            List of created/updated InspectionDefect objects
        """
        template = inspection_run.template_snapshot
        step_data = inspection_run.step_data or {}

        # Evaluate all rules
        evaluation_results = RuleEvaluator.evaluate_all_rules(template, step_data)

        # Generate defects for failures
        defects = []
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
