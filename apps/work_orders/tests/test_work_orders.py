"""
Comprehensive tests for Work Order Creation and Management (Phase 2 Milestones 4-5).

Tests use only seeded data from seed_config.py and follow DATA_CONTRACT.md.
No hardcoded values.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.customers.models import Customer
from apps.assets.models import Vehicle
from apps.organization.models import Department
from apps.work_orders.models import WorkOrder
import hashlib

User = get_user_model()


class WorkOrderTestCase(TestCase):
    """Base test case for work order tests."""

    def setUp(self):
        """Set up test fixtures using seed config principles."""
        self.client = APIClient()

        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        self.client.force_authenticate(user=self.user)

        # Create department from seed config (DEPARTMENTS[1])
        self.dept, _ = Department.objects.get_or_create(
            code='SVCRPR',
            defaults={'name': 'Service & Repair', 'allows_floating': True}
        )

        # Create customer (from CUSTOMERS pattern)
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
            model='F-150'
        )

        # Minimal template for inspections
        self.template_data = {
            'template': {
                'template_key': 'test_template',
                'name': 'Test Template',
                'version': '1.0.0'
            },
            'procedure': {
                'title': 'Test Procedure',
                'steps': []
            }
        }

    def create_inspection(self):
        """Helper to create inspection."""
        from django.utils import timezone

        return InspectionRun.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            template_key='test_template',
            template_snapshot=self.template_data,
            status='IN_PROGRESS',
            started_at=timezone.now()
        )

    def create_defect(self, inspection, severity, title, description='', location='', step_key='step_01'):
        """Helper to create defect with proper hash."""
        identity_string = f"{inspection.id}{step_key}{title}"
        defect_identity = hashlib.sha256(identity_string.encode()).hexdigest()

        return InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=defect_identity,
            step_key=step_key,
            severity=severity,
            title=title,
            description=description,
            defect_details={'location': location} if location else {}
        )


class WorkOrderCreationTests(WorkOrderTestCase):
    """Tests for work order creation from inspection defects."""

    def test_create_work_order_from_single_defect(self):
        """Test creating work order from single defect."""
        inspection = self.create_inspection()

        defect = self.create_defect(
            inspection,
            severity='CRITICAL',
            title='Brake failure risk',
            location='Brake System',
            step_key='brake_01'
        )

        response = self.client.post(
            '/api/work-orders/from_defect/',
            data={
                'defect_id': str(defect.id),
                'department_id': str(self.dept.id),
                'priority': 'EMERGENCY'
            },
            format='json'
        )

        # from_defect returns 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()

        wo = WorkOrder.objects.get(id=data['id'])
        self.assertEqual(wo.priority, 'EMERGENCY')
        self.assertEqual(wo.defect_links.count(), 1)

    def test_create_work_order_with_normal_priority(self):
        """Test creating work order with normal priority."""
        inspection = self.create_inspection()

        defect = self.create_defect(
            inspection,
            severity='MINOR',
            title='Minor maintenance needed',
            location='Engine Bay',
            step_key='maintenance_01'
        )

        response = self.client.post(
            '/api/work-orders/from_defect/',
            data={
                'defect_id': str(defect.id),
                'department_id': str(self.dept.id)
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()

        wo = WorkOrder.objects.get(id=data['id'])
        self.assertEqual(wo.status, 'PENDING')
        self.assertEqual(wo.source_type, 'INSPECTION_DEFECT')

    def test_work_order_links_to_inspection(self):
        """Test that work order maintains reference to source inspection."""
        inspection = self.create_inspection()

        defect = self.create_defect(
            inspection,
            severity='MAJOR',
            title='Hydraulic leak',
            step_key='check_01'
        )

        response = self.client.post(
            '/api/work-orders/from_defect/',
            data={
                'defect_id': str(defect.id),
                'department_id': str(self.dept.id)
            },
            format='json'
        )

        wo = WorkOrder.objects.get(id=response.json()['id'])

        # Verify work order created from defect
        self.assertEqual(wo.defect_links.first().defect.inspection_run, inspection)
        self.assertEqual(wo.customer, inspection.customer)
        self.assertEqual(wo.asset_type, inspection.asset_type)


class WorkOrderManagementTests(WorkOrderTestCase):
    """Tests for work order management operations."""

    def test_list_work_orders(self):
        """Test listing work orders."""
        inspection = self.create_inspection()
        defect = self.create_defect(inspection, 'MAJOR', 'Test defect')

        # Create work order
        self.client.post(
            '/api/work-orders/from_defect/',
            data={
                'defect_id': str(defect.id),
                'department_id': str(self.dept.id)
            },
            format='json'
        )

        # List work orders
        response = self.client.get('/api/work-orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn('results', data)
        self.assertGreater(len(data['results']), 0)

    def test_work_order_detail(self):
        """Test retrieving work order details."""
        inspection = self.create_inspection()
        defect = self.create_defect(inspection, 'MAJOR', 'Major priority defect')

        create_response = self.client.post(
            '/api/work-orders/from_defect/',
            data={
                'defect_id': str(defect.id),
                'department_id': str(self.dept.id),
                'priority': 'HIGH'
            },
            format='json'
        )

        wo_id = create_response.json()['id']

        response = self.client.get(f'/api/work-orders/{wo_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['id'], wo_id)
        self.assertEqual(data['priority'], 'HIGH')

    def test_start_work_order(self):
        """Test starting a work order."""
        inspection = self.create_inspection()
        defect = self.create_defect(inspection, 'MAJOR', 'Repair needed')

        create_response = self.client.post(
            '/api/work-orders/from_defect/',
            data={
                'defect_id': str(defect.id),
                'department_id': str(self.dept.id)
            },
            format='json'
        )

        wo_id = create_response.json()['id']

        response = self.client.post(f'/api/work-orders/{wo_id}/start/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        wo = WorkOrder.objects.get(id=wo_id)
        self.assertEqual(wo.status, 'IN_PROGRESS')
        self.assertIsNotNone(wo.started_at)

    def test_complete_work_order(self):
        """Test completing a work order."""
        inspection = self.create_inspection()
        defect = self.create_defect(inspection, 'MAJOR', 'Repair completed')

        create_response = self.client.post(
            '/api/work-orders/from_defect/',
            data={
                'defect_id': str(defect.id),
                'department_id': str(self.dept.id)
            },
            format='json'
        )

        wo_id = create_response.json()['id']

        # Start then complete
        self.client.post(f'/api/work-orders/{wo_id}/start/')
        response = self.client.post(f'/api/work-orders/{wo_id}/complete/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        wo = WorkOrder.objects.get(id=wo_id)
        self.assertEqual(wo.status, 'COMPLETED')
        self.assertIsNotNone(wo.completed_at)
