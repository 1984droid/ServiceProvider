#!/usr/bin/env python
"""Test script to validate dielectric template filtering and structure."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.inspections.services.template_filter_service import TemplateFilterService
from apps.assets.models import Equipment

# Find an A92_2_AERIAL equipment
eq = Equipment.objects.filter(equipment_type='A92_2_AERIAL').first()

if not eq:
    print("No A92_2_AERIAL equipment found in database")
    print("Creating test equipment...")
    from apps.customers.models import Customer
    customer = Customer.objects.first()
    if customer:
        eq = Equipment.objects.create(
            equipment_type='A92_2_AERIAL',
            serial_number='TEST-AERIAL-001',
            asset_number='TEST-001',
            customer=customer,
            capabilities=['INSULATING_SYSTEM']
        )
        print(f"Created test equipment: {eq.serial_number}")
    else:
        print("No customer found to create test equipment")
        exit(1)

print(f"\nTesting with equipment: {eq.serial_number}")
print(f"   Type: {eq.equipment_type}")
print(f"   Capabilities: {eq.capabilities}")

# Test template filtering
service = TemplateFilterService()
equipment_dict = {
    'id': str(eq.id),
    'equipment_type': eq.equipment_type,
    'capabilities': eq.capabilities or []
}
templates = service.get_applicable_templates_for_equipment(equipment_dict)

print(f"\nTotal templates for this equipment: {len(templates)}")

# Find dielectric templates
dielectric_templates = [t for t in templates if 'dielectric' in t.get('template_key', '').lower()]

print(f"\nDielectric templates found: {len(dielectric_templates)}")
for t in dielectric_templates:
    print(f"   - {t.get('name')}")
    print(f"     Key: {t.get('template_key')}")
    print(f"     Status: {t.get('status')}")
    print(f"     Required capabilities: {t.get('required_capabilities')}")
    print()

# Specifically check for the new monolithic template
new_template = next(
    (t for t in templates if t.get('template_key') == 'ansi_a92_2_periodic_dielectric_test'),
    None
)

if new_template:
    print("\nSUCCESS: New monolithic dielectric template IS available for this equipment")
    print(f"   Name: {new_template.get('name')}")
    print(f"   Steps: {new_template.get('step_count', 'unknown')}")
    print(f"   Rules: {new_template.get('rule_count', 'unknown')}")
else:
    print("\nERROR: New monolithic dielectric template NOT found in filtered results")
    print("\nChecking if it exists in all templates...")
    from apps.inspections.services.template_service import TemplateService
    all_templates = TemplateService().list_all_templates()
    found_in_all = next(
        (t for t in all_templates if t.get('template_key') == 'ansi_a92_2_periodic_dielectric_test'),
        None
    )
    if found_in_all:
        print("   Template exists globally but was filtered out")
        print(f"   Required capabilities: {found_in_all.get('required_capabilities')}")
    else:
        print("   Template not found at all!")
