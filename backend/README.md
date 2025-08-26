# Render Control Plane - Backend

This Django backend provides the core API and business logic for the Render Control Plane system.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Django REST   │    │   Celery        │    │   PostgreSQL    │
│   API           │◄──►│   Background    │◄──►│   Database      │
│   (Django)      │    │   Tasks         │    │   (Production)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Redis         │    │   Render API    │    │   SQLite        │
│   (Message      │    │   Integration   │    │   (Development) │
│   Broker)       │    │   (Tasks)       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Redis server
- PostgreSQL (for production)

### Local Development Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```bash
   export SECRET_KEY="your-development-secret-key"
   export DEBUG="True"
   export CELERY_BROKER_URL="redis://localhost:6379/0"
   ```

5. **Start Redis:**
   ```bash
   # macOS
   brew install redis && brew services start redis
   
   # Ubuntu/Debian
   sudo apt-get install redis-server && sudo systemctl start redis
   ```

6. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

7. **Start Celery worker (in separate terminal):**
   ```bash
   cd backend
   source venv/bin/activate
   celery -A backend worker -l info
   ```

8. **Start development server:**
   ```bash
   python manage.py runserver
   ```

## 📚 API Reference

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-app-name.onrender.com`

### Authentication
Currently open for development. Implement authentication for production.

### Endpoints

#### Health Check
```http
GET /api/health/
```

**Response:**
```json
{
    "status": "healthy",
    "message": "Control Plane API is running"
}
```

#### Tenant Management

**Create Tenant**
```http
POST /api/tenants/
Content-Type: application/json

{
    "name": "Acme Corporation",
    "slug": "acme-corp"  // Optional
}
```

**Get Tenant Status**
```http
GET /api/tenants/{id}/status/
```

**List All Tenants**
```http
GET /api/tenants/
```

**Get Tenant Details**
```http
GET /api/tenants/{id}/
```

**Delete Tenant**
```http
DELETE /api/tenants/{id}/
```

### Tenant Statuses

- **PROVISIONING**: Infrastructure is being created
- **ACTIVE**: Infrastructure is ready and operational
- **SUSPENDED**: Tenant is suspended (infrastructure cleaned up)
- **ERROR**: An error occurred during provisioning

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Django secret key | Yes | Development default |
| `DEBUG` | Debug mode | No | `True` |
| `ALLOWED_HOSTS` | Comma-separated host list | No | `[]` |
| `DATABASE_URL` | PostgreSQL connection string | Production | SQLite |
| `CELERY_BROKER_URL` | Redis connection string | Yes | `redis://localhost:6379/0` |
| `RENDER_API_KEY` | Render API key for provisioning | Yes | None |

### Database Configuration

The application automatically switches between databases:

- **Development**: SQLite (`db.sqlite3`)
- **Production**: PostgreSQL (via `DATABASE_URL`)

### Celery Configuration

- **Broker**: Redis
- **Result Backend**: Redis
- **Task Serialization**: JSON
- **Worker Concurrency**: 4
- **Queue**: `infrastructure` for provisioning tasks

## 🗄️ Models

### Tenant Model

```python
class Tenant(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    status = models.CharField(max_length=20, choices=TenantStatus.choices)
    render_service_ids = models.JSONField(default=dict)
    custom_plugin_repo = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 🔄 Background Tasks

### Available Tasks

- **`provision_tenant_infrastructure`**: Creates Render services for a tenant
- **`cleanup_tenant_infrastructure`**: Removes Render services for a tenant

### Task Queue

Tasks are routed to the `infrastructure` queue for better resource management.

### Running Tasks Manually

```bash
# Start Celery worker
celery -A backend worker -l info

# Monitor tasks
celery -A backend flower  # Optional: web-based monitoring
```

## 🧪 Testing

### Running Tests
```bash
python manage.py test
```

### Development Testing (without Celery)
```bash
export CELERY_TASK_ALWAYS_EAGER=True
python manage.py test
```

### Test Coverage
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## 🛠️ Development

### Code Style

This project follows PEP 8 style guidelines. Recommended tools:

```bash
# Install development tools
pip install black flake8 isort

# Format code
black .
isort .

# Check code style
flake8 .
```

### Management Commands

**Deployment Command**
```bash
python manage.py deploy
```
Handles database migrations and static file collection for production.

**Custom Commands**
- `deploy`: Production deployment tasks

### Logging

Logging is configured for both development and production:

- **Development**: Console output with DEBUG level
- **Production**: Structured logging with INFO level
- **Celery**: Task-specific logging with error tracking

## 📊 Monitoring

### Health Checks
- **Endpoint**: `/api/health/`
- **Purpose**: Render deployment monitoring
- **Response**: Service status and uptime

### Django Admin
- **URL**: `/admin/`
- **Purpose**: Database management and monitoring
- **Access**: Create superuser with `python manage.py createsuperuser`

## 🔒 Security

### Production Security Features

When `DEBUG=False`, Django automatically enables:

- HTTPS redirects
- HSTS (HTTP Strict Transport Security)
- Secure headers (XSS protection, content type sniffing)
- CSRF protection
- Secure cookie settings

### Environment Variable Security

- Sensitive variables are loaded from environment
- Never commit secrets to version control
- Use Render dashboard for production secrets

## 🚧 Development Roadmap

### Completed ✅
- [x] Django REST API setup
- [x] Tenant model and management
- [x] Celery background task integration
- [x] PostgreSQL production database setup
- [x] Health check endpoints
- [x] Security hardening for production
- [x] Deployment management commands

### In Progress 🔄
- [ ] Render API integration for actual service provisioning
- [ ] Tenant-specific environment variable management
- [ ] Cost tracking and reporting

### Planned 📋
- [ ] Authentication and authorization system
- [ ] Tenant suspension and reactivation
- [ ] Monitoring and alerting integration
- [ ] Backup and restore functionality
- [ ] API rate limiting and throttling

## 📁 Project Structure

```
backend/
├── backend/                 # Django project settings
│   ├── settings.py         # Main settings file
│   ├── urls.py             # Main URL configuration
│   ├── wsgi.py             # WSGI application
│   └── celery.py           # Celery configuration
├── tenants/                # Main Django app
│   ├── models.py           # Tenant model
│   ├── views.py            # API views
│   ├── serializers.py      # DRF serializers
│   ├── tasks.py            # Celery background tasks
│   ├── urls.py             # App URL configuration
│   └── management/         # Custom management commands
│       └── commands/
│           └── deploy.py   # Deployment command
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── db.sqlite3             # Development database
```

## 🆘 Troubleshooting

### Common Issues

**Database Connection Errors**
- Check `DATABASE_URL` environment variable
- Ensure PostgreSQL is running (production)
- Verify database credentials

**Celery Worker Issues**
- Check Redis connection (`CELERY_BROKER_URL`)
- Ensure Redis server is running
- Check task queue configuration

**Migration Errors**
- Run `python manage.py migrate --plan` to preview
- Check for conflicting migrations
- Use `python manage.py showmigrations` to see status

### Debug Mode

For debugging, set:
```bash
export DEBUG=True
export CELERY_TASK_ALWAYS_EAGER=True
```

This will:
- Enable Django debug mode
- Run Celery tasks synchronously
- Show detailed error messages

---

For more information, see the main [README.md](../README.md) file.
