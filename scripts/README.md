# Development Scripts

Helper scripts for streamlined development workflow.

**See [SCRIPTS_README.md](SCRIPTS_README.md) for detailed documentation.**

---

## Quick Reference

### Initial Setup
```bash
# Linux/Mac
chmod +x scripts/*.sh
./scripts/setup_dev.sh

# Windows
scripts\setup_dev.bat
```

### Daily Development
```bash
# Start server
./scripts/run_dev.sh       # Linux/Mac
scripts\run_dev.bat         # Windows

# Django shell
./scripts/shell.sh          # Linux/Mac
scripts\shell.bat           # Windows

# After model changes
./scripts/make_migrations.sh   # Linux/Mac
scripts\make_migrations.bat    # Windows
```

### Database Operations
```bash
# Reset database (DESTRUCTIVE)
./scripts/reset_dev.sh      # Linux/Mac
scripts\reset_dev.bat       # Windows

# Generate new .env
./scripts/generate_env.sh   # Linux/Mac
scripts\generate_env.bat    # Windows
```

---

## Scripts Included

| Script | Purpose |
|--------|---------|
| `setup_dev.sh/bat` | Complete dev environment setup |
| `run_dev.sh/bat` | Start development server |
| `shell.sh/bat` | Open Django shell |
| `make_migrations.sh/bat` | Create and apply migrations |
| `reset_dev.sh/bat` | Drop and recreate database |
| `generate_env.sh/bat` | Generate .env with secure values |
| `generate_env.py` | Core env generation script |

---

**For complete documentation, see [SCRIPTS_README.md](SCRIPTS_README.md)**
