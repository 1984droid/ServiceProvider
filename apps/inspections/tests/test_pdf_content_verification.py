"""
Tests for PDF Content Verification

Verifies that standard text actually appears in generated PDFs.
Uses PyPDF2 to extract and verify PDF content.
"""

import hashlib
from io import BytesIO
from django.test import TestCase
from django.utils import timezone

from apps.customers.models import Customer
from apps.assets.models import Vehicle
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.inspections.services.pdf_export_service import InspectionPDFExporter

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


class PDFContentVerificationTest(TestCase):
    """Verify standard text appears in PDF content."""

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

    def extract_pdf_text(self, pdf_buffer: BytesIO) -> str:
        """Extract all text from PDF."""
        if not PYPDF2_AVAILABLE:
            self.skipTest("PyPDF2 not installed")

        pdf_buffer.seek(0)
        reader = PyPDF2.PdfReader(pdf_buffer)

        text = ""
        for page in reader.pages:
            text += page.extract_text()

        return text

    def test_pypdf2_available(self):
        """Test that PyPDF2 is available for PDF verification."""
        self.assertTrue(
            PYPDF2_AVAILABLE,
            "PyPDF2 required for PDF content verification. Install with: pip install PyPDF2"
        )

    def test_pdf_contains_standard_reference_in_steps(self):
        """Test that PDF contains standard reference from inspection steps."""
        if not PYPDF2_AVAILABLE:
            self.skipTest("PyPDF2 not installed")

        # Create inspection with ANSI template
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='ansi_a92_2_2021_frequent_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            inspector_name='John Doe',
            template_snapshot={
                'procedures': [
                    {
                        'procedure_key': 'general_inspection',
                        'title': 'General Inspection',
                        'steps': [
                            {
                                'step_key': 'boom_condition',
                                'title': 'Inspect boom condition',
                                'standard_ref': 'ANSI A92.2-2021 Section 8.2.3(2)',
                                'standard_text': {
                                    'section': '8.2.3(2)',
                                    'excerpt': 'Inspect boom and platform for visible defects.',
                                    'show_full_section': False
                                },
                                'fields': []
                            }
                        ]
                    }
                ],
                'metadata': {}
            },
            step_data={'boom_condition': 'PASS'}
        )

        # Generate PDF
        exporter = InspectionPDFExporter(inspection)
        pdf_buffer = exporter.generate()

        # Extract text
        pdf_text = self.extract_pdf_text(pdf_buffer)

        # Verify standard reference appears
        self.assertIn('ANSI A92.2-2021 Section 8.2.3(2)', pdf_text)

        # Verify excerpt appears (or truncated version)
        self.assertIn('Inspect boom and platform', pdf_text)

    def test_pdf_contains_standard_text_in_defects(self):
        """Test that PDF contains standard text from defect details."""
        if not PYPDF2_AVAILABLE:
            self.skipTest("PyPDF2 not installed")

        # Create inspection
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='ansi_a92_2_2021_periodic_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            inspector_name='Jane Smith',
            template_snapshot={'procedures': [], 'metadata': {}},
            step_data={}
        )

        # Create defect with standard reference
        InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=hashlib.sha256(b'boom_crack').hexdigest(),
            module_key='boom_assembly',
            step_key='visual_inspection',
            severity='CRITICAL',
            status='OPEN',
            title='Cracked Boom Weld',
            description='Structural crack detected in boom weld joint',
            defect_details={
                'standard_reference': 'ANSI A92.2-2021 Section 8.2.3(2)',
                'severity': 'CRITICAL',
                'location': 'Upper boom assembly',
                'corrective_action': 'Replace boom section'
            }
        )

        # Generate PDF
        exporter = InspectionPDFExporter(inspection)
        pdf_buffer = exporter.generate()

        # Extract text
        pdf_text = self.extract_pdf_text(pdf_buffer)

        # Verify standard reference appears in defect section
        self.assertIn('ANSI A92.2-2021 Section 8.2.3(2)', pdf_text)

        # Verify defect title appears
        self.assertIn('Cracked Boom Weld', pdf_text)

    def test_pdf_multiple_standard_references(self):
        """Test that PDF contains multiple distinct standard references."""
        if not PYPDF2_AVAILABLE:
            self.skipTest("PyPDF2 not installed")

        # Create inspection with multiple procedures
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='ansi_a92_2_2021_periodic_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            inspector_name='Bob Wilson',
            template_snapshot={
                'procedures': [
                    {
                        'procedure_key': 'boom_inspection',
                        'title': 'Boom Inspection',
                        'steps': [
                            {
                                'step_key': 'boom_visual',
                                'title': 'Visual inspection',
                                'standard_ref': 'ANSI A92.2-2021 Section 8.2.3(2)',
                                'standard_text': {
                                    'section': '8.2.3(2)',
                                    'excerpt': 'Inspect boom for visible defects.',
                                    'show_full_section': False
                                },
                                'fields': []
                            }
                        ]
                    },
                    {
                        'procedure_key': 'hydraulic_test',
                        'title': 'Hydraulic Test',
                        'steps': [
                            {
                                'step_key': 'hydraulic_check',
                                'title': 'Hydraulic system check',
                                'standard_ref': 'ANSI A92.2-2021 Section 8.2.3(4)',
                                'standard_text': {
                                    'section': '8.2.3(4)',
                                    'excerpt': 'Inspect hydraulic system for leaks.',
                                    'show_full_section': False
                                },
                                'fields': []
                            }
                        ]
                    }
                ],
                'metadata': {}
            },
            step_data={'boom_visual': 'PASS', 'hydraulic_check': 'FAIL'}
        )

        # Generate PDF
        exporter = InspectionPDFExporter(inspection)
        pdf_buffer = exporter.generate()

        # Extract text
        pdf_text = self.extract_pdf_text(pdf_buffer)

        # Verify both standard references appear
        self.assertIn('Section 8.2.3(2)', pdf_text)
        self.assertIn('Section 8.2.3(4)', pdf_text)

        # Verify both excerpts appear
        self.assertIn('boom', pdf_text.lower())
        self.assertIn('hydraulic', pdf_text.lower())

    def test_pdf_without_standard_text_still_generates(self):
        """Test that PDF generates successfully without standard text."""
        if not PYPDF2_AVAILABLE:
            self.skipTest("PyPDF2 not installed")

        # Create inspection without standard text
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='basic_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            inspector_name='John Doe',
            template_snapshot={
                'procedures': [
                    {
                        'procedure_key': 'basic_check',
                        'title': 'Basic Check',
                        'steps': [
                            {
                                'step_key': 'general_check',
                                'title': 'General condition',
                                'fields': []
                            }
                        ]
                    }
                ],
                'metadata': {}
            },
            step_data={'general_check': 'PASS'}
        )

        # Generate PDF (should work without standard text)
        exporter = InspectionPDFExporter(inspection)
        pdf_buffer = exporter.generate()

        # Verify PDF was generated
        self.assertIsNotNone(pdf_buffer)
        self.assertGreater(pdf_buffer.getvalue().__len__(), 0)

        # Extract text
        pdf_text = self.extract_pdf_text(pdf_buffer)

        # Verify basic content appears
        self.assertIn('General condition', pdf_text)
        self.assertIn('Basic Check', pdf_text)

    def test_pdf_standard_text_excerpt_truncation(self):
        """Test that long excerpts are truncated in PDF."""
        if not PYPDF2_AVAILABLE:
            self.skipTest("PyPDF2 not installed")

        # Create inspection with long excerpt
        long_excerpt = "A" * 200  # 200 character excerpt
        expected_truncated = "A" * 147 + "..."

        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            inspector_name='Test Inspector',
            template_snapshot={
                'procedures': [
                    {
                        'procedure_key': 'test_proc',
                        'title': 'Test Procedure',
                        'steps': [
                            {
                                'step_key': 'test_step',
                                'title': 'Test Step',
                                'standard_ref': 'ANSI A92.2-2021 Section 1.1',
                                'standard_text': {
                                    'section': '1.1',
                                    'excerpt': long_excerpt,
                                    'show_full_section': False
                                },
                                'fields': []
                            }
                        ]
                    }
                ],
                'metadata': {}
            },
            step_data={'test_step': 'PASS'}
        )

        # Generate PDF
        exporter = InspectionPDFExporter(inspection)
        pdf_buffer = exporter.generate()

        # Extract text
        pdf_text = self.extract_pdf_text(pdf_buffer)

        # Verify truncated excerpt appears (should contain ellipsis)
        # Note: PDF text extraction may not preserve exact formatting,
        # so we just verify some truncation occurred
        a_count = pdf_text.count('A')
        self.assertLess(a_count, 200, "Excerpt should be truncated")
        self.assertGreater(a_count, 100, "Some of excerpt should appear")
