# Archived Scripts

This directory contains one-time migration and experimental scripts that have served their purpose but are preserved for reference.

## Migration Scripts (Completed)

### `add_standard_references_to_templates.py`
**Status:** Completed  
**Purpose:** Added standard_ref fields to all ANSI A92.2-2021 templates  
**Date:** March 2026  
**Notes:** All templates now have standard references. Do not run again.

### `extract_ansi_from_docx.py`
**Status:** Superseded by extract_standard_text.py  
**Purpose:** Experimental extraction of text and images from ANSI DOCX  
**Date:** March 2026  
**Notes:** Used during research phase. Final extraction script is in parent directory.

### `fix_templates.py`
**Status:** Completed  
**Purpose:** Fixed template formatting and validation issues  
**Date:** March 2026  
**Notes:** One-time template cleanup. Templates are now valid.

## Active Scripts

Active scripts remain in the parent `scripts/` directory:

- `extract_standard_text.py` - Extracts ANSI standard text excerpts (use for updates)
- `generate_sample_pdfs.py` - Generates sample PDF reports for testing
- `reset_database.py` - Database reset utility
- Setup/deployment scripts (setup_dev, run_dev, etc.)

## Note

These archived scripts should not be deleted as they provide historical context and could be referenced for future migrations. However, they should not be run in production or development environments.
