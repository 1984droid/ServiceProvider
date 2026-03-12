"""Seed reset skeleton (v1)

Run:
- python manage.py shell < tools/seed/seed_reset.py

Goal: remove demo tenants and all dependent objects safely in dev environments.
Implement tenant-based deletion by slug prefix.

IMPORTANT:
- Only enable destructive deletion if SEED_FORCE_RESET=1 (safety).
"""

import os

def main():
    if os.environ.get("SEED_FORCE_RESET") != "1":
        print("Refusing to reset without SEED_FORCE_RESET=1")
        return

    prefix = os.environ.get("SEED_TENANT_SLUG_PREFIX", "demo")
    print(f"Resetting demo data for prefix={prefix}")

    # TODO: Replace with your models and deletion logic.
    # Example:
    # Tenant.objects.filter(slug__startswith=f"{prefix}_").delete()

    print("Reset complete (stub).")

if __name__ == "__main__":
    main()
