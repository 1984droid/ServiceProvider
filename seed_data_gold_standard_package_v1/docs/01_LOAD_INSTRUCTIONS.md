# 01 Load Instructions

## Option A (recommended): Python loader script
1) Copy `scripts/` into your repo under something like `tools/seed/`
2) Update imports at the top of `seed_load.py` to match your model paths.
3) Run:
   - python manage.py shell < tools/seed/seed_load.py

Or implement a management command:
- python manage.py seed_demo --reset

## Option B: Django loaddata fixtures
This package includes a *placeholder* fixtures directory you can adopt if you prefer `manage.py loaddata`,
but because field names are evolving, the script approach is usually faster.

## Expected environment variables
- SEED_TENANT_SLUG_PREFIX=demo (optional)
- SEED_FORCE_RESET=1 (optional; enables destructive reset logic)

## After loading
Run:
- python manage.py shell < tools/seed/seed_verify.py

This prints a health report: counts, balances, and whether key linkages exist.
