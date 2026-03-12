"""Seed verification skeleton (v1)

Run:
- python manage.py shell < tools/seed/seed_verify.py

Prints a health report:
- object counts
- sample linkages exist
- inventory totals sensible
- core balances computed
- leasing sharing contracts exist

Fill in actual queries once models are wired.
"""

def main():
    print("Seed verification report (stub)")
    # TODO: Add real checks:
    # - assert tenants exist
    # - assert at least 1 asset has meters
    # - assert inventory has on-hand in at least one location
    # - assert special order request exists
    # - assert sharing contract exists
    # - assert one UNSAFE defect exists (if you seed inspections later)
    print("OK (stub)")

if __name__ == "__main__":
    main()
