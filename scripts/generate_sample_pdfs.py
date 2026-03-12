"""
Generate Sample PDF Reports

Run with: python scripts/generate_sample_pdfs.py

Outputs PDFs to temp/pdfs/ for manual review.
"""

import os
import sys
import django
import hashlib
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from apps.customers.models import Customer
from apps.assets.models import Vehicle, Equipment
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.inspections.services.pdf_export_service import InspectionPDFExporter


def main():
    """Generate sample inspection PDFs."""
    # Create output directory
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp', 'pdfs')
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nGenerating sample PDFs in: {output_dir}\n")
    print("=" * 60)

    # Create test customer
    customer, _ = Customer.objects.get_or_create(
        name="Sample Fleet Company",
        defaults={
            'legal_name': "Sample Fleet Company Inc.",
            'city': "Chicago",
            'state': "IL"
        }
    )

    # Create vehicle
    vehicle, _ = Vehicle.objects.get_or_create(
        vin="1FDXE45S08HA86448",
        defaults={
            'customer': customer,
            'unit_number': "TRUCK-001",
            'year': 2023,
            'make': "Ford",
            'model': "F-450",
            'body_type': "AERIAL"
        }
    )

    # Create equipment
    equipment, _ = Equipment.objects.get_or_create(
        serial_number="AT40G-SAMPLE",
        defaults={
            'customer': customer,
            'asset_number': "AER-001",
            'equipment_type': 'AERIAL_DEVICE',
            'manufacturer': "Altec",
            'model': "AT40G",
            'capabilities': ['DIELECTRIC', 'HYDRAULIC']
        }
    )

    # 1. Minimal inspection (no defects) - WITH STEP DATA
    print("1. Creating minimal inspection with step data PDF...")
    inspection1 = InspectionRun.objects.create(
        asset_type='VEHICLE',
        asset_id=vehicle.id,
        customer=customer,
        template_key='ansi_a92_2_annual',
        status='COMPLETED',
        started_at=timezone.now(),
        finalized_at=timezone.now(),
        inspector_name='John Smith',
        template_snapshot={
            'procedure': {
                'steps': [
                    {
                        'step_key': 'visual_inspection',
                        'title': 'Visual Inspection',
                        'type': 'CHECK',
                        'field_type': 'PASS_FAIL'
                    },
                    {
                        'step_key': 'function_test',
                        'title': 'Operational Function Test',
                        'type': 'CHECK',
                        'field_type': 'PASS_FAIL'
                    },
                    {
                        'step_key': 'hydraulic_pressure',
                        'title': 'Hydraulic System Pressure',
                        'type': 'MEASURE',
                        'field_type': 'NUMERIC',
                        'unit': 'PSI'
                    },
                    {
                        'step_key': 'dielectric_test',
                        'title': 'Dielectric Insulation Test',
                        'type': 'TEST',
                        'field_type': 'PASS_FAIL'
                    }
                ]
            },
            'metadata': {
                'template_key': 'ansi_a92_2_annual',
                'version': '2.0.0'
            }
        },
        step_data={
            'visual_inspection': 'PASS',
            'function_test': 'PASS',
            'hydraulic_pressure': {'value': 2850, 'unit': 'PSI'},
            'dielectric_test': 'PASS'
        }
    )

    exporter = InspectionPDFExporter(inspection1)
    pdf_buffer = exporter.generate()
    filepath = os.path.join(output_dir, f"01_minimal_{inspection1.id}.pdf")
    with open(filepath, 'wb') as f:
        f.write(pdf_buffer.getvalue())
    print(f"   OK Created: {os.path.basename(filepath)}")

    # 2. Inspection with CRITICAL defects - WITH FAILED STEPS
    print("2. Creating inspection with CRITICAL defects and failed steps PDF...")
    inspection2 = InspectionRun.objects.create(
        asset_type='EQUIPMENT',
        asset_id=equipment.id,
        customer=customer,
        template_key='ansi_a92_2_annual',
        status='COMPLETED',
        started_at=timezone.now(),
        finalized_at=timezone.now(),
        inspector_name='Sarah Johnson',
        template_snapshot={
            'procedure': {
                'steps': [
                    {
                        'step_key': 'visual_inspection',
                        'title': 'Visual Structural Inspection',
                        'type': 'CHECK',
                        'field_type': 'PASS_FAIL'
                    },
                    {
                        'step_key': 'hose_inspection',
                        'title': 'Hydraulic Hose Condition',
                        'type': 'CHECK',
                        'field_type': 'PASS_FAIL'
                    },
                    {
                        'step_key': 'weld_inspection',
                        'title': 'Structural Weld Integrity',
                        'type': 'CHECK',
                        'field_type': 'PASS_FAIL'
                    },
                    {
                        'step_key': 'safety_systems',
                        'title': 'Safety System Functional Test',
                        'type': 'TEST',
                        'field_type': 'PASS_FAIL'
                    },
                    {
                        'step_key': 'boom_extension',
                        'title': 'Boom Extension Measurement',
                        'type': 'MEASURE',
                        'field_type': 'NUMERIC',
                        'unit': 'feet'
                    }
                ]
            },
            'metadata': {}
        },
        step_data={
            'visual_inspection': 'PASS',
            'hose_inspection': 'FAIL',  # Critical defect
            'weld_inspection': 'FAIL',  # Critical defect
            'safety_systems': 'PASS',
            'boom_extension': {'value': 40, 'unit': 'feet'}
        }
    )

    InspectionDefect.objects.create(
        inspection_run=inspection2,
        defect_identity=hashlib.sha256(b'critical_hydraulic').hexdigest(),
        module_key='hydraulic_system',
        step_key='hose_inspection',
        severity='CRITICAL',
        status='OPEN',
        title='Hydraulic Hose Severely Damaged',
        description='Main hydraulic hose shows severe cracking and fluid leakage.'
    )

    InspectionDefect.objects.create(
        inspection_run=inspection2,
        defect_identity=hashlib.sha256(b'critical_weld').hexdigest(),
        module_key='structural',
        step_key='weld_inspection',
        severity='CRITICAL',
        status='OPEN',
        title='Crack in Main Boom Weld',
        description='Structural crack detected in primary boom weld joint.'
    )

    exporter = InspectionPDFExporter(inspection2)
    pdf_buffer = exporter.generate()
    filepath = os.path.join(output_dir, f"02_critical_defects_{inspection2.id}.pdf")
    with open(filepath, 'wb') as f:
        f.write(pdf_buffer.getvalue())
    print(f"   OK Created: {os.path.basename(filepath)}")

    # 3. Inspection with mixed severity defects - WITH COMPREHENSIVE STEP DATA
    print("3. Creating inspection with comprehensive step data PDF...")
    inspection3 = InspectionRun.objects.create(
        asset_type='EQUIPMENT',
        asset_id=equipment.id,
        customer=customer,
        template_key='ansi_a92_2_annual',
        status='COMPLETED',
        started_at=timezone.now(),
        finalized_at=timezone.now(),
        inspector_name='Mike Davis',
        template_snapshot={
            'procedure': {
                'steps': [
                    {
                        'step_key': 'pre_inspection_setup',
                        'title': 'Pre-Inspection Setup',
                        'type': 'SETUP',
                        'field_type': 'PASS_FAIL'
                    },
                    {
                        'step_key': 'boom_visual',
                        'title': 'Boom Visual Condition',
                        'type': 'CHECK',
                        'field_type': 'PASS_FAIL'
                    },
                    {
                        'step_key': 'hydraulic_pressure',
                        'title': 'Hydraulic System Pressure',
                        'type': 'MEASURE',
                        'field_type': 'NUMERIC',
                        'unit': 'PSI'
                    },
                    {
                        'step_key': 'platform_capacity',
                        'title': 'Platform Rated Capacity',
                        'type': 'MEASURE',
                        'field_type': 'NUMERIC',
                        'unit': 'lbs'
                    },
                    {
                        'step_key': 'dielectric_test_result',
                        'title': 'Dielectric Test Result',
                        'type': 'TEST',
                        'field_type': 'PASS_FAIL'
                    },
                    {
                        'step_key': 'control_panel',
                        'title': 'Control Panel Functionality',
                        'type': 'CHECK',
                        'field_type': 'PASS_FAIL'
                    },
                    {
                        'step_key': 'safety_labels',
                        'title': 'Safety Label Condition',
                        'type': 'CHECK',
                        'field_type': 'PASS_FAIL'
                    },
                    {
                        'step_key': 'load_test',
                        'title': 'Load Test Completion',
                        'type': 'TEST',
                        'field_type': 'PASS_FAIL'
                    },
                    {
                        'step_key': 'next_service_interval',
                        'title': 'Hours Until Next Service',
                        'type': 'INFO',
                        'field_type': 'NUMERIC',
                        'unit': 'hours'
                    }
                ]
            },
            'metadata': {}
        },
        step_data={
            'pre_inspection_setup': 'PASS',
            'boom_visual': 'FAIL',  # Minor paint defect
            'hydraulic_pressure': {'value': 2750, 'unit': 'PSI'},
            'platform_capacity': {'value': 500, 'unit': 'lbs'},
            'dielectric_test_result': 'PASS',
            'control_panel': 'FAIL',  # Major defect
            'safety_labels': 'FAIL',  # Minor defect
            'load_test': 'PASS',
            'next_service_interval': {'value': 150, 'unit': 'hours'}
        }
    )

    defects_data = [
        ('CRITICAL', 'Upper Limit Switch Inoperative', 'safety_systems'),
        ('MAJOR', 'Hydraulic Cylinder Seal Leaking', 'hydraulic_system'),
        ('MAJOR', 'Control Panel Display Intermittent', 'electrical'),
        ('MINOR', 'Paint Chipping on Boom Sections', 'boom_assembly'),
        ('MINOR', 'Worn Safety Decals', 'platform'),
        ('ADVISORY', 'Service Interval Approaching', 'maintenance'),
    ]

    for severity, title, module in defects_data:
        InspectionDefect.objects.create(
            inspection_run=inspection3,
            defect_identity=hashlib.sha256(f"{severity}_{title}".encode()).hexdigest(),
            module_key=module,
            step_key='inspection_step',
            severity=severity,
            status='OPEN',
            title=title,
            description=f"{title} - detailed description here."
        )

    exporter = InspectionPDFExporter(inspection3)
    pdf_buffer = exporter.generate()
    filepath = os.path.join(output_dir, f"03_mixed_severity_{inspection3.id}.pdf")
    with open(filepath, 'wb') as f:
        f.write(pdf_buffer.getvalue())
    print(f"   OK Created: {os.path.basename(filepath)}")

    print("=" * 60)
    files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
    print(f"\nOK Generated {len(files)} PDF files")
    print(f"Location: {output_dir}\n")
    for f in sorted(files):
        size = os.path.getsize(os.path.join(output_dir, f)) / 1024
        print(f"   * {f} ({size:.1f} KB)")
    print()


if __name__ == '__main__':
    main()
