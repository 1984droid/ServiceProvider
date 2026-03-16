"""
Tests for Work Order Creation API Endpoint

Tests the POST /api/inspections/{id}/create_work_orders/ endpoint.
"""

import hashlib
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.work_orders.models import WorkOrder
from apps.customers.models import Customer
from apps.assets.models import Vehicle
from apps.organization.models import Department
from django.contrib.auth.models import User


def make_defect_identity(key: str) -> str:
    """Generate valid 64-char SHA256 hash for defect identity."""
    return hashlib.sha256(key.encode()).hexdigest()


class WorkOrderCreationAPITest(TestCase):
    """Test work order creation API endpoint."""

    def setUp(self):
        """Set up test fixtures."""
        # Create user
        self.user = User.objects.create_user(
            username='test_inspector',
            password='test123',
            email='inspector@test.com'
        )

        # Create customer
        self.customer = Customer.objects.create(
            name="Test Customer",
            city="Chicago",
            state="IL"
        )

        # Create vehicle
        self.vehicle = Vehicle.objects.create(
            customer=self.customer,
            vin="1HGCM82633A123456",
            year=2020,
            make="Ford",
            model="F-350"
        )

        # Create department
        self.department = Department.objects.create(
            name="Service Department",
            code="SVC"
        )

        # Create completed inspection
        self.inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            template_snapshot={'modules': [], 'metadata': {}}
        )

        # Create OPEN defects
        self.defect1 = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('defect_1'),
            module_key='hydraulics',
            step_key='hose_check',
            severity='CRITICAL',
            status='OPEN',
            title='Damaged Hydraulic Hose',
            description='Hose shows cracking',
            defect_details={'location': 'LEFT_BOOM'}
        )

        self.defect2 = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('defect_2'),
            module_key='hydraulics',
            step_key='pump_check',
            severity='MAJOR',
            status='OPEN',
            title='Hydraulic Pump Leak',
            description='Small leak at pump seal',
            defect_details={'location': 'LEFT_BOOM'}
        )

        self.defect3 = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=make_defect_identity('defect_3'),
            module_key='electrical',
            step_key='light_check',
            severity='MINOR',
            status='OPEN',
            title='Broken Work Light',
            description='Light does not illuminate',
            defect_details={'location': 'RIGHT_BOOM'}
        )

        # Create client and authenticate
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_work_orders_from_all_defects(self):
        """Test creating work orders from all OPEN defects."""
        url = f'/api/inspections/{self.inspection.id}/create_work_orders/'

        response = self.client.post(url, {
            'department_id': str(self.department.id),
            'group_by_location': False
        }, format='json')

        if response.status_code != status.HTTP_200_OK:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('created_work_orders', response.data)
        self.assertIn('total_work_orders', response.data)
        self.assertIn('total_defects_processed', response.data)

        # Should create 3 work orders (one per defect)
        self.assertEqual(response.data['total_work_orders'], 3)
        self.assertEqual(response.data['total_defects_processed'], 3)

        # Verify work orders created
        self.assertEqual(WorkOrder.objects.count(), 3)

    def test_create_work_orders_from_specific_defects(self):
        """Test creating work orders from specific defect IDs."""
        url = f'/api/inspections/{self.inspection.id}/create_work_orders/'

        response = self.client.post(url, {
            'defect_ids': [str(self.defect1.id), str(self.defect2.id)],
            'department_id': str(self.department.id),
            'group_by_location': False
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should create 2 work orders
        self.assertEqual(response.data['total_work_orders'], 2)
        self.assertEqual(response.data['total_defects_processed'], 2)

        # Verify work orders created
        self.assertEqual(WorkOrder.objects.count(), 2)

    def test_create_work_orders_grouped_by_location(self):
        """Test creating work orders grouped by location."""
        url = f'/api/inspections/{self.inspection.id}/create_work_orders/'

        response = self.client.post(url, {
            'department_id': str(self.department.id),
            'group_by_location': True
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should create 2 work orders (LEFT_BOOM + RIGHT_BOOM)
        self.assertEqual(response.data['total_work_orders'], 2)
        self.assertEqual(response.data['total_defects_processed'], 3)

        # Verify work orders created
        self.assertEqual(WorkOrder.objects.count(), 2)

    def test_create_work_orders_with_auto_approve(self):
        """Test creating work orders with auto-approval."""
        url = f'/api/inspections/{self.inspection.id}/create_work_orders/'

        response = self.client.post(url, {
            'department_id': str(self.department.id),
            'auto_approve': True
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify all work orders are approved
        for wo in WorkOrder.objects.all():
            self.assertEqual(wo.approval_status, 'APPROVED')

    def test_cannot_create_work_orders_from_incomplete_inspection(self):
        """Test validation: inspection must be COMPLETED."""
        # Create in-progress inspection
        incomplete_inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_inspection',
            status='IN_PROGRESS',
            started_at=timezone.now(),
            template_snapshot={'modules': [], 'metadata': {}}
        )

        url = f'/api/inspections/{incomplete_inspection.id}/create_work_orders/'

        response = self.client.post(url, {
            'department_id': str(self.department.id)
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Inspection must be finalized', str(response.data))

    def test_cannot_create_work_orders_with_invalid_department(self):
        """Test validation: department must exist."""
        url = f'/api/inspections/{self.inspection.id}/create_work_orders/'

        response = self.client.post(url, {
            'department_id': 'invalid-uuid-12345'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_work_orders_with_invalid_defect_ids(self):
        """Test validation: defect IDs must belong to inspection."""
        url = f'/api/inspections/{self.inspection.id}/create_work_orders/'

        # Create defect from different inspection
        other_inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            template_snapshot={'modules': [], 'metadata': {}}
        )

        other_defect = InspectionDefect.objects.create(
            inspection_run=other_inspection,
            defect_identity=make_defect_identity('other_defect'),
            step_key='test_step',
            severity='MINOR',
            status='OPEN',
            title='Other Defect',
            description='From different inspection'
        )

        response = self.client.post(url, {
            'defect_ids': [str(other_defect.id)],
            'department_id': str(self.department.id)
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('do not belong to this inspection', str(response.data))

    def test_cannot_create_work_orders_from_closed_defects(self):
        """Test validation: at least one defect must be OPEN."""
        # Close all defects
        InspectionDefect.objects.filter(
            inspection_run=self.inspection
        ).update(status='RESOLVED')

        url = f'/api/inspections/{self.inspection.id}/create_work_orders/'

        response = self.client.post(url, {
            'department_id': str(self.department.id)
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No OPEN defects', str(response.data))

    def test_work_order_response_format(self):
        """Test response format matches specification."""
        url = f'/api/inspections/{self.inspection.id}/create_work_orders/'

        response = self.client.post(url, {
            'department_id': str(self.department.id),
            'group_by_location': False
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate response structure
        self.assertIn('created_work_orders', response.data)
        self.assertIn('total_work_orders', response.data)
        self.assertIn('total_defects_processed', response.data)

        # Validate work order summary structure
        for wo_summary in response.data['created_work_orders']:
            self.assertIn('id', wo_summary)
            self.assertIn('work_order_number', wo_summary)
            self.assertIn('title', wo_summary)
            self.assertIn('priority', wo_summary)
            self.assertIn('line_count', wo_summary)
            self.assertIn('defect_count', wo_summary)

    def test_defects_linked_to_work_orders(self):
        """Test defects are properly linked to work orders."""
        url = f'/api/inspections/{self.inspection.id}/create_work_orders/'

        response = self.client.post(url, {
            'department_id': str(self.department.id),
            'group_by_location': False
        }, format='json')

        if response.status_code != status.HTTP_200_OK:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify work orders link back to defects via source_id
        # Each defect should have a corresponding work order with source_type='INSPECTION_DEFECT'
        wo_for_defect1 = WorkOrder.objects.filter(
            source_type='INSPECTION_DEFECT',
            source_id=self.defect1.id
        ).first()
        self.assertIsNotNone(wo_for_defect1)

    def test_department_id_required(self):
        """Test department_id is required."""
        url = f'/api/inspections/{self.inspection.id}/create_work_orders/'

        response = self.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('department_id', str(response.data))

    def test_authentication_required(self):
        """Test endpoint requires authentication."""
        # Unauthenticated client
        unauthenticated_client = APIClient()

        url = f'/api/inspections/{self.inspection.id}/create_work_orders/'

        response = unauthenticated_client.post(url, {
            'department_id': str(self.department.id)
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inspection_not_found(self):
        """Test 404 for non-existent inspection."""
        url = '/api/inspections/00000000-0000-0000-0000-000000000000/create_work_orders/'

        response = self.client.post(url, {
            'department_id': str(self.department.id)
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
