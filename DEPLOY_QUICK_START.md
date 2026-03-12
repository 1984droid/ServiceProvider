# Quick Deployment Guide

Three easy ways to deploy this application.

---

## 🚀 Option 1: One-Command Docker Deployment (Fastest)

**Requirements:** Docker installed

```bash
# 1. Configure environment
cp .env.docker .env.docker.local
nano .env.docker.local  # Update DB_PASSWORD and SECRET_KEY

# 2. Deploy everything
docker compose up -d

# 3. Create admin user
docker compose exec web python manage.py createsuperuser

# Done! Access at http://localhost:8100/admin
```

---

## 🖥️ Option 2: Traditional Server Deployment

**Requirements:** Python 3.14+, PostgreSQL 18+

```bash
# 1. Run production setup script
python deploy.py setup

# This will:
# - Create .env.production with secure settings
# - Install production dependencies
# - Create database
# - Run migrations
# - Collect static files

# 2. Create superuser
python create_superuser.py

# 3. Start server
gunicorn config.wsgi:application --bind 0.0.0.0:8100 --workers 4
```

---

## ⚙️ Option 3: Development Setup (Already Done!)

**You've already completed this:**

```bash
# What you did:
python setup.py setup  # ✓ Done
# Server running on http://localhost:8100

# Admin credentials:
# Username: admin
# Password: admin
```

---

## 📋 Quick Commands

### Development
```bash
python setup.py setup          # Initial setup
python setup.py update         # Update after git pull
python manage.py runserver     # Start dev server
```

### Production
```bash
python deploy.py setup         # Production setup
python deploy.py update        # Update production
python deploy.py check         # Check readiness
python deploy.py backup        # Backup database
```

### Docker
```bash
docker compose up -d           # Start all services
docker compose down            # Stop all services
docker compose logs -f web     # View application logs
docker compose exec web bash   # Access container shell
```

---

## 🔒 Production Checklist

Before deploying to production:

1. **Security**
   ```bash
   # Generate secure secret key
   python -c "import secrets; print(secrets.token_urlsafe(50))"

   # Update .env.production:
   # - SECRET_KEY=<generated-key>
   # - DEBUG=False
   # - ALLOWED_HOSTS=yourdomain.com
   # - DB_PASSWORD=<strong-password>
   ```

2. **SSL Certificate**
   ```bash
   # Free certificate from Let's Encrypt
   sudo certbot --nginx -d yourdomain.com
   ```

3. **Firewall**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

4. **Backups**
   ```bash
   # Setup daily backups
   crontab -e
   # Add: 0 2 * * * cd /path/to/app && python deploy.py backup
   ```

---

## 🆘 Quick Troubleshooting

### Can't connect to database
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql
# or
docker compose ps db
```

### Static files not loading
```bash
python manage.py collectstatic --noinput
```

### Docker container won't start
```bash
docker compose logs web
docker compose logs db
```

### Port already in use
```bash
# Change DJANGO_PORT in .env
# or
# Change ports in docker-compose.yml
```

---

## 📚 Full Documentation

- **Complete Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Setup Documentation**: [docs/SETUP_SCRIPT.md](docs/SETUP_SCRIPT.md)
- **API Reference**: [API_SUMMARY.md](API_SUMMARY.md)

---

## 🎯 Current Status

✅ **Development Environment**: Running on http://localhost:8100
✅ **Database**: PostgreSQL 18 on port 8101
✅ **All Models**: Migrated and ready
✅ **Admin User**: Created (admin/admin)
✅ **Deployment Scripts**: Ready to use

**You're ready to develop or deploy to production!**
