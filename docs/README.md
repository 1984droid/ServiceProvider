# Documentation Index

Complete documentation for the Service Provider application.

---

## Quick Start

**New to the project?** Start here:
- **[SETUP_SCRIPT.md](SETUP_SCRIPT.md)** - Automated setup with `python setup.py setup` (RECOMMENDED)
- **[QUICK_START.md](QUICK_START.md)** - Manual setup guide (alternative)

**Important:** NEW_BUILD_STARTER runs on **port 8100** (not 8000) to avoid conflicts with the legacy application.

---

## Core Documentation

### Data Model & Architecture

1. **[SCHEMA_QUICK_REFERENCE.md](SCHEMA_QUICK_REFERENCE.md)** 📊
   - Visual guide to all models, fields, and relationships
   - Quick reference cheat sheet
   - **Start here for data model overview**

2. **[DATA_CONTRACT.md](DATA_CONTRACT.md)** 📋
   - Comprehensive data model specification
   - Business rules and constraints
   - API expectations
   - Validation rules

3. **[MODEL_CHANGES_SUMMARY.md](MODEL_CHANGES_SUMMARY.md)** 📝
   - Recent model changes and rationale
   - Migration from multi-tenant to single-tenant
   - New features explained

### Specialized Workflows

4. **[INSPECTION_EQUIPMENT_FLOW.md](INSPECTION_EQUIPMENT_FLOW.md)** 🔧
   - Tag-driven inspection workflow
   - Equipment data collection on-demand
   - Placard and capability data entry

### Development Tools

5. **[SETUP_SCRIPT.md](SETUP_SCRIPT.md)** 🔧
   - Automated setup/update/wipe script
   - Database management commands
   - Development workflow guide
   - **Recommended for all installations**

6. **[SCRIPTS_README.md](SCRIPTS_README.md)** 🛠️
   - Guide to all development scripts
   - Daily workflows
   - Troubleshooting

7. **[DEPLOYMENT.md](DEPLOYMENT.md)** 🚀
   - Port configuration details
   - Production deployment guide
   - Docker and Nginx examples
   - Migration strategy

8. **[API_REFERENCE.md](API_REFERENCE.md)** 📡
   - Complete REST API documentation
   - All endpoints with examples
   - Request/response formats
   - Filtering, searching, pagination

---

## Document Summary

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **SETUP_SCRIPT.md** | Automated setup script | First time setup, updates (RECOMMENDED) |
| **QUICK_START.md** | Manual setup guide | Alternative setup method |
| **SCHEMA_QUICK_REFERENCE.md** | Visual data model | Building features, API design |
| **DATA_CONTRACT.md** | Detailed specification | Implementation, validation |
| **MODEL_CHANGES_SUMMARY.md** | Change history | Understanding recent updates |
| **INSPECTION_EQUIPMENT_FLOW.md** | Equipment workflow | Building inspection features |
| **SCRIPTS_README.md** | Development scripts | Daily development |
| **DEPLOYMENT.md** | Deployment guide | Production setup, port config |
| **API_REFERENCE.md** | REST API documentation | API integration, frontend development |

---

## Reading Order

### For Developers (First Time)
1. QUICK_START.md - Get running
2. SCHEMA_QUICK_REFERENCE.md - Understand data model
3. API_REFERENCE.md - Learn API endpoints
4. SCRIPTS_README.md - Learn daily tools

### For Product/Design
1. DATA_CONTRACT.md - Business rules
2. INSPECTION_EQUIPMENT_FLOW.md - User workflows
3. SCHEMA_QUICK_REFERENCE.md - Data relationships

### For QA/Testing
1. DATA_CONTRACT.md - Validation rules
2. MODEL_CHANGES_SUMMARY.md - What changed
3. INSPECTION_EQUIPMENT_FLOW.md - Test scenarios

---

## Additional Resources

- **Main README**: `../README.md` - Project overview
- **Scripts**: `../scripts/` - Development helper scripts
- **Models**: `../apps/*/models.py` - Actual model implementations

---

**Keep this documentation up to date as the project evolves.**
