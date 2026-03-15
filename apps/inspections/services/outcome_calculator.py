"""
Inspection Outcome Calculator

Auto-calculates inspection pass/fail outcome based on:
1. Defect severity levels
2. Blocking failures in steps
3. Template rules

The system decides - not the inspector.
"""

from typing import Dict, Any, List
from apps.inspections.models import InspectionRun, InspectionDefect


class OutcomeCalculator:
    """Calculate inspection outcome automatically based on defects and data."""

    @classmethod
    def calculate_outcome(
        cls,
        inspection_run: InspectionRun,
        defects: List[InspectionDefect] = None
    ) -> Dict[str, Any]:
        """
        Calculate inspection outcome based on defects and blocking failures.

        Logic:
        - FAIL: Any CRITICAL severity defects OR blocking step failures
        - PASS_WITH_REPAIRS: Any MAJOR severity defects (but no CRITICAL)
        - PASS: Only MINOR/ADVISORY defects or no defects

        Args:
            inspection_run: InspectionRun instance
            defects: List of InspectionDefect instances (if None, will query)

        Returns:
            Dict with:
                - outcome: 'PASS' | 'PASS_WITH_REPAIRS' | 'FAIL'
                - summary: Detailed breakdown
        """
        # Get defects if not provided
        if defects is None:
            defects = list(
                InspectionDefect.objects.filter(inspection_run=inspection_run)
            )

        # Count defects by severity
        defect_counts = {
            'CRITICAL': 0,
            'MAJOR': 0,
            'MINOR': 0,
            'ADVISORY': 0,
        }

        for defect in defects:
            severity = defect.severity
            if severity in defect_counts:
                defect_counts[severity] += 1

        # Check for blocking failures
        blocking_failures = cls._check_blocking_failures(inspection_run)

        # Determine outcome
        outcome = cls._determine_outcome(defect_counts, blocking_failures)

        # Build summary
        summary = {
            'total_defects': len(defects),
            'defects_by_severity': defect_counts,
            'blocking_failures': blocking_failures,
            'critical_defects_found': defect_counts['CRITICAL'] > 0,
            'major_defects_found': defect_counts['MAJOR'] > 0,
            'equipment_safe_for_operation': outcome != 'FAIL',  # Safe unless FAIL
            'requires_immediate_action': outcome == 'FAIL',
            'requires_repairs': outcome in ['FAIL', 'PASS_WITH_REPAIRS'],
        }

        return {
            'outcome': outcome,
            'summary': summary,
        }

    @classmethod
    def _determine_outcome(
        cls,
        defect_counts: Dict[str, int],
        blocking_failures: List[str]
    ) -> str:
        """
        Determine outcome based on defects and blocking failures.

        Returns:
            'PASS' | 'PASS_WITH_REPAIRS' | 'FAIL'
        """
        # FAIL if any critical defects or blocking failures
        if defect_counts['CRITICAL'] > 0 or len(blocking_failures) > 0:
            return 'FAIL'

        # PASS_WITH_REPAIRS if any major defects
        if defect_counts['MAJOR'] > 0:
            return 'PASS_WITH_REPAIRS'

        # PASS otherwise (only minor/advisory or no defects)
        return 'PASS'

    @classmethod
    def _check_blocking_failures(
        cls,
        inspection_run: InspectionRun
    ) -> List[str]:
        """
        Check for blocking failures in step data.

        A blocking failure occurs when:
        1. Step has blocking_fail: true in template
        2. Step has auto_defect_on rules that were triggered

        Returns:
            List of step_keys with blocking failures
        """
        blocking_failures = []
        template_snapshot = inspection_run.template_snapshot
        step_data = inspection_run.step_data

        # Get procedure steps from template
        procedure = template_snapshot.get('procedure', {})
        steps = procedure.get('steps', [])

        for step in steps:
            step_key = step.get('step_key')
            blocking_fail = step.get('blocking_fail', False)

            if not blocking_fail:
                continue

            # Check if this step has auto_defect_on rules that were triggered
            auto_defect_rules = step.get('auto_defect_on', [])
            if not auto_defect_rules:
                continue

            # Get step values
            step_values = step_data.get(step_key, {})

            # Check if any auto_defect_on rule is triggered
            for rule in auto_defect_rules:
                when_condition = rule.get('when', {})
                if cls._evaluate_condition(when_condition, step_values):
                    blocking_failures.append(step_key)
                    break  # One triggered rule is enough

        return blocking_failures

    @classmethod
    def _evaluate_condition(
        cls,
        condition: Dict[str, Any],
        step_values: Dict[str, Any]
    ) -> bool:
        """
        Evaluate a 'when' condition.

        Supports:
        - path + equals: {"path": "field_id", "equals": true}
        - any_field_in: {"any_field_in": ["VALUE1", "VALUE2"]}

        Returns:
            True if condition is met
        """
        # Check path + equals condition
        if 'path' in condition and 'equals' in condition:
            field_id = condition['path']
            expected_value = condition['equals']
            actual_value = step_values.get(field_id)
            return actual_value == expected_value

        # Check any_field_in condition
        if 'any_field_in' in condition:
            trigger_values = condition['any_field_in']
            # Check if any field value matches any trigger value
            for value in step_values.values():
                if value in trigger_values:
                    return True
            return False

        # Unknown condition type
        return False

    @classmethod
    def get_outcome_display(cls, outcome: str) -> str:
        """
        Get human-readable display text for outcome.

        Args:
            outcome: 'PASS' | 'PASS_WITH_REPAIRS' | 'FAIL'

        Returns:
            Display string
        """
        displays = {
            'PASS': 'PASS - Equipment safe for operation',
            'PASS_WITH_REPAIRS': 'PASS - Repairs required before next inspection',
            'FAIL': 'FAIL - Equipment unsafe, tagged out of service',
        }
        return displays.get(outcome, outcome)
