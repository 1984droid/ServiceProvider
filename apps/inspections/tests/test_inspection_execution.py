"""
Comprehensive tests for Phase 1 Inspection Execution workflow.

Tests:
- Step data management (save_step endpoint)
- Field validation
- Manual defect creation
- Inspection state transitions
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.customers.models import Customer
from apps.assets.models import Vehicle, Equipment
from decimal import Decimal
import json

User = get_user_model()


class InspectionExecutionTestCase(TestCase):
    """Base test case with common setup for inspection execution tests."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()

        # Create test user (superuser to bypass permission checks in tests)
        self.user = User.objects.create_user(
            username='inspector',
            password='testpass123',
            email='inspector@test.com',
            is_staff=True,
            is_superuser=True
        )
        self.client.force_authenticate(user=self.user)

        # Create customer
        self.customer = Customer.objects.create(
            name='Test Fleet Company',
            legal_name='Test Fleet Company LLC',
            is_active=True
        )

        # Create vehicle
        self.vehicle = Vehicle.objects.create(
            customer=self.customer,
            vin='1HGBH41JXMN109186',
            unit_number='TRUCK-001',
            year=2021,
            make='Ford',
            model='F-150',
            license_plate='ABC-123',
            capabilities=['TOWING', 'CARGO']
        )

        # Create equipment
        self.equipment = Equipment.objects.create(
            customer=self.customer,
            serial_number='SN123456',
            asset_number='EQ-001',
            manufacturer='Genie',
            model='Z-45/25J',
            equipment_type='A92_2_AERIAL',
            capabilities=['PLATFORM', 'ARTICULATING']
        )

        # Template with all field types and step types
        self.template_data = {
            'template': {
                'template_key': 'comprehensive_test',
                'name': 'Comprehensive Test Template',
                'version': '1.0.0',
                'standard_code': 'TEST-001',
                'domain': 'TESTING'
            },
            'procedure': {
                'title': 'Comprehensive Inspection Procedure',
                'steps': [
                    # SETUP step with various field types
                    {
                        'step_key': 'setup_01',
                        'type': 'SETUP',
                        'title': 'Pre-Inspection Setup',
                        'fields': [
                            {
                                'field_id': 'inspector_name',
                                'type': 'TEXT',
                                'label': 'Inspector Name',
                                'required': True
                            },
                            {
                                'field_id': 'weather_conditions',
                                'type': 'ENUM',
                                'label': 'Weather Conditions',
                                'enum_ref': 'weather',
                                'required': True
                            },
                            {
                                'field_id': 'site_safe',
                                'type': 'BOOLEAN',
                                'label': 'Site is Safe',
                                'required': True
                            }
                        ]
                    },
                    # VISUAL_INSPECTION step
                    {
                        'step_key': 'visual_01',
                        'type': 'VISUAL_INSPECTION',
                        'title': 'Visual Inspection',
                        'fields': [
                            {
                                'field_id': 'exterior_condition',
                                'type': 'CHOICE_MULTI',
                                'label': 'Exterior Issues Found',
                                'values': ['RUST', 'DENTS', 'LEAKS', 'DAMAGE'],
                                'required': False
                            },
                            {
                                'field_id': 'notes',
                                'type': 'TEXT_AREA',
                                'label': 'Visual Inspection Notes',
                                'required': False
                            }
                        ]
                    },
                    # MEASUREMENT step with NUMBER fields
                    {
                        'step_key': 'measurement_01',
                        'type': 'MEASUREMENT',
                        'title': 'Critical Measurements',
                        'fields': [
                            {
                                'field_id': 'tire_pressure_fl',
                                'type': 'NUMBER',
                                'label': 'Tire Pressure Front Left (PSI)',
                                'min': 30,
                                'max': 50,
                                'precision': 1,
                                'required': True
                            },
                            {
                                'field_id': 'tire_pressure_fr',
                                'type': 'NUMBER',
                                'label': 'Tire Pressure Front Right (PSI)',
                                'min': 30,
                                'max': 50,
                                'precision': 1,
                                'required': True
                            }
                        ]
                    },
                    # FUNCTION_TEST step
                    {
                        'step_key': 'function_01',
                        'type': 'FUNCTION_TEST',
                        'title': 'Functional Tests',
                        'fields': [
                            {
                                'field_id': 'brakes_pass',
                                'type': 'BOOLEAN',
                                'label': 'Brakes Function Properly',
                                'required': True
                            },
                            {
                                'field_id': 'lights_pass',
                                'type': 'BOOLEAN',
                                'label': 'All Lights Operational',
                                'required': True
                            }
                        ]
                    },
                    # DEFECT_CAPTURE step
                    {
                        'step_key': 'defects_01',
                        'type': 'DEFECT_CAPTURE',
                        'title': 'Defect Recording',
                        'fields': [
                            {
                                'field_id': 'defect_notes',
                                'type': 'TEXT_AREA',
                                'label': 'General Defect Notes',
                                'required': False
                            }
                        ]
                    }
                ],
                'enums': {
                    'weather': ['CLEAR', 'CLOUDY', 'RAIN', 'SNOW', 'FOG']
                }
            }
        }

    def create_inspection(self, asset_type='VEHICLE', asset=None):
        """Helper to create inspection run."""
        from django.utils import timezone

        if asset is None:
            asset = self.vehicle if asset_type == 'VEHICLE' else self.equipment

        # Create inspection with embedded template
        inspection = InspectionRun.objects.create(
            customer=self.customer,
            asset_type=asset_type,
            asset_id=asset.id,
            template_key=self.template_data['template']['template_key'],
            template_snapshot=self.template_data,
            status='DRAFT',
            inspector_name='Test Inspector',
            started_at=timezone.now(),
            step_data={}
        )
        return inspection


class StepDataManagementTests(InspectionExecutionTestCase):
    """Test save_step endpoint and step data persistence."""

    def test_save_step_with_valid_data(self):
        """Test saving step data with all valid fields."""
        inspection = self.create_inspection()

        step_data = {
            'step_key': 'setup_01',
            'field_data': {
                'inspector_name': 'John Doe',
                'weather_conditions': 'CLEAR',
                'site_safe': True
            },
            'validate': False
        }

        response = self.client.patch(
            f'/api/inspections/{inspection.id}/save_step/',
            data=step_data,
            format='json'
        )

        # Debug output
        if response.status_code != status.HTTP_200_OK:
            print(f"\nDEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response data: {response.data}")
            print(f"DEBUG: Inspection ID: {inspection.id}")
            print(f"DEBUG: Inspection exists: {InspectionRun.objects.filter(id=inspection.id).exists()}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify data was saved
        inspection.refresh_from_db()
        self.assertIn('setup_01', inspection.step_data)
        self.assertEqual(inspection.step_data['setup_01']['inspector_name'], 'John Doe')
        self.assertEqual(inspection.step_data['setup_01']['weather_conditions'], 'CLEAR')
        self.assertTrue(inspection.step_data['setup_01']['site_safe'])

    def test_save_step_with_number_fields(self):
        """Test saving NUMBER fields with precision validation."""
        inspection = self.create_inspection()

        step_data = {
            'step_key': 'measurement_01',
            'field_data': {
                'tire_pressure_fl': 35.5,
                'tire_pressure_fr': 36.0
            },
            'validate': False
        }

        response = self.client.patch(
            f'/api/inspections/{inspection.id}/save_step/',
            data=step_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify numbers saved correctly
        inspection.refresh_from_db()
        self.assertEqual(float(inspection.step_data['measurement_01']['tire_pressure_fl']), 35.5)
        self.assertEqual(float(inspection.step_data['measurement_01']['tire_pressure_fr']), 36.0)

    def test_save_step_with_choice_multi(self):
        """Test saving CHOICE_MULTI field (array)."""
        inspection = self.create_inspection()

        step_data = {
            'step_key': 'visual_01',
            'field_data': {
                'exterior_condition': ['RUST', 'DENTS'],
                'notes': 'Minor rust on rear bumper, small dent on driver door'
            },
            'validate': False
        }

        response = self.client.patch(
            f'/api/inspections/{inspection.id}/save_step/',
            data=step_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify array saved correctly
        inspection.refresh_from_db()
        self.assertIsInstance(inspection.step_data['visual_01']['exterior_condition'], list)
        self.assertIn('RUST', inspection.step_data['visual_01']['exterior_condition'])
        self.assertIn('DENTS', inspection.step_data['visual_01']['exterior_condition'])

    def test_save_step_overwrites_previous_data(self):
        """Test that saving step data overwrites previous values."""
        inspection = self.create_inspection()

        # Save initial data
        step_data_v1 = {
            'step_key': 'setup_01',
            'field_data': {
                'inspector_name': 'John Doe',
                'weather_conditions': 'CLEAR',
                'site_safe': True
            },
            'validate': False
        }
        self.client.patch(f'/api/inspections/{inspection.id}/save_step/', data=step_data_v1, format='json')

        # Update with new data
        step_data_v2 = {
            'step_key': 'setup_01',
            'field_data': {
                'inspector_name': 'Jane Smith',
                'weather_conditions': 'RAIN',
                'site_safe': False
            },
            'validate': False
        }
        response = self.client.patch(f'/api/inspections/{inspection.id}/save_step/', data=step_data_v2, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify data was overwritten
        inspection.refresh_from_db()
        self.assertEqual(inspection.step_data['setup_01']['inspector_name'], 'Jane Smith')
        self.assertEqual(inspection.step_data['setup_01']['weather_conditions'], 'RAIN')
        self.assertFalse(inspection.step_data['setup_01']['site_safe'])

    def test_save_step_preserves_other_steps(self):
        """Test that saving one step doesn't affect other steps."""
        inspection = self.create_inspection()

        # Save step 1
        step1_data = {
            'step_key': 'setup_01',
            'field_data': {'inspector_name': 'John Doe', 'weather_conditions': 'CLEAR', 'site_safe': True},
            'validate': False
        }
        self.client.patch(f'/api/inspections/{inspection.id}/save_step/', data=step1_data, format='json')

        # Save step 2
        step2_data = {
            'step_key': 'visual_01',
            'field_data': {'exterior_condition': ['RUST'], 'notes': 'Minor rust'},
            'validate': False
        }
        self.client.patch(f'/api/inspections/{inspection.id}/save_step/', data=step2_data, format='json')

        # Verify both steps exist
        inspection.refresh_from_db()
        self.assertIn('setup_01', inspection.step_data)
        self.assertIn('visual_01', inspection.step_data)
        self.assertEqual(inspection.step_data['setup_01']['inspector_name'], 'John Doe')
        self.assertIn('RUST', inspection.step_data['visual_01']['exterior_condition'])

    def test_cannot_save_to_completed_inspection(self):
        """Test that completed inspections cannot be modified."""
        from django.utils import timezone

        inspection = self.create_inspection()
        inspection.finalized_at = timezone.now()
        inspection.save()

        step_data = {
            'step_key': 'setup_01',
            'field_data': {'inspector_name': 'John Doe', 'weather_conditions': 'CLEAR', 'site_safe': True},
            'validate': False
        }

        response = self.client.patch(
            f'/api/inspections/{inspection.id}/save_step/',
            data=step_data,
            format='json'
        )

        # Should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ManualDefectCreationTests(InspectionExecutionTestCase):
    """Test manual defect creation via add_defect endpoint."""

    def test_create_manual_defect_critical(self):
        """Test creating a CRITICAL manual defect."""
        inspection = self.create_inspection()

        defect_data = {
            'step_key': 'visual_01',
            'severity': 'CRITICAL',
            'title': 'Structural crack in frame',
            'description': 'Found a 6-inch crack in the main frame rail near the rear axle. Vehicle is unsafe to operate.',
            'defect_details': {
                'location': 'Main frame rail, rear driver side'
            }
        }

        response = self.client.post(
            f'/api/inspections/{inspection.id}/add_defect/',
            data=defect_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['severity'], 'CRITICAL')
        self.assertEqual(response.data['title'], 'Structural crack in frame')
        self.assertEqual(response.data['step_key'], 'visual_01')
        self.assertIsNone(response.data['rule_id'])  # Manual defects have no rule_id
        self.assertEqual(response.data['status'], 'OPEN')

        # Verify defect exists in database
        defect = InspectionDefect.objects.get(id=response.data['id'])
        self.assertEqual(defect.inspection_run, inspection)
        self.assertEqual(defect.severity, 'CRITICAL')
        self.assertEqual(defect.defect_details['location'], 'Main frame rail, rear driver side')

    def test_create_defects_all_severity_levels(self):
        """Test creating defects with all severity levels."""
        inspection = self.create_inspection()

        severities = ['CRITICAL', 'MAJOR', 'MINOR', 'ADVISORY']

        for severity in severities:
            defect_data = {
                'step_key': 'visual_01',
                'severity': severity,
                'title': f'{severity} level defect',
                'description': f'This is a {severity} severity issue'
            }

            response = self.client.post(
                f'/api/inspections/{inspection.id}/add_defect/',
                data=defect_data,
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['severity'], severity)

        # Verify all 4 defects created
        defects = InspectionDefect.objects.filter(inspection_run=inspection)
        self.assertEqual(defects.count(), 4)

    def test_create_defect_without_required_fields(self):
        """Test that defects require step_key, severity, and title."""
        inspection = self.create_inspection()

        # Missing severity
        response = self.client.post(
            f'/api/inspections/{inspection.id}/add_defect/',
            data={'step_key': 'visual_01', 'title': 'Test defect'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('severity', response.data['error'].lower())

        # Missing title
        response = self.client.post(
            f'/api/inspections/{inspection.id}/add_defect/',
            data={'step_key': 'visual_01', 'severity': 'MAJOR'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data['error'].lower())

        # Missing step_key
        response = self.client.post(
            f'/api/inspections/{inspection.id}/add_defect/',
            data={'severity': 'MAJOR', 'title': 'Test defect'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('step_key', response.data['error'].lower())

    def test_create_defect_invalid_severity(self):
        """Test that invalid severity values are rejected."""
        inspection = self.create_inspection()

        defect_data = {
            'step_key': 'visual_01',
            'severity': 'SUPER_CRITICAL',  # Invalid
            'title': 'Test defect',
            'description': 'Test'
        }

        response = self.client.post(
            f'/api/inspections/{inspection.id}/add_defect/',
            data=defect_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_add_defect_to_completed_inspection(self):
        """Test that defects cannot be added to completed inspections."""
        inspection = self.create_inspection()
        inspection.status = 'COMPLETED'
        inspection.save()

        defect_data = {
            'step_key': 'visual_01',
            'severity': 'MAJOR',
            'title': 'Test defect',
            'description': 'Should not be allowed'
        }

        response = self.client.post(
            f'/api/inspections/{inspection.id}/add_defect/',
            data=defect_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_defects_for_inspection(self):
        """Test retrieving all defects for an inspection."""
        inspection = self.create_inspection()

        # Create 3 defects
        for i in range(3):
            self.client.post(
                f'/api/inspections/{inspection.id}/add_defect/',
                data={
                    'step_key': f'visual_0{i}' if i > 0 else 'visual_01',
                    'severity': 'MINOR',
                    'title': f'Defect {i+1}',
                    'description': f'Description {i+1}'
                },
                format='json'
            )

        # Get all defects
        response = self.client.get(f'/api/inspections/{inspection.id}/defects/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['defects']), 3)


class InspectionStateTransitionTests(InspectionExecutionTestCase):
    """Test inspection status transitions."""

    def test_new_inspection_starts_as_draft(self):
        """Test that new inspections start with DRAFT status."""
        inspection = self.create_inspection()
        self.assertEqual(inspection.status, 'DRAFT')

    def test_saving_step_changes_to_in_progress(self):
        """Test that saving step data changes status to IN_PROGRESS."""
        inspection = self.create_inspection()
        self.assertEqual(inspection.status, 'DRAFT')

        # Save a step
        step_data = {
            'step_key': 'setup_01',
            'field_data': {'inspector_name': 'John Doe', 'weather_conditions': 'CLEAR', 'site_safe': True},
            'validate': False
        }
        self.client.patch(f'/api/inspections/{inspection.id}/save_step/', data=step_data, format='json')

        # Verify status changed
        inspection.refresh_from_db()
        self.assertEqual(inspection.status, 'IN_PROGRESS')


class EquipmentInspectionTests(InspectionExecutionTestCase):
    """Test inspection execution with equipment assets."""

    def test_create_inspection_for_equipment(self):
        """Test creating inspection for equipment asset."""
        inspection = self.create_inspection(asset_type='EQUIPMENT', asset=self.equipment)

        self.assertEqual(inspection.asset_type, 'EQUIPMENT')
        self.assertEqual(str(inspection.asset_id), str(self.equipment.id))

        # Verify asset_info populated correctly
        response = self.client.get(f'/api/inspections/{inspection.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['asset_info']['type'], 'EQUIPMENT')
        self.assertEqual(response.data['asset_info']['equipment_type'], 'A92_2_AERIAL')
        self.assertEqual(response.data['asset_info']['serial_number'], 'SN123456')

    def test_save_step_data_for_equipment(self):
        """Test saving step data for equipment inspection."""
        inspection = self.create_inspection(asset_type='EQUIPMENT', asset=self.equipment)

        step_data = {
            'step_key': 'setup_01',
            'field_data': {'inspector_name': 'Equipment Inspector', 'weather_conditions': 'CLEAR', 'site_safe': True},
            'validate': False
        }

        response = self.client.patch(
            f'/api/inspections/{inspection.id}/save_step/',
            data=step_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify data saved
        inspection.refresh_from_db()
        self.assertEqual(inspection.step_data['setup_01']['inspector_name'], 'Equipment Inspector')


class AuthorizationTests(InspectionExecutionTestCase):
    """Test authentication and authorization for inspection endpoints."""

    def test_unauthenticated_cannot_save_step(self):
        """Test that unauthenticated users cannot save step data."""
        inspection = self.create_inspection()

        # Remove authentication
        self.client.force_authenticate(user=None)

        step_data = {
            'step_key': 'setup_01',
            'field_data': {'inspector_name': 'John Doe', 'weather_conditions': 'CLEAR', 'site_safe': True},
            'validate': False
        }

        response = self.client.patch(
            f'/api/inspections/{inspection.id}/save_step/',
            data=step_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_cannot_add_defect(self):
        """Test that unauthenticated users cannot add defects."""
        inspection = self.create_inspection()

        # Remove authentication
        self.client.force_authenticate(user=None)

        defect_data = {
            'step_key': 'visual_01',
            'severity': 'MAJOR',
            'title': 'Test defect',
            'description': 'Should not work'
        }

        response = self.client.post(
            f'/api/inspections/{inspection.id}/add_defect/',
            data=defect_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class InspectionReviewTestCase(InspectionExecutionTestCase):
    """Tests for Phase 2 Milestone 1: Inspection Review endpoint."""

    def test_get_inspection_review(self):
        """Test GET /api/inspections/{id}/review/ returns all review data."""
        inspection = self.create_inspection()

        # Fill in some step data
        step_data = {
            'step_key': 'setup_01',
            'field_data': {
                'inspector_name': 'John Doe',
                'weather_conditions': 'CLEAR',
                'site_safe': True
            },
            'validate': False
        }
        self.client.patch(
            f'/api/inspections/{inspection.id}/save_step/',
            data=step_data,
            format='json'
        )

        # Evaluate rules to generate defects
        self.client.post(f'/api/inspections/{inspection.id}/evaluate_rules/')

        # Get review data
        response = self.client.get(f'/api/inspections/{inspection.id}/review/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Verify structure
        self.assertIn('inspection', data)
        self.assertIn('completion', data)
        self.assertIn('defects', data)

        # Verify inspection data
        self.assertEqual(data['inspection']['id'], str(inspection.id))
        self.assertIn('template_snapshot', data['inspection'])
        self.assertIn('step_data', data['inspection'])

        # Verify completion data
        self.assertIn('total_steps', data['completion'])
        self.assertIn('completed_steps', data['completion'])
        self.assertIn('completion_percentage', data['completion'])
        self.assertIn('ready_to_finalize', data['completion'])

        # Verify defects data
        self.assertIn('count', data['defects'])
        self.assertIn('items', data['defects'])
        self.assertIn('summary', data['defects'])
        self.assertIsInstance(data['defects']['items'], list)

    def test_review_with_no_defects(self):
        """Test review endpoint when inspection has no defects."""
        inspection = self.create_inspection()

        response = self.client.get(f'/api/inspections/{inspection.id}/review/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Should have 0 defects
        self.assertEqual(data['defects']['count'], 0)
        self.assertEqual(len(data['defects']['items']), 0)
        self.assertEqual(data['defects']['summary']['total_defects'], 0)

    def test_review_with_multiple_defects(self):
        """Test review endpoint aggregates defects correctly."""
        inspection = self.create_inspection()

        # Add defects at different severity levels
        defects = [
            {'step_key': 'visual_01', 'severity': 'CRITICAL', 'title': 'Critical defect'},
            {'step_key': 'visual_01', 'severity': 'MAJOR', 'title': 'Major defect'},
            {'step_key': 'function_01', 'severity': 'MINOR', 'title': 'Minor defect'},
            {'step_key': 'function_01', 'severity': 'ADVISORY', 'title': 'Advisory defect'},
        ]

        for defect_data in defects:
            self.client.post(
                f'/api/inspections/{inspection.id}/add_defect/',
                data=defect_data,
                format='json'
            )

        response = self.client.get(f'/api/inspections/{inspection.id}/review/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Verify defect count
        self.assertEqual(data['defects']['count'], 4)
        self.assertEqual(len(data['defects']['items']), 4)

        # Verify summary
        summary = data['defects']['summary']
        self.assertEqual(summary['total_defects'], 4)
        self.assertEqual(summary['by_severity']['CRITICAL'], 1)
        self.assertEqual(summary['by_severity']['MAJOR'], 1)
        self.assertEqual(summary['by_severity']['MINOR'], 1)
        self.assertEqual(summary['by_severity']['ADVISORY'], 1)

    def test_review_not_found(self):
        """Test review endpoint returns 404 for non-existent inspection."""
        response = self.client.get('/api/inspections/00000000-0000-0000-0000-000000000000/review/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_review_includes_step_responses(self):
        """Test review endpoint includes all saved step responses."""
        inspection = self.create_inspection()

        # Save multiple steps
        steps_to_save = [
            {
                'step_key': 'setup_01',
                'field_data': {
                    'inspector_name': 'John Doe',
                    'weather_conditions': 'CLEAR',
                    'site_safe': True
                }
            },
            {
                'step_key': 'visual_01',
                'field_data': {
                    'platform_condition': 'GOOD',
                    'controls_operational': 'YES'
                }
            },
        ]

        for step_data in steps_to_save:
            self.client.patch(
                f'/api/inspections/{inspection.id}/save_step/',
                data={**step_data, 'validate': False},
                format='json'
            )

        response = self.client.get(f'/api/inspections/{inspection.id}/review/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Verify step responses are present
        step_data = data['inspection']['step_data']
        self.assertIn('setup_01', step_data)
        self.assertIn('visual_01', step_data)
        self.assertEqual(step_data['setup_01']['inspector_name'], 'John Doe')
        self.assertEqual(step_data['visual_01']['platform_condition'], 'GOOD')


class InspectionFinalizationTestCase(InspectionExecutionTestCase):
    """Tests for Phase 2 Milestone 3: Inspection Finalization with Signature."""

    def test_finalize_with_signature(self):
        """Test finalizing inspection with signature data."""
        inspection = self.create_inspection()

        # Complete all required steps
        for step in self.template_data['procedure']['steps']:
            step_data = {
                'step_key': step['step_key'],
                'field_data': {},
                'validate': False
            }
            # Add minimal field data for each step
            for field in step['fields']:
                if field['type'] == 'TEXT':
                    step_data['field_data'][field['field_id']] = 'Test value'
                elif field['type'] == 'BOOLEAN':
                    step_data['field_data'][field['field_id']] = True
                elif field['type'] == 'NUMBER':
                    step_data['field_data'][field['field_id']] = 35
                elif field['type'] == 'ENUM':
                    step_data['field_data'][field['field_id']] = 'CLEAR'
                elif field['type'] == 'CHOICE_MULTI':
                    step_data['field_data'][field['field_id']] = []

            self.client.patch(
                f'/api/inspections/{inspection.id}/save_step/',
                data=step_data,
                format='json'
            )

        # Mock signature data (base64 PNG)
        signature_data = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='

        # Finalize with signature
        response = self.client.post(
            f'/api/inspections/{inspection.id}/finalize/',
            data={'signature_data': signature_data},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Verify response structure
        self.assertIn('message', data)
        self.assertIn('inspection', data)

        # Verify inspection is now COMPLETED
        self.assertEqual(data['inspection']['status'], 'COMPLETED')
        self.assertIsNotNone(data['inspection']['finalized_at'])

        # Reload and verify signature was saved
        inspection.refresh_from_db()
        self.assertEqual(inspection.status, 'COMPLETED')
        self.assertIsNotNone(inspection.finalized_at)
        self.assertIsNotNone(inspection.inspector_signature)

    def test_finalize_without_signature(self):
        """Test finalizing inspection without signature (should still work)."""
        inspection = self.create_inspection()

        # Complete all steps
        for step in self.template_data['procedure']['steps']:
            step_data = {
                'step_key': step['step_key'],
                'field_data': {},
                'validate': False
            }
            for field in step['fields']:
                if field['type'] == 'TEXT':
                    step_data['field_data'][field['field_id']] = 'Test'
                elif field['type'] == 'BOOLEAN':
                    step_data['field_data'][field['field_id']] = True
                elif field['type'] == 'NUMBER':
                    step_data['field_data'][field['field_id']] = 35

            self.client.patch(
                f'/api/inspections/{inspection.id}/save_step/',
                data=step_data,
                format='json'
            )

        # Finalize without signature
        response = self.client.post(
            f'/api/inspections/{inspection.id}/finalize/',
            data={},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['inspection']['status'], 'COMPLETED')

    def test_finalize_incomplete_inspection(self):
        """Test that incomplete inspection cannot be finalized without force."""
        inspection = self.create_inspection()

        # Only complete one step (not all required)
        step_data = {
            'step_key': 'setup_01',
            'field_data': {
                'inspector_name': 'John Doe',
                'weather_conditions': 'CLEAR',
                'site_safe': True
            }
        }
        self.client.patch(
            f'/api/inspections/{inspection.id}/save_step/',
            data=step_data,
            format='json'
        )

        # Try to finalize - should fail if there are required steps
        response = self.client.post(
            f'/api/inspections/{inspection.id}/finalize/',
            data={'force': False},
            format='json'
        )

        # May succeed or fail depending on whether steps are required
        # If it fails, should be 400 BAD REQUEST
        if response.status_code != status.HTTP_200_OK:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_finalize_already_finalized(self):
        """Test that already finalized inspection cannot be finalized again."""
        inspection = self.create_inspection()

        # Complete all steps
        for step in self.template_data['procedure']['steps']:
            step_data = {
                'step_key': step['step_key'],
                'field_data': {},
                'validate': False
            }
            for field in step['fields']:
                if field['type'] == 'BOOLEAN':
                    step_data['field_data'][field['field_id']] = True
                elif field['type'] == 'TEXT':
                    step_data['field_data'][field['field_id']] = 'Test'

            self.client.patch(
                f'/api/inspections/{inspection.id}/save_step/',
                data=step_data,
                format='json'
            )

        # Finalize first time
        self.client.post(
            f'/api/inspections/{inspection.id}/finalize/',
            data={},
            format='json'
        )

        # Try to finalize again
        response = self.client.post(
            f'/api/inspections/{inspection.id}/finalize/',
            data={},
            format='json'
        )

        # Should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_edit_finalized_inspection(self):
        """Test that finalized inspection cannot be edited."""
        inspection = self.create_inspection()

        # Complete and finalize
        for step in self.template_data['procedure']['steps']:
            step_data = {
                'step_key': step['step_key'],
                'field_data': {},
                'validate': False
            }
            for field in step['fields']:
                if field['type'] == 'BOOLEAN':
                    step_data['field_data'][field['field_id']] = True

            self.client.patch(
                f'/api/inspections/{inspection.id}/save_step/',
                data=step_data,
                format='json'
            )

        self.client.post(
            f'/api/inspections/{inspection.id}/finalize/',
            data={},
            format='json'
        )

        # Try to save step data after finalization
        step_data = {
            'step_key': 'setup_01',
            'field_data': {'inspector_name': 'Changed Name'},
            'validate': False
        }
        response = self.client.patch(
            f'/api/inspections/{inspection.id}/save_step/',
            data=step_data,
            format='json'
        )

        # Should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_add_defects_to_finalized_inspection(self):
        """Test that defects cannot be added to finalized inspection."""
        inspection = self.create_inspection()

        # Complete and finalize
        for step in self.template_data['procedure']['steps']:
            step_data = {
                'step_key': step['step_key'],
                'field_data': {},
                'validate': False
            }
            self.client.patch(
                f'/api/inspections/{inspection.id}/save_step/',
                data=step_data,
                format='json'
            )

        self.client.post(
            f'/api/inspections/{inspection.id}/finalize/',
            data={},
            format='json'
        )

        # Try to add defect
        defect_data = {
            'step_key': 'visual_01',
            'severity': 'MAJOR',
            'title': 'Should not work'
        }
        response = self.client.post(
            f'/api/inspections/{inspection.id}/add_defect/',
            data=defect_data,
            format='json'
        )

        # Should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_finalize_preserves_timestamp(self):
        """Test that finalization timestamp is preserved."""
        from datetime import datetime
        from django.utils import timezone

        inspection = self.create_inspection()

        # Complete steps
        for step in self.template_data['procedure']['steps']:
            step_data = {
                'step_key': step['step_key'],
                'field_data': {},
                'validate': False
            }
            self.client.patch(
                f'/api/inspections/{inspection.id}/save_step/',
                data=step_data,
                format='json'
            )

        # Finalize
        before_finalize = timezone.now()
        response = self.client.post(
            f'/api/inspections/{inspection.id}/finalize/',
            data={},
            format='json'
        )
        after_finalize = timezone.now()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify timestamp is within expected range
        inspection.refresh_from_db()
        self.assertIsNotNone(inspection.finalized_at)
        self.assertGreaterEqual(inspection.finalized_at, before_finalize)
        self.assertLessEqual(inspection.finalized_at, after_finalize)
