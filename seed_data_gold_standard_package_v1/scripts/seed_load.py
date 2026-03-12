"""Seed loader skeleton (v1)

How to run (example):
- python manage.py shell < tools/seed/seed_load.py

This script reads seed/seed_plan.yaml and creates:
- tenants, users, assets, meters
- inventory locations, parts, initial stock adjustments
- vendor and special-order request
- leasing sharing contract and billing schedule

IMPORTANT:
- Replace the placeholder imports with your project's actual models.
- Replace any field names that differ (e.g. tenant_root vs tenant).

"""

import os
from decimal import Decimal
from pathlib import Path
import yaml
from django.utils import timezone
from django.db import transaction

BASE_DIR = Path(__file__).resolve().parent.parent  # adjust if you relocate scripts
SEED_PLAN = Path(os.environ.get("SEED_PLAN_PATH", BASE_DIR / "seed" / "seed_plan.yaml"))

# TODO: Replace these imports with your actual models
# from core_tenant.models import Tenant
# from users.models import User, Membership
# from assets.models import Asset
# from maintenance.models import MaintenanceProgram, MaintenanceDueInstance, AssetMeter
# from inspections.models import InspectionProgram
# from inventory.models import Vendor, Part, InventoryLocation, InventoryTransaction
# from leasing.models import SharingContract, RecurringBillingSchedule

def money(x):
    return Decimal(str(x))

def load_plan():
    with open(SEED_PLAN, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def upsert_by_slug(model, slug_field, slug, defaults):
    """Simple upsert helper; replace with your ORM approach."""
    obj, created = model.objects.get_or_create(**{slug_field: slug}, defaults=defaults)
    if not created:
        for k, v in defaults.items():
            setattr(obj, k, v)
        obj.save()
    return obj

def main():
    plan = load_plan()
    prefix = os.environ.get("SEED_TENANT_SLUG_PREFIX", "demo")
    force_reset = os.environ.get("SEED_FORCE_RESET") == "1"

    print(f"Loading seed plan: {SEED_PLAN}")
    print(f"Prefix={prefix} force_reset={force_reset}")

    # TODO: optionally implement reset by deleting demo tenants

    with transaction.atomic():
        # 1) Tenants
        tenant_by_slug = {}
        for t in plan["tenants"]:
            slug = t["slug"]
            defaults = {"name": t["name"], **t.get("type_flags", {})}
            # tenant = upsert_by_slug(Tenant, "slug", slug, defaults)
            # tenant_by_slug[slug] = tenant
            tenant_by_slug[slug] = {"slug": slug, **defaults}  # placeholder
            print("Tenant:", slug)

        # 2) Users/Memberships
        for u in plan.get("users", []):
            print("User:", u["email"], "tenant:", u["tenant_slug"], "role:", u["role"])
            # user = User.objects.get_or_create(email=u["email"])[0]
            # Membership.objects.get_or_create(user=user, tenant_root=tenant_by_slug[u["tenant_slug"]], defaults={"role": u["role"]})

        # 3) Assets
        asset_by_key = {}
        for a in plan.get("assets", []):
            print("Asset:", a["name"], a["identifiers"])
            # asset = Asset.objects.create(...)
            asset_by_key[a["key"]] = {"id": a["key"]}  # placeholder

        # 4) Meters
        for m in plan.get("meters", []):
            print("Meter:", m["asset_key"], m["meter_type"], m["value"])
            # AssetMeter.upsert_current(asset=..., meter_type=..., value=..., source=...)

        # 5) Maintenance + inspection programs
        for mp in plan.get("maintenance_programs", []):
            print("MaintenanceProgram:", mp["key"])
            # MaintenanceProgram.objects.get_or_create(program_key=mp["key"], defaults={...})

        for ip in plan.get("inspection_programs", []):
            print("InspectionProgram:", ip["program_key"], ip["standards_version"])
            # InspectionProgram.objects.get_or_create(program_key=ip["program_key"], defaults={...})

        # 6) Inventory locations
        for loc in plan.get("inventory_locations", []):
            print("Location:", loc["code"], loc["name"])
            # InventoryLocation.objects.get_or_create(code=..., tenant_root=..., defaults={...})

        # 7) Parts
        for p in plan.get("parts", []):
            print("Part:", p["sku"], p["description"])
            # Part.objects.get_or_create(sku=..., tenant_root=..., defaults={...})

        # 8) Initial stock adjustments
        for s in plan.get("initial_stock", []):
            print("Initial stock:", s["part_key"], s["location_code"], s["qty"])
            # InventoryTransaction.create_initial_load(...)

        # 9) Vendors + special orders
        for v in plan.get("vendors", []):
            print("Vendor:", v["name"])
            # Vendor.objects.get_or_create(...)

        for so in plan.get("special_orders", []):
            print("SpecialOrder:", so["key"], so["part_key"], so["qty"])
            # SpecialOrderPartRequest.objects.get_or_create(...)

        # 10) Leasing sharing + billing schedule
        leasing = plan.get("leasing", {})
        for sc in leasing.get("sharing_contracts", []):
            print("SharingContract:", sc["leasing_tenant_slug"], "->", sc["customer_tenant_slug"])
            # SharingContract.objects.get_or_create(...)

        for bs in leasing.get("billing_schedules", []):
            print("BillingSchedule:", bs["cadence"], "next:", bs["next_run_date"])
            # RecurringBillingSchedule.objects.get_or_create(...)

    print("Seed load complete.")

if __name__ == "__main__":
    main()
