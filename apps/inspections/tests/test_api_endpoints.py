"""
Tests for new API endpoints

Tests /evaluate_rules and /defects endpoints.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.customers.models import Customer
from apps.assets.models import Vehicle
from django.utils import timezone


class InspectionAPIRuleEvaluationTests(TestCase):
    """Test API endpoints for rule evaluation."""

    def setUp(self):
        """Create test data."""
        self.client = APIClient()

        # Create user and authenticate
        self.user = User.objects.create_user(username='testuser', password='testpass', is_staff=True)
        self.client.force_authenticate(user=self.user)

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
                            }
                        ]
                    }
                ]
            },
            'rules': [
                {
                    'rule_id': 'cleanliness_check',
                    'title': 'Cleanliness must be GOOD',
                    'when': {'step_key': 'visual_inspection'},
                    'assert': {
                        'type': 'ENUM_EQUALS',
                        'left': {'path': 'cleanliness'},
                        'right': 'GOOD'
                    },
                    'on_fail': {
                        'severity': 'CRITICAL',
                        'defect_title': 'Poor cleanliness',
                        'defect_description': 'Cleanliness below standards'
                    }
                }
            ]
        }

    def test_evaluate_rules_endpoint_no_defects(self):
        """Test POST /inspections/{id}/evaluate_rules/ with no defects."""
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
                    'cleanliness': 'GOOD'
                }
            }
        )

        url = f'/api/inspections/{inspection.id}/evaluate_rules/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['defects_generated'], 0)
        self.assertEqual(len(response.data['defects']), 0)
        self.assertIn('summary', response.data)

    def test_evaluate_rules_endpoint_with_defects(self):
        """Test POST /inspections/{id}/evaluate_rules/ with defects."""
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
                    'cleanliness': 'POOR'
                }
            }
        )

        url = f'/api/inspections/{inspection.id}/evaluate_rules/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['defects_generated'], 1)
        self.assertEqual(len(response.data['defects']), 1)

        # Check defect data
        defect = response.data['defects'][0]
        self.assertEqual(defect['severity'], 'CRITICAL')
        self.assertEqual(defect['title'], 'Poor cleanliness')
        self.assertEqual(defect['status'], 'OPEN')

    def test_evaluate_rules_endpoint_summary_data(self):
        """Test evaluate_rules endpoint returns summary."""
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
                    'cleanliness': 'POOR'
                }
            }
        )

        url = f'/api/inspections/{inspection.id}/evaluate_rules/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        summary = response.data['summary']
        self.assertEqual(summary['total_defects'], 1)
        self.assertEqual(summary['by_severity']['CRITICAL'], 1)
        self.assertEqual(summary['by_status']['OPEN'], 1)

    def test_defects_endpoint_no_defects(self):
        """Test GET /inspections/{id}/defects/ with no defects."""
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_template',
            status='IN_PROGRESS',
            started_at=timezone.now(),
            template_snapshot=self.template,
            step_data={}
        )

        url = f'/api/inspections/{inspection.id}/defects/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['defects']), 0)

    def test_defects_endpoint_with_defects(self):
        """Test GET /inspections/{id}/defects/ with defects."""
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_template',
            status='IN_PROGRESS',
            started_at=timezone.now(),
            template_snapshot=self.template,
            step_data={}
        )

        # Create defects manually
        defect1_identity = InspectionDefect.generate_defect_identity(
            inspection.id, '', 'step_1', 'rule_1'
        )
        defect2_identity = InspectionDefect.generate_defect_identity(
            inspection.id, '', 'step_2', 'rule_2'
        )

        InspectionDefect.objects.create(
            inspection_run=inspection,
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
            inspection_run=inspection,
            defect_identity=defect2_identity,
            module_key='',
            step_key='step_2',
            rule_id='rule_2',
            severity='MAJOR',
            title='Major defect',
            description='Test',
            status='OPEN'
        )

        url = f'/api/inspections/{inspection.id}/defects/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['defects']), 2)

    def test_defects_endpoint_summary(self):
        """Test defects endpoint returns summary."""
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_template',
            status='IN_PROGRESS',
            started_at=timezone.now(),
            template_snapshot=self.template,
            step_data={}
        )

        # Create defects
        defect_identity = InspectionDefect.generate_defect_identity(
            inspection.id, '', 'step_1', 'rule_1'
        )

        InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=defect_identity,
            module_key='',
            step_key='step_1',
            rule_id='rule_1',
            severity='CRITICAL',
            title='Critical defect',
            description='Test',
            status='OPEN'
        )

        url = f'/api/inspections/{inspection.id}/defects/'
        response = self.client.get(url)

        summary = response.data['summary']
        self.assertEqual(summary['total_defects'], 1)
        self.assertEqual(summary['by_severity']['CRITICAL'], 1)

    def test_evaluate_rules_nonexistent_inspection(self):
        """Test evaluate_rules with nonexistent inspection returns 404."""
        import uuid
        fake_id = uuid.uuid4()
        url = f'/api/inspections/{fake_id}/evaluate_rules/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_defects_nonexistent_inspection(self):
        """Test defects endpoint with nonexistent inspection returns 404."""
        import uuid
        fake_id = uuid.uuid4()
        url = f'/api/inspections/{fake_id}/defects/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_evaluate_rules_idempotent(self):
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
                    'cleanliness': 'POOR'
                }
            }
        )

        url = f'/api/inspections/{inspection.id}/evaluate_rules/'

        # Call first time
        response1 = self.client.post(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data['defects_generated'], 1)

        # Call second time
        response2 = self.client.post(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['defects_generated'], 1)

        # Should still only have 1 defect
        self.assertEqual(inspection.defects.count(), 1)
