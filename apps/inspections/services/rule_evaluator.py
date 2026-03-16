"""
Rule Evaluation Service

Evaluates inspection rules against collected step data to determine if defects should be generated.
Supports 14 assertion types and complex when-conditions.
"""

from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal


class RuleEvaluationResult:
    """Result of evaluating a single rule."""
    def __init__(
        self,
        rule_id: str,
        passed: bool,
        step_key: str,
        actual_value: Any = None,
        expected_value: Any = None,
        assertion_type: str = None,
        error: Optional[str] = None
    ):
        self.rule_id = rule_id
        self.passed = passed
        self.step_key = step_key
        self.actual_value = actual_value
        self.expected_value = expected_value
        self.assertion_type = assertion_type
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'rule_id': self.rule_id,
            'passed': self.passed,
            'step_key': self.step_key,
            'actual_value': self.actual_value,
            'expected_value': self.expected_value,
            'assertion_type': self.assertion_type,
            'error': self.error
        }


class RuleEvaluator:
    """
    Service for evaluating inspection rules against step data.

    Supported assertion types:
    - NUMERIC_EQUALS, NUMERIC_GT, NUMERIC_LT, NUMERIC_GTE, NUMERIC_LTE, NUMERIC_IN_RANGE
    - STRING_EQUALS, STRING_CONTAINS
    - BOOLEAN_TRUE, BOOLEAN_FALSE
    - ENUM_EQUALS, ENUM_IN
    - EXISTS, NOT_EXISTS
    """

    NUMERIC_ASSERTIONS = [
        'NUMERIC_EQUALS',
        'NUMERIC_GT',
        'NUMERIC_LT',
        'NUMERIC_GTE',
        'NUMERIC_LTE',
        'NUMERIC_IN_RANGE'
    ]

    STRING_ASSERTIONS = [
        'STRING_EQUALS',
        'STRING_CONTAINS'
    ]

    BOOLEAN_ASSERTIONS = [
        'BOOLEAN_TRUE',
        'BOOLEAN_FALSE'
    ]

    ENUM_ASSERTIONS = [
        'ENUM_EQUALS',
        'ENUM_IN'
    ]

    EXISTENCE_ASSERTIONS = [
        'EXISTS',
        'NOT_EXISTS'
    ]

    @classmethod
    def evaluate_all_rules(
        cls,
        template: Dict[str, Any],
        step_data: Dict[str, Any]
    ) -> List[RuleEvaluationResult]:
        """
        Evaluate all rules in template against step data.

        Args:
            template: Full inspection template dict
            step_data: Collected step data from inspection

        Returns:
            List of RuleEvaluationResult objects
        """
        rules = template.get('rules', [])
        if not rules:
            return []

        results = []
        for rule in rules:
            result = cls.evaluate_rule(rule, step_data, template)
            if result:
                results.append(result)

        return results

    @classmethod
    def evaluate_rule(
        cls,
        rule: Dict[str, Any],
        step_data: Dict[str, Any],
        template: Dict[str, Any]
    ) -> Optional[RuleEvaluationResult]:
        """
        Evaluate a single rule.

        Args:
            rule: Rule definition from template
            step_data: Collected step data
            template: Full template for context

        Returns:
            RuleEvaluationResult or None if when-condition not met
        """
        rule_id = rule.get('rule_id')
        when = rule.get('when')
        assertion = rule.get('assert')

        # Check when condition
        if not cls.check_when_condition(when, step_data):
            return None  # Rule doesn't apply

        # Get step key from when condition
        step_key = when.get('step_key') if when else None
        if not step_key:
            return RuleEvaluationResult(
                rule_id=rule_id,
                passed=False,
                step_key='unknown',
                error='Rule missing step_key in when condition'
            )

        # Evaluate assertion
        try:
            passed, actual_value, expected_value = cls.evaluate_assertion(
                assertion,
                step_data,
                step_key
            )

            return RuleEvaluationResult(
                rule_id=rule_id,
                passed=passed,
                step_key=step_key,
                actual_value=actual_value,
                expected_value=expected_value,
                assertion_type=assertion.get('type') if assertion else None
            )

        except Exception as e:
            return RuleEvaluationResult(
                rule_id=rule_id,
                passed=False,
                step_key=step_key,
                error=str(e)
            )

    @classmethod
    def check_when_condition(
        cls,
        when: Optional[Dict[str, Any]],
        step_data: Dict[str, Any]
    ) -> bool:
        """
        Check if when-condition is satisfied.

        Args:
            when: When condition from rule
            step_data: Collected step data

        Returns:
            True if condition met, False otherwise
        """
        if not when:
            return True  # No condition means always evaluate

        # Check step_key condition
        step_key = when.get('step_key')
        if step_key and step_key not in step_data:
            return False  # Step not completed

        # Only step existence checking is implemented
        return True

    @classmethod
    def evaluate_assertion(
        cls,
        assertion: Dict[str, Any],
        step_data: Dict[str, Any],
        step_key: str
    ) -> Tuple[bool, Any, Any]:
        """
        Evaluate an assertion.

        Args:
            assertion: Assertion definition
            step_data: Collected step data
            step_key: Current step key

        Returns:
            Tuple of (passed, actual_value, expected_value)
        """
        if not assertion:
            return (True, None, None)

        assertion_type = assertion.get('type')

        # Resolve left operand (actual value from step data)
        left_path = assertion.get('left', {}).get('path')
        actual_value = cls.resolve_path(left_path, step_data, step_key) if left_path else None

        # Resolve right operand (expected value)
        expected_value = assertion.get('right')

        # Evaluate based on assertion type
        if assertion_type in cls.NUMERIC_ASSERTIONS:
            return cls._evaluate_numeric_assertion(assertion_type, actual_value, expected_value)
        elif assertion_type in cls.STRING_ASSERTIONS:
            return cls._evaluate_string_assertion(assertion_type, actual_value, expected_value)
        elif assertion_type in cls.BOOLEAN_ASSERTIONS:
            return cls._evaluate_boolean_assertion(assertion_type, actual_value)
        elif assertion_type in cls.ENUM_ASSERTIONS:
            return cls._evaluate_enum_assertion(assertion_type, actual_value, expected_value)
        elif assertion_type in cls.EXISTENCE_ASSERTIONS:
            return cls._evaluate_existence_assertion(assertion_type, actual_value)
        else:
            raise ValueError(f"Unsupported assertion type: {assertion_type}")

    @classmethod
    def resolve_path(
        cls,
        path: str,
        step_data: Dict[str, Any],
        step_key: str
    ) -> Any:
        """
        Resolve a path to a value in step data.

        Supports:
        - Simple field names: 'cleanliness'
        - Nested paths: 'measurements.test_duration_seconds'
        - Array indices: 'items[0].name'

        Args:
            path: Path to resolve (dot notation or JSONPath-style)
            step_data: Step data dictionary
            step_key: Current step key

        Returns:
            Resolved value or None if not found
        """
        if not path:
            return None

        # Get step's data
        current_step_data = step_data.get(step_key, {})

        # Split path by dots
        parts = path.split('.')
        current = current_step_data

        for part in parts:
            if current is None:
                return None

            # Handle array indices (e.g., 'items[0]')
            if '[' in part and ']' in part:
                field_name = part[:part.index('[')]
                index = int(part[part.index('[') + 1:part.index(']')])
                current = current.get(field_name, [])
                if isinstance(current, list) and 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                # Simple field access
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return None

        return current

    @classmethod
    def _evaluate_numeric_assertion(
        cls,
        assertion_type: str,
        actual: Any,
        expected: Any
    ) -> Tuple[bool, Any, Any]:
        """Evaluate numeric assertions."""
        # Convert actual to Decimal
        try:
            actual_num = Decimal(str(actual)) if actual is not None else None
        except (ValueError, TypeError):
            return (False, actual, expected)

        if actual_num is None:
            return (False, actual, expected)

        # Handle NUMERIC_IN_RANGE separately (expected is dict)
        if assertion_type == 'NUMERIC_IN_RANGE':
            if isinstance(expected, dict):
                try:
                    min_val = Decimal(str(expected.get('min')))
                    max_val = Decimal(str(expected.get('max')))
                    passed = min_val <= actual_num <= max_val
                except (ValueError, TypeError):
                    return (False, actual, expected)
            else:
                passed = False
            return (passed, actual, expected)

        # For other assertions, convert expected to Decimal
        try:
            expected_num = Decimal(str(expected)) if expected is not None else None
        except (ValueError, TypeError):
            return (False, actual, expected)

        if assertion_type == 'NUMERIC_EQUALS':
            passed = actual_num == expected_num
        elif assertion_type == 'NUMERIC_GT':
            passed = actual_num > expected_num
        elif assertion_type == 'NUMERIC_LT':
            passed = actual_num < expected_num
        elif assertion_type == 'NUMERIC_GTE':
            passed = actual_num >= expected_num
        elif assertion_type == 'NUMERIC_LTE':
            passed = actual_num <= expected_num
        else:
            passed = False

        return (passed, actual, expected)

    @classmethod
    def _evaluate_string_assertion(
        cls,
        assertion_type: str,
        actual: Any,
        expected: Any
    ) -> Tuple[bool, Any, Any]:
        """Evaluate string assertions."""
        if actual is None:
            return (False, actual, expected)

        actual_str = str(actual)
        expected_str = str(expected) if expected is not None else ''

        if assertion_type == 'STRING_EQUALS':
            passed = actual_str == expected_str
        elif assertion_type == 'STRING_CONTAINS':
            passed = expected_str in actual_str
        else:
            passed = False

        return (passed, actual, expected)

    @classmethod
    def _evaluate_boolean_assertion(
        cls,
        assertion_type: str,
        actual: Any
    ) -> Tuple[bool, Any, bool]:
        """Evaluate boolean assertions."""
        if assertion_type == 'BOOLEAN_TRUE':
            passed = actual is True
            expected = True
        elif assertion_type == 'BOOLEAN_FALSE':
            passed = actual is False
            expected = False
        else:
            passed = False
            expected = None

        return (passed, actual, expected)

    @classmethod
    def _evaluate_enum_assertion(
        cls,
        assertion_type: str,
        actual: Any,
        expected: Any
    ) -> Tuple[bool, Any, Any]:
        """Evaluate enum assertions."""
        if actual is None:
            return (False, actual, expected)

        if assertion_type == 'ENUM_EQUALS':
            passed = actual == expected
        elif assertion_type == 'ENUM_IN':
            # Expected should be a list
            if isinstance(expected, list):
                passed = actual in expected
            else:
                passed = False
        else:
            passed = False

        return (passed, actual, expected)

    @classmethod
    def _evaluate_existence_assertion(
        cls,
        assertion_type: str,
        actual: Any
    ) -> Tuple[bool, Any, None]:
        """Evaluate existence assertions."""
        if assertion_type == 'EXISTS':
            passed = actual is not None
        elif assertion_type == 'NOT_EXISTS':
            passed = actual is None
        else:
            passed = False

        return (passed, actual, None)
