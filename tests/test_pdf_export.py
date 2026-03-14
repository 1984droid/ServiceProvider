"""
Tests for PDF Export Service
"""

import hashlib
from django.test import TestCase
from django.utils import timezone

from apps.customers.models import Customer
from apps.assets.models import Vehicle
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.inspections.services.pdf_export_service import InspectionPDFExporter


class PDFExportTest(TestCase):
    """Test PDF export functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create customer
        self.customer = Customer.objects.create(
            name="Test Fleet Company",
            city="Chicago",
            state="IL"
        )

        # Create vehicle
        self.vehicle = Vehicle.objects.create(
            customer=self.customer,
            vin="1HGCM82633A123456",
            unit_number="TRUCK-001",
            year=2020,
            make="Ford",
            model="F-350"
        )

    def test_generate_basic_pdf(self):
        """Test generating PDF for basic inspection."""
        # Create inspection
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            inspector_name='John Doe',
            template_snapshot={'modules': [], 'metadata': {}},
            step_data={'test_step': 'pass'}
        )

        # Generate PDF
        exporter = InspectionPDFExporter(inspection)
        pdf_buffer = exporter.generate()

        # Verify PDF was generated
        self.assertIsNotNone(pdf_buffer)
        self.assertGreater(pdf_buffer.getvalue().__len__(), 0)

        # Verify it starts with PDF header
        pdf_content = pdf_buffer.getvalue()
        self.assertTrue(pdf_content.startswith(b'%PDF'))

    def test_generate_pdf_with_defects(self):
        """Test generating PDF with defects."""
        # Create inspection
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='ansi_a92_2_2021_annual_aerial_vehicle',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            inspector_name='Jane Smith',
            template_snapshot={'modules': [], 'metadata': {}},
            step_data={}
        )

        # Create defects with different severities
        InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=hashlib.sha256(b'critical_defect').hexdigest(),
            module_key='hydraulic_system',
            step_key='hose_inspection',
            severity='CRITICAL',
            status='OPEN',
            title='Damaged Hydraulic Hose',
            description='Severe wear detected on main hydraulic line'
        )

        InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=hashlib.sha256(b'minor_defect').hexdigest(),
            module_key='boom_assembly',
            step_key='visual_inspection',
            severity='MINOR',
            status='OPEN',
            title='Paint Chipping',
            description='Minor paint damage on boom assembly'
        )

        # Generate PDF
        exporter = InspectionPDFExporter(inspection)
        pdf_buffer = exporter.generate()

        # Verify PDF was generated
        self.assertIsNotNone(pdf_buffer)
        self.assertGreater(pdf_buffer.getvalue().__len__(), 0)

        # Verify it starts with PDF header
        pdf_content = pdf_buffer.getvalue()
        self.assertTrue(pdf_content.startswith(b'%PDF'))

    def test_generate_pdf_for_equipment(self):
        """Test generating PDF for equipment inspection."""
        from apps.assets.models import Equipment

        # Create equipment
        equipment = Equipment.objects.create(
            customer=self.customer,
            serial_number='EQ-123456',
            asset_number='AER-001',
            equipment_type='A92_2_AERIAL',
            manufacturer='Altec',
            model='AT40G'
        )

        # Create inspection
        inspection = InspectionRun.objects.create(
            asset_type='EQUIPMENT',
            asset_id=equipment.id,
            customer=self.customer,
            template_key='ansi_a92_2_2021_annual_aerial_device',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            inspector_name='Bob Wilson',
            template_snapshot={'modules': [], 'metadata': {}},
            step_data={}
        )

        # Generate PDF
        exporter = InspectionPDFExporter(inspection)
        pdf_buffer = exporter.generate()

        # Verify PDF was generated
        self.assertIsNotNone(pdf_buffer)
        self.assertGreater(pdf_buffer.getvalue().__len__(), 0)

        # Verify it starts with PDF header
        pdf_content = pdf_buffer.getvalue()
        self.assertTrue(pdf_content.startswith(b'%PDF'))
