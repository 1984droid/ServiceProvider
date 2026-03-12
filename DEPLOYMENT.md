# Deployment Guide - Service Provider Application

Complete deployment guide for production environments with multiple deployment options.

---

## Prerequisites

- **Python 3.14+**
- **PostgreSQL 18+**
- **Domain name** (for production)
- **SSL certificate** (for HTTPS)
- **Docker** (for containerized deployment)

---

## Deployment Options

### Option 1: Traditional Deployment (VPS/Server)

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.14
sudo apt install python3.14 python3.14-venv python3-pip

# Install PostgreSQL 18
sudo apt install postgresql-18 postgresql-contrib

# Install nginx
sudo apt install nginx
```

#### 2. Application Deployment

```bash
# Clone repository
git clone <your-repo-url>
cd ServiceProvider

# Create virtual environment
python3.14 -m venv venv
source venv/bin/activate

# Run deployment script
python deploy.py setup
```

This will:
- ✓ Create `.env.production` with secure settings
- ✓ Install production dependencies (gunicorn, whitenoise)
- ✓ Create PostgreSQL database
- ✓ Run migrations
- ✓ Collect static files
- ✓ Generate superuser creation script

#### 3. Create Superuser

```bash
python create_superuser.py
```

#### 4. Configure Nginx

```bash
# Copy nginx configuration
sudo cp nginx/nginx.conf /etc/nginx/sites-available/serviceprovider
sudo ln -s /etc/nginx/sites-available/serviceprovider /etc/nginx/sites-enabled/

# Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. Configure Systemd Service

Create `/etc/systemd/system/serviceprovider.service`:

```ini
[Unit]
Description=Service Provider Application
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/ServiceProvider
Environment="PATH=/path/to/ServiceProvider/venv/bin"
ExecStart=/path/to/ServiceProvider/venv/bin/gunicorn \
    config.wsgi:application \
    --bind 0.0.0.0:8100 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /var/log/serviceprovider/access.log \
    --error-logfile /var/log/serviceprovider/error.log

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable serviceprovider
sudo systemctl start serviceprovider
```

---

### Option 2: Docker Deployment (Recommended)

#### 1. Install Docker

```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose-plugin
```

#### 2. Configure Environment

```bash
# Edit .env.docker with your settings
nano .env.docker
```

Update these values:
- `SECRET_KEY` - Generate secure key
- `DB_PASSWORD` - Strong database password
- `ALLOWED_HOSTS` - Your domain(s)
- `CORS_ALLOWED_ORIGINS` - Your frontend URLs

#### 3. Build and Start

```bash
# Build and start all services
docker compose up -d

# Check logs
docker compose logs -f

# Create superuser
docker compose exec web python manage.py createsuperuser
```

#### 4. Services Available

- **Django Application**: http://localhost:8100
- **PostgreSQL**: localhost:8101
- **Nginx**: http://localhost:80
- **Redis**: localhost:6379

#### 5. Manage Services

```bash
# Stop services
docker compose down

# Restart services
docker compose restart

# View logs
docker compose logs -f web

# Backup database
docker compose exec db pg_dump -U postgres service_provider_prod > backup.sql

# Update application
git pull
docker compose build web
docker compose up -d
```

---

## Production Checklist

### Security

- [ ] Set strong `SECRET_KEY` in `.env.production`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Enable SSL/HTTPS
- [ ] Configure firewall (allow only 80, 443)
- [ ] Use strong database password
- [ ] Enable CSRF and session cookie security
- [ ] Configure CORS properly

### Database

- [ ] PostgreSQL 18+ installed and running
- [ ] Database created
- [ ] Migrations applied
- [ ] Regular backups configured
- [ ] Connection pooling configured

### Application

- [ ] Static files collected
- [ ] Media files directory writable
- [ ] Logging configured
- [ ] Superuser created
- [ ] Email backend configured (optional)
- [ ] Sentry/monitoring configured (optional)

### Server

- [ ] Nginx configured as reverse proxy
- [ ] SSL certificate installed
- [ ] Systemd service configured
- [ ] Log rotation configured
- [ ] Monitoring/alerts setup

---

## Updating Production

### Traditional Deployment

```bash
cd ServiceProvider
source venv/bin/activate
git pull
python deploy.py update
sudo systemctl restart serviceprovider
```

### Docker Deployment

```bash
cd ServiceProvider
git pull
docker compose build web
docker compose up -d
```

---

## Backup & Restore

### Automated Backup (Traditional)

```bash
# Create backup
python deploy.py backup

# Backups are stored in: backups/
```

### Automated Backup (Docker)

```bash
# Backup database
docker compose exec db pg_dump -U postgres service_provider_prod > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker compose exec -T db psql -U postgres service_provider_prod < backups/backup_20260311_120000.sql
```

### Scheduled Backups (Crontab)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/ServiceProvider && /path/to/venv/bin/python deploy.py backup
```

---

## Monitoring & Logs

### Application Logs

**Traditional:**
```bash
# Application logs
tail -f logs/django.log

# Gunicorn logs
journalctl -u serviceprovider -f
```

**Docker:**
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f web
docker compose logs -f db
```

### Database Logs

```bash
# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-18-main.log
```

### Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

---

## SSL/HTTPS Setup

### Using Let's Encrypt (Free)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

### Using Custom Certificate

1. Place certificate files in `nginx/ssl/`:
   - `cert.pem` - Certificate
   - `key.pem` - Private key

2. Uncomment HTTPS server block in `nginx/nginx.conf`

3. Reload nginx:
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

---

## Performance Optimization

### Database

```python
# Add to settings.py for connection pooling
DATABASES = {
    'default': {
        ...
        'CONN_MAX_AGE': 600,  # 10 minutes
        'OPTIONS': {
            'pool': {
                'min_size': 2,
                'max_size': 10,
            }
        }
    }
}
```

### Caching with Redis

```python
# Add to settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Static Files

Static files are served by:
- **Nginx** (in production with reverse proxy)
- **WhiteNoise** (Docker/standalone)

---

## Troubleshooting

### Database Connection Failed

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection settings in .env
cat .env.production

# Test connection
psql -h localhost -p 8101 -U postgres -d service_provider_prod
```

### Static Files Not Loading

```bash
# Collect static files
python manage.py collectstatic --noinput

# Check nginx configuration
sudo nginx -t

# Check file permissions
ls -la staticfiles/
```

### Docker Container Not Starting

```bash
# Check logs
docker compose logs web
docker compose logs db

# Rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## Scaling

### Horizontal Scaling

1. **Load Balancer**: Add nginx/HAProxy load balancer
2. **Multiple App Servers**: Run multiple gunicorn instances
3. **Shared Database**: All app servers connect to same PostgreSQL
4. **Shared Storage**: Use NFS/S3 for media files
5. **Redis**: Centralized caching/session storage

### Vertical Scaling

1. **Increase Workers**: More gunicorn workers
2. **Database Tuning**: Optimize PostgreSQL settings
3. **Connection Pooling**: pgBouncer
4. **Caching**: Redis for sessions and frequently accessed data

---

## Quick Reference

### Commands

```bash
# Development
python setup.py setup          # Initial setup
python setup.py update         # Update installation
python manage.py runserver     # Dev server

# Production
python deploy.py setup         # Production setup
python deploy.py update        # Update production
python deploy.py check         # Check production readiness
python deploy.py backup        # Backup database

# Docker
docker compose up -d           # Start
docker compose down            # Stop
docker compose logs -f         # View logs
docker compose build           # Rebuild
```

### URLs

- **Admin**: http://yourdomain.com/admin/
- **API**: http://yourdomain.com/api/
- **Docs**: http://yourdomain.com/api/docs/ (if enabled)

---

## Support

For issues or questions:
1. Check logs first
2. Review this documentation
3. Check GitHub issues
4. Contact system administrator

---

**Version**: 1.0
**Last Updated**: 2026-03-11
