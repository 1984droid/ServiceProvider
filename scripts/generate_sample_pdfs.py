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

    # 1. Minimal inspection (no defects)
    print("1. Creating minimal inspection PDF...")
    inspection1 = InspectionRun.objects.create(
        asset_type='VEHICLE',
        asset_id=vehicle.id,
        customer=customer,
        template_key='ansi_a92_2_annual',
        status='COMPLETED',
        started_at=timezone.now(),
        finalized_at=timezone.now(),
        inspector_name='John Smith',
        template_snapshot={'modules': [], 'metadata': {}},
        step_data={}
    )

    exporter = InspectionPDFExporter(inspection1)
    pdf_buffer = exporter.generate()
    filepath = os.path.join(output_dir, f"01_minimal_{inspection1.id}.pdf")
    with open(filepath, 'wb') as f:
        f.write(pdf_buffer.getvalue())
    print(f"   OK Created: {os.path.basename(filepath)}")

    # 2. Inspection with CRITICAL defects
    print("2. Creating inspection with CRITICAL defects PDF...")
    inspection2 = InspectionRun.objects.create(
        asset_type='EQUIPMENT',
        asset_id=equipment.id,
        customer=customer,
        template_key='ansi_a92_2_annual',
        status='COMPLETED',
        started_at=timezone.now(),
        finalized_at=timezone.now(),
        inspector_name='Sarah Johnson',
        template_snapshot={'modules': [], 'metadata': {}},
        step_data={}
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

    # 3. Inspection with mixed severity defects
    print("3. Creating inspection with mixed defects PDF...")
    inspection3 = InspectionRun.objects.create(
        asset_type='EQUIPMENT',
        asset_id=equipment.id,
        customer=customer,
        template_key='ansi_a92_2_annual',
        status='COMPLETED',
        started_at=timezone.now(),
        finalized_at=timezone.now(),
        inspector_name='Mike Davis',
        template_snapshot={'modules': [], 'metadata': {}},
        step_data={}
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
    print(f"📁 Location: {output_dir}\n")
    for f in sorted(files):
        size = os.path.getsize(os.path.join(output_dir, f)) / 1024
        print(f"   📄 {f} ({size:.1f} KB)")
    print()


if __name__ == '__main__':
    main()
