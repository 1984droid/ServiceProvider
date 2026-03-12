"""
Tests for RuleEvaluator service

Covers all 14 assertion types and path resolution logic.
"""

from django.test import TestCase
from decimal import Decimal
from apps.inspections.services.rule_evaluator import RuleEvaluator, RuleEvaluationResult


class RuleEvaluatorPathResolutionTests(TestCase):
    """Test path resolution in step data."""

    def setUp(self):
        """Set up test data."""
        self.step_data = {
            'visual_inspection': {
                'cleanliness': 'GOOD',
                'measurements': {
                    'test_duration_seconds': 180,
                    'voltage': 24000
                },
                'items': [
                    {'name': 'Item 1', 'status': 'PASS'},
                    {'name': 'Item 2', 'status': 'FAIL'}
                ]
            }
        }

    def test_simple_field_path(self):
        """Test simple field path resolution."""
        result = RuleEvaluator.resolve_path(
            'cleanliness',
            self.step_data,
            'visual_inspection'
        )
        self.assertEqual(result, 'GOOD')

    def test_nested_field_path(self):
        """Test nested field path resolution."""
        result = RuleEvaluator.resolve_path(
            'measurements.test_duration_seconds',
            self.step_data,
            'visual_inspection'
        )
        self.assertEqual(result, 180)

    def test_array_index_path(self):
        """Test array index path resolution."""
        result = RuleEvaluator.resolve_path(
            'items[0].name',
            self.step_data,
            'visual_inspection'
        )
        self.assertEqual(result, 'Item 1')

    def test_array_second_index_path(self):
        """Test array second index path resolution."""
        result = RuleEvaluator.resolve_path(
            'items[1].status',
            self.step_data,
            'visual_inspection'
        )
        self.assertEqual(result, 'FAIL')

    def test_nonexistent_path(self):
        """Test nonexistent path returns None."""
        result = RuleEvaluator.resolve_path(
            'nonexistent.field',
            self.step_data,
            'visual_inspection'
        )
        self.assertIsNone(result)

    def test_invalid_array_index(self):
        """Test invalid array index returns None."""
        result = RuleEvaluator.resolve_path(
            'items[99].name',
            self.step_data,
            'visual_inspection'
        )
        self.assertIsNone(result)

    def test_missing_step_key(self):
        """Test missing step key returns None."""
        result = RuleEvaluator.resolve_path(
            'cleanliness',
            self.step_data,
            'nonexistent_step'
        )
        self.assertIsNone(result)


class NumericAssertionTests(TestCase):
    """Test numeric assertion types."""

    def test_numeric_equals_pass(self):
        """Test NUMERIC_EQUALS assertion passes."""
        passed, actual, expected = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_EQUALS',
            180,
            180
        )
        self.assertTrue(passed)
        self.assertEqual(actual, 180)
        self.assertEqual(expected, 180)

    def test_numeric_equals_fail(self):
        """Test NUMERIC_EQUALS assertion fails."""
        passed, actual, expected = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_EQUALS',
            175,
            180
        )
        self.assertFalse(passed)

    def test_numeric_gt_pass(self):
        """Test NUMERIC_GT assertion passes."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_GT',
            185,
            180
        )
        self.assertTrue(passed)

    def test_numeric_gt_fail(self):
        """Test NUMERIC_GT assertion fails."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_GT',
            175,
            180
        )
        self.assertFalse(passed)

    def test_numeric_lt_pass(self):
        """Test NUMERIC_LT assertion passes."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_LT',
            175,
            180
        )
        self.assertTrue(passed)

    def test_numeric_lt_fail(self):
        """Test NUMERIC_LT assertion fails."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_LT',
            185,
            180
        )
        self.assertFalse(passed)

    def test_numeric_gte_pass_greater(self):
        """Test NUMERIC_GTE assertion passes with greater value."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_GTE',
            185,
            180
        )
        self.assertTrue(passed)

    def test_numeric_gte_pass_equal(self):
        """Test NUMERIC_GTE assertion passes with equal value."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_GTE',
            180,
            180
        )
        self.assertTrue(passed)

    def test_numeric_gte_fail(self):
        """Test NUMERIC_GTE assertion fails."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_GTE',
            175,
            180
        )
        self.assertFalse(passed)

    def test_numeric_lte_pass_less(self):
        """Test NUMERIC_LTE assertion passes with less value."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_LTE',
            175,
            180
        )
        self.assertTrue(passed)

    def test_numeric_lte_pass_equal(self):
        """Test NUMERIC_LTE assertion passes with equal value."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_LTE',
            180,
            180
        )
        self.assertTrue(passed)

    def test_numeric_lte_fail(self):
        """Test NUMERIC_LTE assertion fails."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_LTE',
            185,
            180
        )
        self.assertFalse(passed)

    def test_numeric_in_range_pass(self):
        """Test NUMERIC_IN_RANGE assertion passes."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_IN_RANGE',
            180,
            {'min': 175, 'max': 185}
        )
        self.assertTrue(passed)

    def test_numeric_in_range_pass_boundary_min(self):
        """Test NUMERIC_IN_RANGE assertion passes at min boundary."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_IN_RANGE',
            175,
            {'min': 175, 'max': 185}
        )
        self.assertTrue(passed)

    def test_numeric_in_range_pass_boundary_max(self):
        """Test NUMERIC_IN_RANGE assertion passes at max boundary."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_IN_RANGE',
            185,
            {'min': 175, 'max': 185}
        )
        self.assertTrue(passed)

    def test_numeric_in_range_fail_below(self):
        """Test NUMERIC_IN_RANGE assertion fails below range."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_IN_RANGE',
            170,
            {'min': 175, 'max': 185}
        )
        self.assertFalse(passed)

    def test_numeric_in_range_fail_above(self):
        """Test NUMERIC_IN_RANGE assertion fails above range."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_IN_RANGE',
            190,
            {'min': 175, 'max': 185}
        )
        self.assertFalse(passed)

    def test_numeric_with_decimal_values(self):
        """Test numeric assertions work with Decimal values."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_EQUALS',
            Decimal('180.5'),
            Decimal('180.5')
        )
        self.assertTrue(passed)

    def test_numeric_with_none_value(self):
        """Test numeric assertion fails with None value."""
        passed, _, _ = RuleEvaluator._evaluate_numeric_assertion(
            'NUMERIC_EQUALS',
            None,
            180
        )
        self.assertFalse(passed)


class StringAssertionTests(TestCase):
    """Test string assertion types."""

    def test_string_equals_pass(self):
        """Test STRING_EQUALS assertion passes."""
        passed, _, _ = RuleEvaluator._evaluate_string_assertion(
            'STRING_EQUALS',
            'GOOD',
            'GOOD'
        )
        self.assertTrue(passed)

    def test_string_equals_fail(self):
        """Test STRING_EQUALS assertion fails."""
        passed, _, _ = RuleEvaluator._evaluate_string_assertion(
            'STRING_EQUALS',
            'POOR',
            'GOOD'
        )
        self.assertFalse(passed)

    def test_string_equals_case_sensitive(self):
        """Test STRING_EQUALS is case sensitive."""
        passed, _, _ = RuleEvaluator._evaluate_string_assertion(
            'STRING_EQUALS',
            'good',
            'GOOD'
        )
        self.assertFalse(passed)

    def test_string_contains_pass(self):
        """Test STRING_CONTAINS assertion passes."""
        passed, _, _ = RuleEvaluator._evaluate_string_assertion(
            'STRING_CONTAINS',
            'This is a GOOD result',
            'GOOD'
        )
        self.assertTrue(passed)

    def test_string_contains_fail(self):
        """Test STRING_CONTAINS assertion fails."""
        passed, _, _ = RuleEvaluator._evaluate_string_assertion(
            'STRING_CONTAINS',
            'This is a POOR result',
            'GOOD'
        )
        self.assertFalse(passed)

    def test_string_with_none_value(self):
        """Test string assertion fails with None value."""
        passed, _, _ = RuleEvaluator._evaluate_string_assertion(
            'STRING_EQUALS',
            None,
            'GOOD'
        )
        self.assertFalse(passed)


class BooleanAssertionTests(TestCase):
    """Test boolean assertion types."""

    def test_boolean_true_pass(self):
        """Test BOOLEAN_TRUE assertion passes."""
        passed, _, _ = RuleEvaluator._evaluate_boolean_assertion(
            'BOOLEAN_TRUE',
            True
        )
        self.assertTrue(passed)

    def test_boolean_true_fail(self):
        """Test BOOLEAN_TRUE assertion fails."""
        passed, _, _ = RuleEvaluator._evaluate_boolean_assertion(
            'BOOLEAN_TRUE',
            False
        )
        self.assertFalse(passed)

    def test_boolean_false_pass(self):
        """Test BOOLEAN_FALSE assertion passes."""
        passed, _, _ = RuleEvaluator._evaluate_boolean_assertion(
            'BOOLEAN_FALSE',
            False
        )
        self.assertTrue(passed)

    def test_boolean_false_fail(self):
        """Test BOOLEAN_FALSE assertion fails."""
        passed, _, _ = RuleEvaluator._evaluate_boolean_assertion(
            'BOOLEAN_FALSE',
            True
        )
        self.assertFalse(passed)

    def test_boolean_with_truthy_value(self):
        """Test boolean assertions require exact bool values."""
        passed, _, _ = RuleEvaluator._evaluate_boolean_assertion(
            'BOOLEAN_TRUE',
            1  # Truthy but not True
        )
        self.assertFalse(passed)


class EnumAssertionTests(TestCase):
    """Test enum assertion types."""

    def test_enum_equals_pass(self):
        """Test ENUM_EQUALS assertion passes."""
        passed, _, _ = RuleEvaluator._evaluate_enum_assertion(
            'ENUM_EQUALS',
            'GOOD',
            'GOOD'
        )
        self.assertTrue(passed)

    def test_enum_equals_fail(self):
        """Test ENUM_EQUALS assertion fails."""
        passed, _, _ = RuleEvaluator._evaluate_enum_assertion(
            'ENUM_EQUALS',
            'POOR',
            'GOOD'
        )
        self.assertFalse(passed)

    def test_enum_in_pass(self):
        """Test ENUM_IN assertion passes."""
        passed, _, _ = RuleEvaluator._evaluate_enum_assertion(
            'ENUM_IN',
            'GOOD',
            ['EXCELLENT', 'GOOD', 'FAIR']
        )
        self.assertTrue(passed)

    def test_enum_in_fail(self):
        """Test ENUM_IN assertion fails."""
        passed, _, _ = RuleEvaluator._evaluate_enum_assertion(
            'ENUM_IN',
            'POOR',
            ['EXCELLENT', 'GOOD', 'FAIR']
        )
        self.assertFalse(passed)

    def test_enum_in_with_non_list(self):
        """Test ENUM_IN fails with non-list expected value."""
        passed, _, _ = RuleEvaluator._evaluate_enum_assertion(
            'ENUM_IN',
            'GOOD',
            'GOOD'  # Not a list
        )
        self.assertFalse(passed)

    def test_enum_with_none_value(self):
        """Test enum assertion fails with None value."""
        passed, _, _ = RuleEvaluator._evaluate_enum_assertion(
            'ENUM_EQUALS',
            None,
            'GOOD'
        )
        self.assertFalse(passed)


class ExistenceAssertionTests(TestCase):
    """Test existence assertion types."""

    def test_exists_pass_with_value(self):
        """Test EXISTS assertion passes with value."""
        passed, _, _ = RuleEvaluator._evaluate_existence_assertion(
            'EXISTS',
            'some value'
        )
        self.assertTrue(passed)

    def test_exists_pass_with_zero(self):
        """Test EXISTS assertion passes with zero."""
        passed, _, _ = RuleEvaluator._evaluate_existence_assertion(
            'EXISTS',
            0
        )
        self.assertTrue(passed)

    def test_exists_pass_with_empty_string(self):
        """Test EXISTS assertion passes with empty string."""
        passed, _, _ = RuleEvaluator._evaluate_existence_assertion(
            'EXISTS',
            ''
        )
        self.assertTrue(passed)

    def test_exists_fail_with_none(self):
        """Test EXISTS assertion fails with None."""
        passed, _, _ = RuleEvaluator._evaluate_existence_assertion(
            'EXISTS',
            None
        )
        self.assertFalse(passed)

    def test_not_exists_pass_with_none(self):
        """Test NOT_EXISTS assertion passes with None."""
        passed, _, _ = RuleEvaluator._evaluate_existence_assertion(
            'NOT_EXISTS',
            None
        )
        self.assertTrue(passed)

    def test_not_exists_fail_with_value(self):
        """Test NOT_EXISTS assertion fails with value."""
        passed, _, _ = RuleEvaluator._evaluate_existence_assertion(
            'NOT_EXISTS',
            'some value'
        )
        self.assertFalse(passed)


class WhenConditionTests(TestCase):
    """Test when-condition checking."""

    def test_no_when_condition_always_true(self):
        """Test no when-condition always returns True."""
        result = RuleEvaluator.check_when_condition(None, {})
        self.assertTrue(result)

    def test_when_condition_step_exists(self):
        """Test when-condition passes if step exists."""
        when = {'step_key': 'visual_inspection'}
        step_data = {'visual_inspection': {'cleanliness': 'GOOD'}}

        result = RuleEvaluator.check_when_condition(when, step_data)
        self.assertTrue(result)

    def test_when_condition_step_missing(self):
        """Test when-condition fails if step missing."""
        when = {'step_key': 'visual_inspection'}
        step_data = {}

        result = RuleEvaluator.check_when_condition(when, step_data)
        self.assertFalse(result)


class RuleEvaluationIntegrationTests(TestCase):
    """Test complete rule evaluation flow."""

    def test_evaluate_rule_passed(self):
        """Test evaluating a rule that passes."""
        rule = {
            'rule_id': 'test_rule_1',
            'when': {'step_key': 'visual_inspection'},
            'assert': {
                'type': 'NUMERIC_EQUALS',
                'left': {'path': 'test_duration'},
                'right': 180
            }
        }

        step_data = {
            'visual_inspection': {
                'test_duration': 180
            }
        }

        template = {}

        result = RuleEvaluator.evaluate_rule(rule, step_data, template)

        self.assertIsNotNone(result)
        self.assertTrue(result.passed)
        self.assertEqual(result.rule_id, 'test_rule_1')
        self.assertEqual(result.step_key, 'visual_inspection')

    def test_evaluate_rule_failed(self):
        """Test evaluating a rule that fails."""
        rule = {
            'rule_id': 'test_rule_2',
            'when': {'step_key': 'visual_inspection'},
            'assert': {
                'type': 'NUMERIC_EQUALS',
                'left': {'path': 'test_duration'},
                'right': 180
            }
        }

        step_data = {
            'visual_inspection': {
                'test_duration': 175
            }
        }

        template = {}

        result = RuleEvaluator.evaluate_rule(rule, step_data, template)

        self.assertIsNotNone(result)
        self.assertFalse(result.passed)
        self.assertEqual(result.actual_value, 175)
        self.assertEqual(result.expected_value, 180)

    def test_evaluate_rule_when_condition_not_met(self):
        """Test evaluating a rule with when-condition not met."""
        rule = {
            'rule_id': 'test_rule_3',
            'when': {'step_key': 'visual_inspection'},
            'assert': {
                'type': 'NUMERIC_EQUALS',
                'left': {'path': 'test_duration'},
                'right': 180
            }
        }

        step_data = {}  # Step not completed
        template = {}

        result = RuleEvaluator.evaluate_rule(rule, step_data, template)

        self.assertIsNone(result)  # Rule doesn't apply

    def test_evaluate_all_rules(self):
        """Test evaluating multiple rules."""
        template = {
            'rules': [
                {
                    'rule_id': 'rule_1',
                    'when': {'step_key': 'step_1'},
                    'assert': {
                        'type': 'NUMERIC_EQUALS',
                        'left': {'path': 'value'},
                        'right': 100
                    }
                },
                {
                    'rule_id': 'rule_2',
                    'when': {'step_key': 'step_2'},
                    'assert': {
                        'type': 'STRING_EQUALS',
                        'left': {'path': 'status'},
                        'right': 'PASS'
                    }
                }
            ]
        }

        step_data = {
            'step_1': {'value': 100},
            'step_2': {'status': 'FAIL'}
        }

        results = RuleEvaluator.evaluate_all_rules(template, step_data)

        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].passed)  # rule_1 passes
        self.assertFalse(results[1].passed)  # rule_2 fails
