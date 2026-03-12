"""
Tests for InspectionRuntime integration with rule evaluation

Tests finalize_with_rules and evaluate_rules methods.
"""

from django.test import TestCase
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.inspections.services.runtime_service import InspectionRuntime
from apps.customers.models import Customer
from apps.assets.models import Vehicle
from django.utils import timezone


class RuntimeRuleEvaluationTests(TestCase):
    """Test runtime service rule evaluation integration."""

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

        # Create inspection template with rules
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
                            },
                            {
                                'field_id': 'test_duration',
                                'label': 'Test Duration',
                                'field_type': 'NUMBER',
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
                        'severity': 'CRITICAL',
                        'defect_title': 'Poor cleanliness',
                        'defect_description': 'Cleanliness below standards'
                    }
                },
                {
                    'rule_id': 'duration_check',
                    'title': 'Duration must be 180 seconds',
                    'when': {'step_key': 'visual_inspection'},
                    'assert': {
                        'type': 'NUMERIC_EQUALS',
                        'left': {'path': 'test_duration'},
                        'right': 180
                    },
                    'on_fail': {
                        'severity': 'MAJOR',
                        'defect_title': 'Incorrect duration',
                        'defect_description': 'Test duration not compliant'
                    }
                }
            ]
        }

    def test_evaluate_rules_no_defects(self):
        """Test evaluate_rules when all rules pass."""
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_template',
            status='IN_PROGRESS',
            started_at=timezone.now(),
            template_snapshot=self.template,
            step_data={
                'visual_inspection': {
                    'cleanliness': 'GOOD',
                    'test_duration': 180
                }
            }
        )

        defects = InspectionRuntime.evaluate_rules(inspection)

        self.assertEqual(len(defects), 0)

    def test_evaluate_rules_with_defects(self):
        """Test evaluate_rules when rules fail."""
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_template',
            status='IN_PROGRESS',
            started_at=timezone.now(),
            template_snapshot=self.template,
            step_data={
                'visual_inspection': {
                    'cleanliness': 'POOR',
                    'test_duration': 175
                }
            }
        )

        defects = InspectionRuntime.evaluate_rules(inspection)

        self.assertEqual(len(defects), 2)

        # Verify defects created
        self.assertEqual(inspection.defects.count(), 2)

    def test_evaluate_rules_multiple_times_idempotent(self):
        """Test calling evaluate_rules multiple times is idempotent."""
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_template',
            status='IN_PROGRESS',
            started_at=timezone.now(),
            template_snapshot=self.template,
            step_data={
                'visual_inspection': {
                    'cleanliness': 'POOR',
                    'test_duration': 180
                }
            }
        )

        # Evaluate first time
        defects1 = InspectionRuntime.evaluate_rules(inspection)
        self.assertEqual(len(defects1), 1)

        # Evaluate second time
        defects2 = InspectionRuntime.evaluate_rules(inspection)
        self.assertEqual(len(defects2), 1)

        # Should only have 1 defect total
        self.assertEqual(inspection.defects.count(), 1)

        # Should be same defect
        self.assertEqual(defects1[0].id, defects2[0].id)

    def test_finalize_with_rules_evaluate_true(self):
        """Test finalize_with_rules with evaluate_rules=True."""
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_template',
            status='IN_PROGRESS',
            started_at=timezone.now(),
            template_snapshot=self.template,
            step_data={
                'visual_inspection': {
                    'cleanliness': 'POOR',
                    'test_duration': 180
                }
            }
        )

        finalized_inspection, defects = InspectionRuntime.finalize_with_rules(
            inspection,
            evaluate_rules=True
        )

        # Inspection should be finalized
        self.assertEqual(finalized_inspection.status, 'COMPLETED')
        self.assertIsNotNone(finalized_inspection.finalized_at)

        # Defects should be generated
        self.assertEqual(len(defects), 1)
        self.assertEqual(inspection.defects.count(), 1)

    def test_finalize_with_rules_evaluate_false(self):
        """Test finalize_with_rules with evaluate_rules=False."""
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_template',
            status='IN_PROGRESS',
            started_at=timezone.now(),
            template_snapshot=self.template,
            step_data={
                'visual_inspection': {
                    'cleanliness': 'POOR',
                    'test_duration': 180
                }
            }
        )

        finalized_inspection, defects = InspectionRuntime.finalize_with_rules(
            inspection,
            evaluate_rules=False
        )

        # Inspection should be finalized
        self.assertEqual(finalized_inspection.status, 'COMPLETED')
        self.assertIsNotNone(finalized_inspection.finalized_at)

        # No defects should be generated
        self.assertEqual(len(defects), 0)
        self.assertEqual(inspection.defects.count(), 0)

    def test_finalize_with_rules_with_signature(self):
        """Test finalize_with_rules with signature data."""
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_template',
            status='IN_PROGRESS',
            started_at=timezone.now(),
            template_snapshot=self.template,
            step_data={
                'visual_inspection': {
                    'cleanliness': 'GOOD',
                    'test_duration': 180
                }
            }
        )

        signature_data = {
            'signature_base64': 'data:image/png;base64,abc123',
            'signed_by': 'John Doe'
        }

        finalized_inspection, defects = InspectionRuntime.finalize_with_rules(
            inspection,
            signature_data=signature_data,
            evaluate_rules=True
        )

        # Inspection should have signature
        self.assertIsNotNone(finalized_inspection.inspector_signature)
        self.assertIn('signature_base64', finalized_inspection.inspector_signature)
        self.assertIn('signed_at', finalized_inspection.inspector_signature)

    def test_evaluate_rules_partial_step_completion(self):
        """Test evaluate_rules with partial step completion."""
        # Template has rules for visual_inspection step
        # But we only provide data for that step
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_template',
            status='IN_PROGRESS',
            started_at=timezone.now(),
            template_snapshot=self.template,
            step_data={
                'visual_inspection': {
                    'cleanliness': 'POOR',
                    'test_duration': 180
                }
            }
        )

        defects = InspectionRuntime.evaluate_rules(inspection)

        # Should only evaluate rules for completed steps
        self.assertEqual(len(defects), 1)  # Only cleanliness failed

    def test_evaluate_rules_empty_step_data(self):
        """Test evaluate_rules with empty step data."""
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_template',
            status='DRAFT',
            started_at=timezone.now(),
            template_snapshot=self.template,
            step_data={}
        )

        defects = InspectionRuntime.evaluate_rules(inspection)

        # No steps completed, so no rules should be evaluated
        self.assertEqual(len(defects), 0)
