# Deployment Guide

This guide covers deploying the Render Control Plane to both local development and production environments.

## 🏠 Local Development

### Prerequisites

- Python 3.13+
- Redis server
- Git

### Step-by-Step Setup

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd Render-ControlPlane
   ```

2. **Set up Python environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   export SECRET_KEY="django-insecure-your-dev-secret-key"
   export DEBUG="True"
   export CELERY_BROKER_URL="redis://localhost:6379/0"
   ```

4. **Install and start Redis:**
   ```bash
   # macOS
   brew install redis
   brew services start redis
   
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install redis-server
   sudo systemctl start redis
   sudo systemctl enable redis
   
   # Windows (using WSL or Docker)
   # Use Docker: docker run -d -p 6379:6379 redis:alpine
   ```

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Celery worker (in a new terminal):**
   ```bash
   cd backend
   source venv/bin/activate
   celery -A backend worker -l info
   ```

8. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

### Verification

- **API**: Visit `http://localhost:8000/api/`
- **Health Check**: Visit `http://localhost:8000/api/health/`
- **Admin**: Visit `http://localhost:8000/admin/`

## 🚀 Production Deployment on Render

### Prerequisites

- Render account
- Git repository with your code
- Render API key

### Automatic Deployment (Recommended)

The project includes a complete `render.yaml` blueprint for automatic deployment:

1. **Push your code to Git:**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push origin main
   ```

2. **Connect to Render:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your Git repository
   - Render will automatically detect and deploy using `render.yaml`

3. **Configure environment variables in Render dashboard:**
   - Navigate to your service
   - Go to "Environment" tab
   - Add the following variables:

   | Variable | Value | Description |
   |----------|-------|-------------|
   | `SECRET_KEY` | `your-production-secret-key` | Strong Django secret key |
   | `RENDER_API_KEY` | `your-render-api-key` | Render API key for tenant provisioning |
   | `DEBUG` | `False` | Disable debug mode |
   | `ALLOWED_HOSTS` | `.onrender.com` | Allow Render domains |

### Manual Deployment

If you prefer manual deployment:

1. **Create a new Web Service:**
   - Service Type: Web Service
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python manage.py deploy && gunicorn backend.wsgi:application`

2. **Create a PostgreSQL database:**
   - Service Type: PostgreSQL
   - Plan: Starter (or higher for production)

3. **Create a Redis instance:**
   - Service Type: Redis
   - Plan: Starter

4. **Create a Worker Service:**
   - Service Type: Worker
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `celery -A backend worker -l info`

5. **Link services and configure environment variables**

## 🔧 Environment Configuration

### Required Environment Variables

| Variable | Development | Production | Description |
|----------|-------------|------------|-------------|
| `SECRET_KEY` | `django-insecure-...` | `your-secure-key` | Django secret key |
| `DEBUG` | `True` | `False` | Debug mode |
| `ALLOWED_HOSTS` | `[]` | `.onrender.com` | Allowed hosts |
| `DATABASE_URL` | Not set | Auto-provided | PostgreSQL connection |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Auto-provided | Redis connection |
| `RENDER_API_KEY` | Not required | Required | Render API key |

### Generating a Secure Secret Key

```bash
# Python method
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Or use Django's built-in command
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🔒 Security Checklist

### Before Production Deployment

- [ ] Set `DEBUG=False`
- [ ] Generate and set a strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Set up HTTPS (automatic on Render)
- [ ] Configure `RENDER_API_KEY` for tenant provisioning
- [ ] Review and update Django security settings
- [ ] Set up proper logging
- [ ] Configure database backups

### Security Features Enabled in Production

When `DEBUG=False`, Django automatically enables:

- HTTPS redirects
- HSTS (HTTP Strict Transport Security)
- Secure headers (XSS protection, content type sniffing)
- CSRF protection
- Secure cookie settings

## 📊 Monitoring and Health Checks

### Health Check Endpoint

- **URL**: `/api/health/`
- **Method**: GET
- **Response**: JSON with service status
- **Purpose**: Render deployment monitoring

### Monitoring Setup

1. **Enable Render monitoring:**
   - Automatic health checks via `/api/health/`
   - Log aggregation in Render dashboard
   - Performance metrics

2. **Django Admin monitoring:**
   - Access via `/admin/`
   - Database management
   - Tenant status monitoring

3. **Celery monitoring (optional):**
   ```bash
   # Install Flower for Celery monitoring
   pip install flower
   
   # Start Flower (development only)
   celery -A backend flower
   ```

## 🔄 Database Management

### Migrations

**Development:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Production:**
```bash
# Migrations run automatically during deployment
python manage.py deploy
```

### Database Backup

**PostgreSQL on Render:**
- Automatic daily backups
- Manual backups via Render dashboard
- Point-in-time recovery available

### Database Connection

The application automatically handles database connections:

- **Development**: SQLite (`db.sqlite3`)
- **Production**: PostgreSQL (via `DATABASE_URL`)

## 🚨 Troubleshooting

### Common Deployment Issues

**Build Failures:**
```bash
# Check requirements.txt
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.13+
```

**Database Connection Errors:**
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test connection
python manage.py dbshell
```

**Celery Worker Issues:**
```bash
# Check Redis connection
redis-cli ping

# Verify CELERY_BROKER_URL
echo $CELERY_BROKER_URL
```

**Health Check Failures:**
```bash
# Test health endpoint locally
curl http://localhost:8000/api/health/

# Check logs
python manage.py runserver --verbosity=2
```

### Debug Mode

For troubleshooting, temporarily enable debug mode:

```bash
export DEBUG=True
export CELERY_TASK_ALWAYS_EAGER=True
```

### Logs and Debugging

**Render Logs:**
- View logs in Render dashboard
- Real-time log streaming
- Log retention and search

**Local Debugging:**
```bash
# Enable verbose logging
python manage.py runserver --verbosity=2

# Check Celery logs
celery -A backend worker -l debug
```

## 🔄 Updates and Maintenance

### Updating the Application

1. **Make changes locally:**
   ```bash
   git checkout -b feature/update
   # Make your changes
   git add .
   git commit -m "Update description"
   ```

2. **Test locally:**
   ```bash
   python manage.py test
   python manage.py runserver
   ```

3. **Deploy to production:**
   ```bash
   git push origin main
   # Render will automatically redeploy
   ```

### Database Schema Changes

1. **Create migrations:**
   ```bash
   python manage.py makemigrations
   ```

2. **Test migrations:**
   ```bash
   python manage.py migrate --plan
   ```

3. **Deploy:**
   ```bash
   git add .
   git commit -m "Add database migrations"
   git push origin main
   ```

### Scaling

**Vertical Scaling:**
- Upgrade service plans in Render dashboard
- Increase CPU/memory allocation

**Horizontal Scaling:**
- Add additional worker instances
- Configure load balancing

## 📞 Support

### Getting Help

1. **Check logs** in Render dashboard
2. **Review this documentation**
3. **Test locally** to isolate issues
4. **Create an issue** in the repository

### Useful Commands

```bash
# Check service status
python manage.py check

# Verify database
python manage.py dbshell

# Test Celery
celery -A backend inspect active

# Check migrations
python manage.py showmigrations

# Collect static files
python manage.py collectstatic --noinput
```

---

For more information, see the main [README.md](README.md) and [backend/README.md](backend/README.md) files.
