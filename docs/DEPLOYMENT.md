# Deployment Guide

## Port Configuration

### Development Environment

**NEW_BUILD_STARTER Ports:**
- Django Backend: `8100`
- Database: `service_provider_new` on PostgreSQL `5432`
- Frontend (future): `3100` or `5173`

**Legacy Application Ports:**
- Django Backend: `8000`
- Database: `advantageapp` on PostgreSQL `5432`
- Frontend: `3000`

This separation allows both applications to run simultaneously during migration.

### Production Environment

In production, configure ports based on your deployment strategy:

**Option 1: Different Domains**
```
legacy.example.com  → Legacy app on port 8000
app.example.com     → NEW_BUILD_STARTER on port 8100
```

**Option 2: Path-Based Routing**
```
example.com/legacy/ → Legacy app on port 8000
example.com/        → NEW_BUILD_STARTER on port 8100
```

**Option 3: Blue-Green Deployment**
```
Blue:  NEW_BUILD_STARTER on 8100
Green: Legacy app on 8000
Swap when ready
```

### Environment Variables

**Required in production `.env`:**
```bash
# Django
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_PORT=8100

# Database
DB_NAME=service_provider_new
DB_USER=app_user
DB_PASSWORD=secure-password-here
DB_HOST=your-db-host.com
DB_PORT=5432

# CORS (if frontend on different domain)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Nginx Configuration Example

```nginx
# NEW_BUILD_STARTER
server {
    listen 80;
    server_name app.example.com;

    location / {
        proxy_pass http://127.0.0.1:8100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/new_build_starter/staticfiles/;
    }
}

# Legacy Application (if still needed)
server {
    listen 80;
    server_name legacy.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        # ... same proxy settings
    }
}
```

### Docker Configuration Example

```yaml
version: '3.8'

services:
  # NEW_BUILD_STARTER
  new_app:
    build: ./NEW_BUILD_STARTER
    ports:
      - "8100:8100"
    environment:
      - DJANGO_PORT=8100
      - DB_NAME=service_provider_new
    depends_on:
      - db

  # Legacy app (if still needed)
  legacy_app:
    build: ./advantage_app
    ports:
      - "8000:8000"
    environment:
      - DB_NAME=advantageapp
    depends_on:
      - db

  # Shared database
  db:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Database Setup

**Production Database Creation:**
```bash
# Create new database for NEW_BUILD_STARTER
psql -U postgres -c "CREATE DATABASE service_provider_new;"

# Create dedicated user
psql -U postgres -c "CREATE USER app_user WITH PASSWORD 'secure-password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE service_provider_new TO app_user;"

# Run migrations
python manage.py migrate --settings=config.settings
```

**Both databases can exist on same PostgreSQL instance:**
- `advantageapp` (legacy)
- `service_provider_new` (NEW_BUILD_STARTER)

### Migration Strategy

**Phase 1: Parallel Running**
- Legacy app on port 8000 (production traffic)
- NEW_BUILD_STARTER on port 8100 (testing/staging)
- Data sync from legacy → new (nightly jobs)

**Phase 2: Gradual Cutover**
- Route some customers to NEW_BUILD_STARTER
- Monitor performance and stability
- Roll back if issues detected

**Phase 3: Full Cutover**
- All traffic to NEW_BUILD_STARTER on 8100
- Legacy app remains on 8000 (read-only archive)
- Final data migration and reconciliation

**Phase 4: Decommission**
- Legacy app shutdown
- Archive legacy database
- NEW_BUILD_STARTER becomes primary

### Monitoring

**Health Check Endpoint:**
```
GET http://localhost:8100/api/health/
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

**Port Verification:**
```bash
# Check if port 8100 is listening
netstat -an | grep 8100

# Or on Linux
sudo lsof -i :8100
```

### Troubleshooting

**Port conflict:**
```bash
# Find process using port 8100
# Windows
netstat -ano | findstr :8100

# Linux/Mac
lsof -ti:8100

# Kill if needed (be careful!)
# Linux/Mac
kill -9 $(lsof -ti:8100)
```

**Wrong database:**
- Check `.env` file has `DB_NAME=service_provider_new`
- Verify `config/settings.py` default matches
- Test connection: `python manage.py dbshell`

**CORS issues (if frontend on different port):**
- Add frontend URL to `CORS_ALLOWED_ORIGINS` in settings
- In development: `http://localhost:3100` or `http://localhost:5173`
- In production: actual domain

---

**Summary:**
- NEW_BUILD_STARTER: Port **8100**, Database **service_provider_new**
- Legacy App: Port **8000**, Database **advantageapp**
- Both can run simultaneously for smooth migration
