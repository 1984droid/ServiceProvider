# Documentation

This directory contains project documentation organized by topic.

## Active Documentation

### ANSI Standard Integration (`ansi_standard_integration/`)
Documentation for the ANSI A92.2-2021 standard text integration system:

- **STANDARD_TEXT_INTEGRATION_SUMMARY.md** - Comprehensive implementation summary
  - Business value and impact
  - Implementation details
  - Coverage analysis (100% across all templates)
  - Technical architecture
  - Testing recommendations

- **STANDARD_TEXT_REFERENCE_DESIGN.md** - Original design document
  - Design options considered
  - Hybrid approach rationale
  - Integration strategy

- **STANDARD_TEXT_USAGE_EXAMPLE.md** - Usage guide for template authors
  - How to add standard text to templates
  - Available excerpts
  - Best practices

## Archive (`archive/`)
Historical documentation from previous iterations and experiments:

- **ANSI_RTF_IMAGES_EXTRACTION_SUMMARY.md** - RTF image extraction research
- **DIELECTRIC_TEST_AUDIT.md** - Dielectric test template audit
- **REFERENCE_IMAGE_IMPLEMENTATION_PLAN.md** - Image reference implementation planning

These documents are preserved for historical reference but represent superseded approaches.

## Core Documentation

Project-wide documentation:

- **README.md** (root) - Project overview and quick start
- **DEPLOYMENT.md** - Production deployment guide
- **DEPLOY_QUICK_START.md** - Quick deployment reference
- **SETUP.md** - Development environment setup
- **SETUP_SUMMARY.md** - Setup process overview
- **DATA_CONTRACT.md** - API and data model documentation
- **API_SUMMARY.md** - API endpoint reference
- **FRONTEND_ROADMAP.md** - Frontend development roadmap

## Contributing

When adding new documentation:

1. Place topic-specific docs in appropriate subdirectories
2. Keep root-level docs for broad project concerns
3. Move superseded docs to `archive/` with context
4. Update this README with new doc locations
