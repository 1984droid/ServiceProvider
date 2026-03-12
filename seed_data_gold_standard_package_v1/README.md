# Seed Data Package — Gold Standard (v1)

Generated: 2026-02-08

Purpose:
- Provide a repeatable **seed dataset** for dev and staging so your team can
  manually exercise the most important workflows without having to create everything by hand.
- This complements the automated test suite package by enabling:
  - UI smoke testing
  - manual debugging with realistic linked records
  - demo data for stakeholders

This seed pack intentionally covers the "gold standard" safety+finance workflows including the
inspection → work order loop improvements discussed in the integration assessment. fileciteturn4file0

## What you get
- `seed/seed_plan.yaml`: The canonical dataset definition (domain-level)
- `seed/catalog_*.csv`: parts/locations/nouns minimal datasets
- `scripts/seed_load.py`: loader skeleton (adapt model imports & field names)
- `scripts/seed_reset.py`: reset helper skeleton
- `scripts/seed_verify.py`: verification script skeleton (checks invariants)
- `docs/*`: instructions, scenario walkthroughs, troubleshooting

## Important note
Because your schema is actively evolving pre-live, the loader scripts are intentionally written as
**thin adapters** you can quickly align to your actual Django models and fields.

Once aligned, this becomes your team's "one command to get a working demo universe".

