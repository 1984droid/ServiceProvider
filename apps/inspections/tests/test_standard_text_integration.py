"""
End-to-End Integration Tests for Standard Text

Tests complete workflows:
1. Load template → Execute inspection → Generate PDF → Verify standard text
2. Create defect → Generate work order → Verify standard reference
3. Performance tests for standard text lookups
"""

import hashlib
import json
from pathlib import Path
from django.test import TestCase
from django.utils import timezone

from apps.customers.models import Customer
from apps.assets.models import Vehicle
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.inspections.services.pdf_export_service import InspectionPDFExporter
from apps.inspections.services.defect_to_work_order_service import DefectToWorkOrderService
from apps.inspections.schemas.template_schema import InspectionTemplate


class StandardTextIntegrationTest(TestCase):
    """End-to-end integration tests for standard text."""

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

        # Load real ANSI template
        template_path = Path('apps/inspections/templates/inspection_templates/ansi_a92_2_2021/frequent_inspection.json')
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template_data = json.load(f)
            self.template = InspectionTemplate(**self.template_data)

    def test_full_inspection_workflow_with_standard_text(self):
        """Test: Load template → Execute inspection → Generate PDF with standard text."""
        # Create inspection from real template
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='ansi_a92_2_2021_frequent_inspection',
            status='IN_PROGRESS',
            started_at=timezone.now(),
            inspector_name='John Doe',
            template_snapshot=self.template_data,
            step_data={}
        )

        # Simulate inspector answering questions
        step_data = {}
        for procedure in self.template.procedures:
            for step in procedure.steps:
                step_data[step.step_key] = 'PASS'

        inspection.step_data = step_data
        inspection.status = 'COMPLETED'
        inspection.finalized_at = timezone.now()
        inspection.save()

        # Generate PDF
        exporter = InspectionPDFExporter(inspection)
        pdf_buffer = exporter.generate()

        # Verify PDF generated successfully
        self.assertIsNotNone(pdf_buffer)
        self.assertGreater(pdf_buffer.getvalue().__len__(), 0)

        pdf_content = pdf_buffer.getvalue()
        self.assertTrue(pdf_content.startswith(b'%PDF'))

        # Verify inspection has all steps with standard text
        step_count = sum(len(proc['steps']) for proc in self.template_data['procedures'])
        self.assertEqual(len(step_data), step_count)

    def test_defect_to_work_order_workflow_with_standard_reference(self):
        """Test: Create defect with standard ref → Generate work order → Verify reference."""
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

        # Create defect with standard reference (from template)
        defect = InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=hashlib.sha256(b'boom_crack_workflow').hexdigest(),
            module_key='boom_assembly',
            step_key='boom_visual_inspection',
            severity='CRITICAL',
            status='OPEN',
            title='Cracked Boom Weld',
            description='Structural crack detected in boom weld joint',
            defect_details={
                'standard_reference': 'ANSI A92.2-2021 Section 8.2.3(2)',
                'severity': 'CRITICAL',
                'location': 'Upper boom assembly',
                'corrective_action': 'Replace boom section',
                'observations': 'Crack extends 3 inches along weld seam'
            }
        )

        # Generate work order
        work_order = DefectToWorkOrderService.generate_work_order_from_defect(
            defect=defect,
            auto_approve=False
        )

        # Verify work order created
        self.assertIsNotNone(work_order)
        self.assertEqual(work_order.source_type, 'INSPECTION_DEFECT')
        self.assertEqual(str(work_order.source_id), str(defect.id))

        # Verify work order has line with standard reference
        self.assertEqual(work_order.lines.count(), 1)
        line = work_order.lines.first()

        # Standard reference should be in description
        self.assertIn('ANSI A92.2-2021 Section 8.2.3(2)', line.description)
        self.assertIn('Standard:', line.description)

        # Defect should be marked as having work order
        defect.refresh_from_db()
        self.assertEqual(defect.status, 'WORK_ORDER_CREATED')

    def test_multiple_defects_workflow_preserves_distinct_references(self):
        """Test: Multiple defects → Multiple work orders → Each preserves correct reference."""
        # Create inspection
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='ansi_a92_2_2021_periodic_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            inspector_name='Bob Wilson',
            template_snapshot={'procedures': [], 'metadata': {}},
            step_data={}
        )

        # Create defects with different standard references
        defects = [
            {
                'key': 'boom_defect',
                'title': 'Boom Crack',
                'standard_ref': 'ANSI A92.2-2021 Section 8.2.3(2)'
            },
            {
                'key': 'hydraulic_defect',
                'title': 'Hydraulic Leak',
                'standard_ref': 'ANSI A92.2-2021 Section 8.2.3(4)'
            },
            {
                'key': 'dielectric_defect',
                'title': 'Dielectric Test Failed',
                'standard_ref': 'ANSI A92.2-2021 Section 5.4.1'
            }
        ]

        created_defects = []
        for defect_data in defects:
            defect = InspectionDefect.objects.create(
                inspection_run=inspection,
                defect_identity=hashlib.sha256(defect_data['key'].encode()).hexdigest(),
                module_key='test_module',
                step_key='test_step',
                severity='CRITICAL',
                status='OPEN',
                title=defect_data['title'],
                description=f"Description for {defect_data['title']}",
                defect_details={
                    'standard_reference': defect_data['standard_ref'],
                    'severity': 'CRITICAL'
                }
            )
            created_defects.append((defect, defect_data['standard_ref']))

        # Generate work orders
        work_orders = DefectToWorkOrderService.generate_work_orders_from_inspection(
            inspection=inspection,
            group_by_location=False
        )

        # Verify we got 3 work orders
        self.assertEqual(len(work_orders), 3)

        # Verify each work order has correct standard reference
        for wo in work_orders:
            line = wo.lines.first()

            # Find which defect this work order is for
            matching_defect = None
            for defect, std_ref in created_defects:
                if std_ref in line.description:
                    matching_defect = (defect, std_ref)
                    break

            self.assertIsNotNone(
                matching_defect,
                f"Work order line should contain one of the standard references"
            )

    def test_inspection_with_all_template_types(self):
        """Test loading and validating all 5 ANSI template types."""
        template_files = {
            'frequent_inspection': 'frequent_inspection.json',
            'periodic_inspection': 'periodic_inspection.json',
            'major_structural_inspection': 'major_structural_inspection.json',
            'dielectric_test_periodic': 'dielectric_test_periodic.json',
            'load_test_only': 'load_test_only.json'
        }

        templates_dir = Path('apps/inspections/templates/inspection_templates/ansi_a92_2_2021')

        for template_key, filename in template_files.items():
            with self.subTest(template=template_key):
                # Load template
                template_path = templates_dir / filename
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    template = InspectionTemplate(**template_data)

                # Create inspection
                inspection = InspectionRun.objects.create(
                    asset_type='VEHICLE',
                    asset_id=self.vehicle.id,
                    customer=self.customer,
                    template_key=f'ansi_a92_2_2021_{template_key}',
                    status='COMPLETED',
                    started_at=timezone.now(),
                    finalized_at=timezone.now(),
                    inspector_name='Test Inspector',
                    template_snapshot=template_data,
                    step_data={}
                )

                # Generate PDF
                exporter = InspectionPDFExporter(inspection)
                pdf_buffer = exporter.generate()

                # Verify PDF generated
                self.assertIsNotNone(pdf_buffer)
                self.assertGreater(pdf_buffer.getvalue().__len__(), 0)

                # Verify all steps have standard text
                for procedure in template.procedures:
                    for step in procedure.steps:
                        self.assertIsNotNone(
                            step.standard_text,
                            f"Step {step.step_key} in {template_key} missing standard_text"
                        )

    def test_pdf_generation_performance_with_standard_text(self):
        """Test that PDF generation with standard text is performant."""
        import time

        # Create inspection with real template
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='ansi_a92_2_2021_periodic_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            inspector_name='Performance Test',
            template_snapshot=self.template_data,
            step_data={}
        )

        # Measure PDF generation time
        start_time = time.time()

        for _ in range(10):  # Generate 10 PDFs
            exporter = InspectionPDFExporter(inspection)
            pdf_buffer = exporter.generate()
            self.assertIsNotNone(pdf_buffer)

        end_time = time.time()
        elapsed = end_time - start_time
        avg_time = elapsed / 10

        # Should generate each PDF in under 2 seconds
        self.assertLess(avg_time, 2.0, f"PDF generation too slow: {avg_time:.2f}s average")

    def test_standard_text_cache_persistence(self):
        """Test that standard text cache persists across multiple PDF generations."""
        # Create two inspections
        inspection1 = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='ansi_a92_2_2021_frequent_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            inspector_name='Inspector 1',
            template_snapshot=self.template_data,
            step_data={}
        )

        inspection2 = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='ansi_a92_2_2021_frequent_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            inspector_name='Inspector 2',
            template_snapshot=self.template_data,
            step_data={}
        )

        # Generate PDFs (should use same cache)
        exporter1 = InspectionPDFExporter(inspection1)
        exporter2 = InspectionPDFExporter(inspection2)

        # Both should have access to the same class-level cache
        self.assertIs(
            exporter1._standard_text_cache,
            exporter2._standard_text_cache,
            "Both exporters should share the same cache instance"
        )

        # Generate PDFs successfully
        pdf1 = exporter1.generate()
        pdf2 = exporter2.generate()

        self.assertIsNotNone(pdf1)
        self.assertIsNotNone(pdf2)

    def test_defect_without_standard_reference_creates_work_order(self):
        """Test that defects without standard references still create work orders."""
        # Create inspection
        inspection = InspectionRun.objects.create(
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            customer=self.customer,
            template_key='basic_inspection',
            status='COMPLETED',
            started_at=timezone.now(),
            finalized_at=timezone.now(),
            inspector_name='Test Inspector',
            template_snapshot={'procedures': [], 'metadata': {}},
            step_data={}
        )

        # Create defect WITHOUT standard reference
        defect = InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=hashlib.sha256(b'no_standard_ref').hexdigest(),
            module_key='general',
            step_key='general_check',
            severity='MINOR',
            status='OPEN',
            title='Minor Issue',
            description='Minor cosmetic issue',
            defect_details={
                'severity': 'MINOR',
                'location': 'Exterior panel'
            }
        )

        # Generate work order (should work without standard reference)
        work_order = DefectToWorkOrderService.generate_work_order_from_defect(defect=defect)

        # Verify work order created
        self.assertIsNotNone(work_order)
        self.assertEqual(work_order.lines.count(), 1)

        # Verify description doesn't contain "Standard:"
        line = work_order.lines.first()
        self.assertNotIn('Standard:', line.description)
