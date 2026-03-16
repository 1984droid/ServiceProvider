# Deployment Guide

## Docker Deployment

### Prerequisites
- Docker 24+ with BuildKit support
- Docker Compose 2.0+ (optional, for local testing)
- PostgreSQL 18+ database (external or via Docker Compose)

### Build Process

The Dockerfile uses a multi-stage build:

**Stage 1: Frontend Builder**
- Uses Node.js 22 to build the React/Vite frontend
- Runs `npm ci` to install dependencies
- Runs `npm run build` to create production build
- Output: `/frontend/dist` directory with static assets

**Stage 2: Python Builder**
- Builds Python virtual environment with all dependencies
- Installs gunicorn and whitenoise for production serving

**Stage 3: Runtime**
- Lightweight Python 3.14 slim image
- Copies built frontend from Stage 1
- Copies Python venv from Stage 2
- Runs `collectstatic` to gather all static files
- Serves via gunicorn with 4 workers

### Build Command

```bash
docker build -t service-provider:latest .
```

### Run Command

```bash
docker run -d \
  -p 8100:8100 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/dbname" \
  -e SECRET_KEY="your-secret-key" \
  -e DJANGO_SETTINGS_MODULE="config.settings" \
  -e ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com" \
  --name service-provider \
  service-provider:latest
```

### Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Django secret key (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hostnames

Optional:
- `DEBUG` - Set to `False` for production (default: False)
- `DJANGO_SETTINGS_MODULE` - Settings module (default: config.settings)

### Docker Compose (Local Testing)

```yaml
version: '3.8'

services:
  db:
    image: postgres:18-alpine
    environment:
      POSTGRES_DB: service_provider
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8100 --workers 4
    volumes:
      - ./media:/app/media
      - ./logs:/app/logs
    ports:
      - "8100:8100"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/service_provider
      - SECRET_KEY=dev-secret-key-change-in-production
      - DEBUG=False
      - ALLOWED_HOSTS=localhost,127.0.0.1
    depends_on:
      - db

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

### Initial Setup (After First Deploy)

1. Run migrations:
```bash
docker exec service-provider python manage.py migrate
```

2. Create superuser:
```bash
docker exec -it service-provider python manage.py createsuperuser
```

3. (Optional) Load seed data:
```bash
docker exec service-provider python manage.py seed_data
```

## Platform-Specific Deployments

### Railway

Railway auto-detects Dockerfiles. Simply:
1. Connect your GitHub repository
2. Set environment variables in Railway dashboard
3. Deploy

**Railway-specific notes:**
- Railway provides DATABASE_URL automatically if you provision PostgreSQL
- Set PORT environment variable if Railway requires it (Railway usually auto-detects from EXPOSE)

### Render

1. Create new Web Service
2. Connect repository
3. Set:
   - **Build Command:** Leave empty (uses Dockerfile)
   - **Environment:** Docker
   - **Health Check Path:** `/admin/`
4. Add environment variables

### Heroku

```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"
git push heroku master
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### AWS ECS / Fargate

1. Push image to ECR:
```bash
aws ecr create-repository --repository-name service-provider
docker tag service-provider:latest <aws-account-id>.dkr.ecr.<region>.amazonaws.com/service-provider:latest
docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/service-provider:latest
```

2. Create ECS task definition with:
   - Image: Your ECR image
   - Port mappings: 8100
   - Environment variables (or use AWS Secrets Manager)
   - RDS PostgreSQL for database

3. Create ECS service with load balancer

## Static Files

The application uses **WhiteNoise** to serve static files efficiently without requiring a separate web server (like nginx) for static assets.

**How it works:**
- Frontend builds to `frontend/dist/`
- `collectstatic` gathers all static files (Django admin, frontend build) into `/app/staticfiles/`
- WhiteNoise serves these files with compression and caching headers
- Production-ready without additional configuration

## Health Checks

The Dockerfile includes a health check that pings `/admin/` every 30 seconds. Most platforms will use this automatically.

Manual health check:
```bash
curl http://localhost:8100/admin/
```

## Troubleshooting

### Frontend not loading
- Check that `collectstatic` ran successfully in build logs
- Verify `STATIC_URL` and `STATIC_ROOT` in settings
- Check browser console for 404 errors on static files

### Database connection errors
- Verify `DATABASE_URL` format: `postgresql://user:password@host:port/database`
- Ensure database is accessible from container
- Check PostgreSQL version (requires 18+)

### Import errors or missing modules
- Verify all dependencies in `requirements.txt`
- Frontend dependencies should auto-install during Docker build
- Check build logs for npm or pip errors

## Production Checklist

- [ ] `DEBUG=False` in environment
- [ ] Strong `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] Database backups configured
- [ ] HTTPS/SSL certificate installed
- [ ] Media files storage configured (S3 recommended for production)
- [ ] Logging configured (CloudWatch, Sentry, etc.)
- [ ] Environment variables secured (not in code)
- [ ] Migrations run successfully
- [ ] Superuser created
- [ ] Health checks passing
