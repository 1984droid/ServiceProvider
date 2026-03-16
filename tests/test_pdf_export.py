"""
Tests for PDF Export Service
"""

import hashlib
import json
from pathlib import Path
from unittest.mock import patch, mock_open
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


class PDFStandardTextIntegrationTest(TestCase):
    """Test PDF export with ANSI standard text integration."""

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

        # Mock standard text data
        self.mock_standard_text = {
            "standard": "ANSI A92.2-2021",
            "common_excerpts": {
                "boom_inspection": {
                    "section": "8.2.3(2)",
                    "excerpt": "Inspect boom and platform for visible defects such as cracks, damage, excessive wear, and loose or missing bolts."
                },
                "hydraulic_inspection": {
                    "section": "8.2.3(4)",
                    "excerpt": "Inspect hydraulic system for leaks, damaged hoses, and proper fluid levels."
                },
                "load_test_general": {
                    "section": "8.2.4.1",
                    "excerpt": "Perform a load test of one and one-half times the rated load capacity in accordance with Section 4.5.1 Stability on Level Surface Test."
                }
            }
        }

    def test_standard_text_cache_loading(self):
        """Test that standard text cache loads correctly."""
        mock_json = json.dumps(self.mock_standard_text)

        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_json)):

            # Reset cache
            InspectionPDFExporter._standard_text_cache = None

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
                step_data={}
            )

            # Create exporter (should load cache)
            exporter = InspectionPDFExporter(inspection)

            # Verify cache was populated
            self.assertIsNotNone(InspectionPDFExporter._standard_text_cache)
            self.assertEqual(len(InspectionPDFExporter._standard_text_cache), 3)
            self.assertIn('8.2.3(2)', InspectionPDFExporter._standard_text_cache)
            self.assertIn('8.2.3(4)', InspectionPDFExporter._standard_text_cache)
            self.assertIn('8.2.4.1', InspectionPDFExporter._standard_text_cache)

    def test_standard_text_cache_missing_file(self):
        """Test graceful handling when standard text file is missing."""
        with patch('pathlib.Path.exists', return_value=False):
            # Reset cache
            InspectionPDFExporter._standard_text_cache = None

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
                step_data={}
            )

            # Create exporter (should handle missing file)
            exporter = InspectionPDFExporter(inspection)

            # Verify cache is empty dict (not None)
            self.assertIsNotNone(InspectionPDFExporter._standard_text_cache)
            self.assertEqual(len(InspectionPDFExporter._standard_text_cache), 0)

    def test_standard_text_lookup_exact_match(self):
        """Test looking up standard text with exact section match."""
        mock_json = json.dumps(self.mock_standard_text)

        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_json)):

            # Reset cache
            InspectionPDFExporter._standard_text_cache = None

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
                step_data={}
            )

            exporter = InspectionPDFExporter(inspection)

            # Test exact match
            excerpt = exporter._get_standard_text_for_reference("ANSI A92.2-2021 Section 8.2.3(2)")
            self.assertIsNotNone(excerpt)
            self.assertIn("Inspect boom and platform", excerpt)

    def test_standard_text_lookup_partial_match(self):
        """Test looking up standard text with partial section match."""
        mock_json = json.dumps(self.mock_standard_text)

        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_json)):

            # Reset cache
            InspectionPDFExporter._standard_text_cache = None

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
                step_data={}
            )

            exporter = InspectionPDFExporter(inspection)

            # Test partial match (should find 8.2.3(4) in "8.2.3(4)")
            excerpt = exporter._get_standard_text_for_reference("Section 8.2.3(4)")
            self.assertIsNotNone(excerpt)
            self.assertIn("hydraulic system", excerpt)

    def test_standard_text_lookup_no_match(self):
        """Test looking up standard text with no match."""
        mock_json = json.dumps(self.mock_standard_text)

        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_json)):

            # Reset cache
            InspectionPDFExporter._standard_text_cache = None

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
                step_data={}
            )

            exporter = InspectionPDFExporter(inspection)

            # Test no match
            excerpt = exporter._get_standard_text_for_reference("Section 99.99.99")
            self.assertIsNone(excerpt)

    def test_standard_text_truncation(self):
        """Test that long excerpts are truncated to 150 characters."""
        long_excerpt_data = {
            "standard": "ANSI A92.2-2021",
            "common_excerpts": {
                "long_text": {
                    "section": "1.1",
                    "excerpt": "A" * 200  # 200 character excerpt
                }
            }
        }

        mock_json = json.dumps(long_excerpt_data)

        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_json)):

            # Reset cache
            InspectionPDFExporter._standard_text_cache = None

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
                step_data={}
            )

            exporter = InspectionPDFExporter(inspection)

            # Test truncation
            excerpt = exporter._get_standard_text_for_reference("Section 1.1")
            self.assertIsNotNone(excerpt)
            self.assertEqual(len(excerpt), 150)  # 147 + '...'
            self.assertTrue(excerpt.endswith('...'))

    def test_pdf_with_standard_text_in_defects(self):
        """Test PDF generation includes standard text in defect details."""
        mock_json = json.dumps(self.mock_standard_text)

        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_json)):

            # Reset cache
            InspectionPDFExporter._standard_text_cache = None

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
                template_snapshot={'modules': [], 'metadata': {}},
                step_data={}
            )

            # Create defect with standard reference
            InspectionDefect.objects.create(
                inspection_run=inspection,
                defect_identity=hashlib.sha256(b'boom_defect').hexdigest(),
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

            # Verify PDF was generated
            self.assertIsNotNone(pdf_buffer)
            self.assertGreater(pdf_buffer.getvalue().__len__(), 0)

            # Verify it starts with PDF header
            pdf_content = pdf_buffer.getvalue()
            self.assertTrue(pdf_content.startswith(b'%PDF'))

    def test_pdf_generation_without_standard_text(self):
        """Test PDF generation works when standard text is unavailable."""
        with patch('pathlib.Path.exists', return_value=False):
            # Reset cache
            InspectionPDFExporter._standard_text_cache = None

            # Create inspection
            inspection = InspectionRun.objects.create(
                asset_type='VEHICLE',
                asset_id=self.vehicle.id,
                customer=self.customer,
                template_key='ansi_a92_2_2021_periodic_inspection',
                status='COMPLETED',
                started_at=timezone.now(),
                finalized_at=timezone.now(),
                inspector_name='John Doe',
                template_snapshot={'modules': [], 'metadata': {}},
                step_data={}
            )

            # Create defect with standard reference
            InspectionDefect.objects.create(
                inspection_run=inspection,
                defect_identity=hashlib.sha256(b'defect').hexdigest(),
                module_key='hydraulic_system',
                step_key='hose_inspection',
                severity='MAJOR',
                status='OPEN',
                title='Hydraulic Leak',
                description='Leak detected in main hydraulic line',
                defect_details={
                    'standard_reference': 'ANSI A92.2-2021 Section 8.2.3(4)',
                    'severity': 'MAJOR'
                }
            )

            # Generate PDF (should work without standard text)
            exporter = InspectionPDFExporter(inspection)
            pdf_buffer = exporter.generate()

            # Verify PDF was generated
            self.assertIsNotNone(pdf_buffer)
            self.assertGreater(pdf_buffer.getvalue().__len__(), 0)

            # Verify it starts with PDF header
            pdf_content = pdf_buffer.getvalue()
            self.assertTrue(pdf_content.startswith(b'%PDF'))


class PDFPhotoEmbeddingTest(TestCase):
    """Test PDF generation with photo embedding."""

    def setUp(self):
        """Set up test fixtures."""
        from PIL import Image as PILImage
        import os
        from django.conf import settings

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
            unit_number="TEST-001",
            year=2020,
            make="Ford",
            model="F-350"
        )

        # Create inspection
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

        # Create defect
        self.defect = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=hashlib.sha256(b'test_photo_defect').hexdigest(),
            step_key='visual_inspection',
            severity='CRITICAL',
            status='OPEN',
            title='Hydraulic Leak with Photo Evidence',
            description='Leak detected on boom cylinder',
            defect_details={'location': 'BOOM'}
        )

        # Create test image files for photos
        self.test_images = []
        media_root = Path(settings.MEDIA_ROOT)
        test_photo_dir = media_root / 'test_photos'
        test_photo_dir.mkdir(parents=True, exist_ok=True)

        for i in range(3):
            # Create a small test image
            img = PILImage.new('RGB', (300, 300), color=(100 + i*50, 150, 200))
            img_path = test_photo_dir / f'test_photo_{i}.jpg'
            img.save(img_path, 'JPEG')
            self.test_images.append(img_path)

    def tearDown(self):
        """Clean up test files."""
        import shutil
        from django.conf import settings

        # Remove test photos
        test_photo_dir = Path(settings.MEDIA_ROOT) / 'test_photos'
        if test_photo_dir.exists():
            shutil.rmtree(test_photo_dir)

    def test_pdf_with_embedded_photos(self):
        """Test PDF generation includes embedded photo thumbnails."""
        from apps.inspections.models import InspectionPhoto
        from django.core.files import File

        # Add photos to defect
        for i, img_path in enumerate(self.test_images):
            with open(img_path, 'rb') as f:
                photo = InspectionPhoto.objects.create(
                    inspection=self.inspection,
                    defect=self.defect,
                    step_key='visual_inspection',
                    image=File(f, name=f'test_photo_{i}.jpg'),
                    caption=f'Photo {i+1} of hydraulic leak'
                )

        # Generate PDF
        exporter = InspectionPDFExporter(self.inspection)
        pdf_buffer = exporter.generate()

        # Verify PDF was generated
        self.assertIsNotNone(pdf_buffer)
        pdf_content = pdf_buffer.getvalue()
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))

        # Verify PDF is larger than one without photos (photos add content)
        # Create a baseline inspection without photos
        inspection_no_photos = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='test_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            template_snapshot={'modules': [], 'metadata': {}}
        )

        InspectionDefect.objects.create(
            inspection_run=inspection_no_photos,
            defect_identity=hashlib.sha256(b'test_no_photo').hexdigest(),
            step_key='visual_inspection',
            severity='CRITICAL',
            status='OPEN',
            title='Defect without photos',
            description='No photo evidence'
        )

        exporter_no_photos = InspectionPDFExporter(inspection_no_photos)
        pdf_no_photos = exporter_no_photos.generate()

        # PDF with photos should be larger
        self.assertGreater(len(pdf_content), len(pdf_no_photos.getvalue()))

    def test_pdf_without_photos(self):
        """Test PDF generation works normally when defect has no photos."""
        # Generate PDF (defect has no photos)
        exporter = InspectionPDFExporter(self.inspection)
        pdf_buffer = exporter.generate()

        # Verify PDF was generated
        self.assertIsNotNone(pdf_buffer)
        self.assertGreater(len(pdf_buffer.getvalue()), 0)
        self.assertTrue(pdf_buffer.getvalue().startswith(b'%PDF'))
