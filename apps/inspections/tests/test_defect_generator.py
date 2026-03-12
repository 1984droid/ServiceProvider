"""
Tests for DefectGenerator service

Tests defect creation, idempotency, and severity mapping.
"""

from django.test import TestCase
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.inspections.services.defect_generator import DefectGenerator
from apps.inspections.services.rule_evaluator import RuleEvaluationResult
from apps.customers.models import Customer
from apps.assets.models import Vehicle
from django.utils import timezone


class DefectGeneratorSetupMixin:
    """Mixin for setting up test data."""

    def setUp(self):
        """Create test data."""
        # Create customer
        self.customer = Customer.objects.create(
            name='Test Customer',
            legal_name='Test Customer LLC',
            is_active=True
        )

        # Create vehicle
        self.vehicle = Vehicle.objects.create(
            customer=self.customer,
            vin='1HGBH41JXMN109186',
            year=2021,
            make='Ford',
            model='F-150'
        )

        # Create inspection template
        self.template = {
            'template': {
                'template_key': 'test_template',
                'version': '1.0.0'
            },
            'procedure': {
                'steps': [
                    {
                        'step_key': 'visual_inspection',
                        'title': 'Visual Inspection',
                        'required': True,
                        'fields': [
                            {
                                'field_id': 'cleanliness',
                                'label': 'Cleanliness',
                                'field_type': 'ENUM',
                                'required': True
                            }
                        ]
                    }
                ]
            },
            'rules': [
                {
                    'rule_id': 'cleanliness_check',
                    'title': 'Cleanliness must be GOOD or EXCELLENT',
                    'when': {'step_key': 'visual_inspection'},
                    'assert': {
                        'type': 'ENUM_IN',
                        'left': {'path': 'cleanliness'},
                        'right': ['GOOD', 'EXCELLENT']
                    },
                    'on_fail': {
                        'severity': 'UNSAFE_OUT_OF_SERVICE',
                        'defect_title': 'Poor cleanliness detected',
                        'defect_description': 'Equipment cleanliness is below acceptable standards'
                    }
                }
            ]
        }

        # Create inspection run
        self.inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_template',
            status='DRAFT',
            started_at=timezone.now(),
            template_snapshot=self.template,
            step_data={}
        )


class SeverityMappingTests(DefectGeneratorSetupMixin, TestCase):
    """Test severity mapping from template to model."""

    def test_severity_map_unsafe_out_of_service(self):
        """Test UNSAFE_OUT_OF_SERVICE maps to CRITICAL."""
        severity = DefectGenerator.map_severity('UNSAFE_OUT_OF_SERVICE')
        self.assertEqual(severity, 'CRITICAL')

    def test_severity_map_degraded_performance(self):
        """Test DEGRADED_PERFORMANCE maps to MAJOR."""
        severity = DefectGenerator.map_severity('DEGRADED_PERFORMANCE')
        self.assertEqual(severity, 'MAJOR')

    def test_severity_map_minor_issue(self):
        """Test MINOR_ISSUE maps to MINOR."""
        severity = DefectGenerator.map_severity('MINOR_ISSUE')
        self.assertEqual(severity, 'MINOR')

    def test_severity_map_advisory_notice(self):
        """Test ADVISORY_NOTICE maps to ADVISORY."""
        severity = DefectGenerator.map_severity('ADVISORY_NOTICE')
        self.assertEqual(severity, 'ADVISORY')

    def test_severity_map_direct_critical(self):
        """Test CRITICAL maps to CRITICAL."""
        severity = DefectGenerator.map_severity('CRITICAL')
        self.assertEqual(severity, 'CRITICAL')

    def test_severity_map_direct_major(self):
        """Test MAJOR maps to MAJOR."""
        severity = DefectGenerator.map_severity('MAJOR')
        self.assertEqual(severity, 'MAJOR')

    def test_severity_map_direct_minor(self):
        """Test MINOR maps to MINOR."""
        severity = DefectGenerator.map_severity('MINOR')
        self.assertEqual(severity, 'MINOR')

    def test_severity_map_direct_advisory(self):
        """Test ADVISORY maps to ADVISORY."""
        severity = DefectGenerator.map_severity('ADVISORY')
        self.assertEqual(severity, 'ADVISORY')

    def test_severity_map_unknown_defaults_to_minor(self):
        """Test unknown severity defaults to MINOR."""
        severity = DefectGenerator.map_severity('UNKNOWN_SEVERITY')
        self.assertEqual(severity, 'MINOR')


class DefectCreationTests(DefectGeneratorSetupMixin, TestCase):
    """Test defect creation from rules."""

    def test_create_defect_from_rule(self):
        """Test creating defect from failed rule."""
        rule = self.template['rules'][0]

        evaluation_result = RuleEvaluationResult(
            rule_id='cleanliness_check',
            passed=False,
            step_key='visual_inspection',
            actual_value='POOR',
            expected_value=['GOOD', 'EXCELLENT'],
            assertion_type='ENUM_IN'
        )

        defect = DefectGenerator.create_defect_from_rule(
            inspection_run=self.inspection,
            rule=rule,
            evaluation_result=evaluation_result
        )

        self.assertIsNotNone(defect)
        self.assertEqual(defect.inspection_run, self.inspection)
        self.assertEqual(defect.severity, 'CRITICAL')
        self.assertEqual(defect.title, 'Poor cleanliness detected')
        self.assertEqual(defect.step_key, 'visual_inspection')
        self.assertEqual(defect.rule_id, 'cleanliness_check')
        self.assertEqual(defect.status, 'OPEN')

    def test_defect_identity_generated(self):
        """Test defect_identity is generated correctly."""
        rule = self.template['rules'][0]

        evaluation_result = RuleEvaluationResult(
            rule_id='cleanliness_check',
            passed=False,
            step_key='visual_inspection',
            actual_value='POOR',
            expected_value=['GOOD', 'EXCELLENT']
        )

        defect = DefectGenerator.create_defect_from_rule(
            inspection_run=self.inspection,
            rule=rule,
            evaluation_result=evaluation_result
        )

        # Verify defect_identity is 64-char SHA256 hash
        self.assertEqual(len(defect.defect_identity), 64)

        # Verify it can be regenerated
        expected_identity = InspectionDefect.generate_defect_identity(
            self.inspection.id,
            '',
            'visual_inspection',
            'cleanliness_check'
        )
        self.assertEqual(defect.defect_identity, expected_identity)

    def test_evaluation_trace_stored(self):
        """Test evaluation trace is stored in defect."""
        rule = self.template['rules'][0]

        evaluation_result = RuleEvaluationResult(
            rule_id='cleanliness_check',
            passed=False,
            step_key='visual_inspection',
            actual_value='POOR',
            expected_value=['GOOD', 'EXCELLENT'],
            assertion_type='ENUM_IN'
        )

        defect = DefectGenerator.create_defect_from_rule(
            inspection_run=self.inspection,
            rule=rule,
            evaluation_result=evaluation_result
        )

        self.assertIsNotNone(defect.evaluation_trace)
        self.assertEqual(defect.evaluation_trace['rule_id'], 'cleanliness_check')
        self.assertEqual(defect.evaluation_trace['step_key'], 'visual_inspection')
        self.assertFalse(defect.evaluation_trace['passed'])
        self.assertEqual(defect.evaluation_trace['actual_value'], 'POOR')


class DefectIdempotencyTests(DefectGeneratorSetupMixin, TestCase):
    """Test defect idempotency - re-running rules doesn't create duplicates."""

    def test_create_defect_twice_same_identity(self):
        """Test creating same defect twice uses same identity."""
        rule = self.template['rules'][0]

        evaluation_result = RuleEvaluationResult(
            rule_id='cleanliness_check',
            passed=False,
            step_key='visual_inspection',
            actual_value='POOR',
            expected_value=['GOOD', 'EXCELLENT']
        )

        # Create defect first time
        defect1 = DefectGenerator.create_defect_from_rule(
            inspection_run=self.inspection,
            rule=rule,
            evaluation_result=evaluation_result
        )

        # Create defect second time
        defect2 = DefectGenerator.create_defect_from_rule(
            inspection_run=self.inspection,
            rule=rule,
            evaluation_result=evaluation_result
        )

        # Should be same defect (same ID)
        self.assertEqual(defect1.id, defect2.id)
        self.assertEqual(defect1.defect_identity, defect2.defect_identity)

        # Should only be one defect in database
        defect_count = InspectionDefect.objects.filter(
            inspection_run=self.inspection
        ).count()
        self.assertEqual(defect_count, 1)

    def test_re_evaluate_updates_existing_defect(self):
        """Test re-evaluating rules updates existing defect."""
        rule = self.template['rules'][0]

        # First evaluation
        evaluation_result1 = RuleEvaluationResult(
            rule_id='cleanliness_check',
            passed=False,
            step_key='visual_inspection',
            actual_value='POOR',
            expected_value=['GOOD', 'EXCELLENT']
        )

        defect1 = DefectGenerator.create_defect_from_rule(
            inspection_run=self.inspection,
            rule=rule,
            evaluation_result=evaluation_result1
        )

        original_created_at = defect1.created_at

        # Second evaluation with different actual value
        evaluation_result2 = RuleEvaluationResult(
            rule_id='cleanliness_check',
            passed=False,
            step_key='visual_inspection',
            actual_value='FAIR',
            expected_value=['GOOD', 'EXCELLENT']
        )

        defect2 = DefectGenerator.create_defect_from_rule(
            inspection_run=self.inspection,
            rule=rule,
            evaluation_result=evaluation_result2
        )

        # Same defect
        self.assertEqual(defect1.id, defect2.id)

        # But evaluation trace updated
        defect2.refresh_from_db()
        self.assertEqual(defect2.evaluation_trace['actual_value'], 'FAIR')

        # created_at unchanged (it's the same defect)
        self.assertEqual(defect2.created_at, original_created_at)


class GenerateDefectsForInspectionTests(DefectGeneratorSetupMixin, TestCase):
    """Test generating defects for entire inspection."""

    def test_generate_defects_for_inspection_no_failures(self):
        """Test generating defects when all rules pass."""
        # Set step data that passes the rule
        self.inspection.step_data = {
            'visual_inspection': {
                'cleanliness': 'GOOD'
            }
        }
        self.inspection.save()

        defects = DefectGenerator.generate_defects_for_inspection(self.inspection)

        self.assertEqual(len(defects), 0)

    def test_generate_defects_for_inspection_with_failures(self):
        """Test generating defects when rules fail."""
        # Set step data that fails the rule
        self.inspection.step_data = {
            'visual_inspection': {
                'cleanliness': 'POOR'
            }
        }
        self.inspection.save()

        defects = DefectGenerator.generate_defects_for_inspection(self.inspection)

        self.assertEqual(len(defects), 1)
        self.assertEqual(defects[0].severity, 'CRITICAL')
        self.assertEqual(defects[0].title, 'Poor cleanliness detected')

    def test_generate_defects_with_multiple_rules(self):
        """Test generating defects with multiple failing rules."""
        # Add second rule
        self.template['rules'].append({
            'rule_id': 'duration_check',
            'title': 'Duration must be 180 seconds',
            'when': {'step_key': 'visual_inspection'},
            'assert': {
                'type': 'NUMERIC_EQUALS',
                'left': {'path': 'duration'},
                'right': 180
            },
            'on_fail': {
                'severity': 'MAJOR',
                'defect_title': 'Incorrect test duration',
                'defect_description': 'Test duration was not 180 seconds'
            }
        })

        self.inspection.template_snapshot = self.template

        # Set step data that fails both rules
        self.inspection.step_data = {
            'visual_inspection': {
                'cleanliness': 'POOR',
                'duration': 175
            }
        }
        self.inspection.save()

        defects = DefectGenerator.generate_defects_for_inspection(self.inspection)

        self.assertEqual(len(defects), 2)

        # Check both defects created
        defect_titles = {d.title for d in defects}
        self.assertIn('Poor cleanliness detected', defect_titles)
        self.assertIn('Incorrect test duration', defect_titles)


class DefectSummaryTests(DefectGeneratorSetupMixin, TestCase):
    """Test defect summary generation."""

    def test_get_defect_summary_no_defects(self):
        """Test defect summary with no defects."""
        summary = DefectGenerator.get_defect_summary(self.inspection)

        self.assertEqual(summary['total_defects'], 0)
        self.assertEqual(summary['by_severity']['CRITICAL'], 0)
        self.assertEqual(summary['by_status']['OPEN'], 0)

    def test_get_defect_summary_with_defects(self):
        """Test defect summary with defects."""
        # Create defects
        defect1_identity = InspectionDefect.generate_defect_identity(
            self.inspection.id, '', 'step_1', 'rule_1'
        )
        defect2_identity = InspectionDefect.generate_defect_identity(
            self.inspection.id, '', 'step_2', 'rule_2'
        )
        defect3_identity = InspectionDefect.generate_defect_identity(
            self.inspection.id, '', 'step_3', 'rule_3'
        )

        InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=defect1_identity,
            module_key='',
            step_key='step_1',
            rule_id='rule_1',
            severity='CRITICAL',
            title='Critical defect',
            description='Test',
            status='OPEN'
        )

        InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=defect2_identity,
            module_key='',
            step_key='step_2',
            rule_id='rule_2',
            severity='MAJOR',
            title='Major defect',
            description='Test',
            status='OPEN'
        )

        InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=defect3_identity,
            module_key='',
            step_key='step_3',
            rule_id='rule_3',
            severity='MINOR',
            title='Minor defect',
            description='Test',
            status='RESOLVED'
        )

        summary = DefectGenerator.get_defect_summary(self.inspection)

        self.assertEqual(summary['total_defects'], 3)
        self.assertEqual(summary['by_severity']['CRITICAL'], 1)
        self.assertEqual(summary['by_severity']['MAJOR'], 1)
        self.assertEqual(summary['by_severity']['MINOR'], 1)
        self.assertEqual(summary['by_status']['OPEN'], 2)
        self.assertEqual(summary['by_status']['RESOLVED'], 1)
