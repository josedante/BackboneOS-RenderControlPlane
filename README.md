# Render Control Plane

A Django-based control plane for managing multi-tenant infrastructure on Render. This system automates the provisioning, management, and decommissioning of tenant-specific infrastructure stacks.

## 🚀 Features

### Core Functionality
- **Tenant Provisioning**: Programmatically create dedicated infrastructure stacks for new tenants using Render blueprints
- **Configuration Management**: Dynamically inject customer-specific configurations into deployment templates
- **Tenant De-provisioning**: Securely remove all tenant services when subscriptions are cancelled
- **Status Tracking**: Real-time monitoring of infrastructure provisioning status

### Customer & Tenant Management
- **Service ID Mapping**: Maintain database mappings linking customers to their Render service IDs
- **Plugin & Customization Management**: Track custom code plugins per customer for build customization
- **Cost Allocation**: Calculate precise infrastructure costs per tenant using Render API data

### Operational & Business Logic
- **REST API Interface**: Complete API for tenant management operations
- **Onboarding Automation**: Endpoint integration for customer signup workflows
- **Lifecycle Management**: Handle upgrades, downgrades, and service suspension

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Control       │    │   Render        │
│   (Customer     │◄──►│   Plane API     │◄──►│   Platform      │
│   Portal)       │    │   (Django)      │    │   (Infra)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Celery        │
                       │   (Background   │
                       │   Tasks)        │
                       └─────────────────┘
```

## 🛠️ Technology Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **Message Broker**: Redis
- **Background Tasks**: Celery
- **Deployment**: Render (with render.yaml blueprint)
- **API Documentation**: Django REST Framework browsable API

## 📋 Prerequisites

- Python 3.13+
- Redis server
- PostgreSQL (for production)
- Render account with API access

## 🚀 Quick Start

### Local Development

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Render-ControlPlane
   ```

2. **Set up the backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   export SECRET_KEY="your-development-secret-key"
   export DEBUG="True"
   export CELERY_BROKER_URL="redis://localhost:6379/0"
   ```

4. **Start Redis:**
   ```bash
   # macOS
   brew install redis && brew services start redis
   
   # Ubuntu/Debian
   sudo apt-get install redis-server && sudo systemctl start redis
   ```

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Start Celery worker (in separate terminal):**
   ```bash
   cd backend
   source venv/bin/activate
   celery -A backend worker -l info
   ```

7. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

### Production Deployment

The project includes a complete `render.yaml` blueprint for deployment on Render:

1. **Deploy to Render:**
   ```bash
   # Push your code to a Git repository
   git push origin main
   
   # Connect your repository to Render
   # Render will automatically deploy using render.yaml
   ```

2. **Configure environment variables in Render dashboard:**
   - `SECRET_KEY`: Strong, unique Django secret key
   - `RENDER_API_KEY`: Your Render API key for tenant provisioning
   - `DEBUG`: Set to "False" for production
   - `ALLOWED_HOSTS`: Set to ".onrender.com"

## 📚 API Documentation

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-app-name.onrender.com`

### Authentication
Currently, the API is open for development. Implement authentication for production use.

### Endpoints

#### Health Check
```http
GET /api/health/
```
Returns service health status.

#### Create Tenant
```http
POST /api/tenants/
Content-Type: application/json

{
    "name": "Acme Corporation",
    "slug": "acme-corp"  // Optional
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "name": "Acme Corporation",
    "slug": "acme-corp",
    "status": "PROVISIONING",
    "render_service_ids": {},
    "created_at": "2024-01-15T10:30:00Z"
}
```

#### Get Tenant Status
```http
GET /api/tenants/{id}/status/
```

#### List All Tenants
```http
GET /api/tenants/
```

#### Get Tenant Details
```http
GET /api/tenants/{id}/
```

#### Delete Tenant
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

The application automatically switches between databases based on environment:

- **Development**: SQLite (`db.sqlite3`)
- **Production**: PostgreSQL (via `DATABASE_URL`)

### Celery Configuration

- **Broker**: Redis
- **Result Backend**: Redis
- **Task Serialization**: JSON
- **Worker Concurrency**: 4
- **Queue**: `infrastructure` for provisioning tasks

## 🏗️ Deployment Architecture

The `render.yaml` defines a complete infrastructure stack:

1. **PostgreSQL Database** (`control-plane-db`)
   - Private network access only
   - Starter plan

2. **Redis Cache** (`control-plane-redis`)
   - Private network access only
   - Starter plan

3. **Django Web Service** (`control-plane-backend`)
   - Python 3.13 runtime
   - Gunicorn WSGI server
   - Health check endpoint
   - Auto-scaling enabled

4. **Celery Worker** (`control-plane-worker`)
   - Background task processing
   - Infrastructure provisioning
   - Tenant management operations

## 🔒 Security

### Production Security Features

When `DEBUG=False`, Django automatically enables:

- HTTPS redirects
- HSTS (HTTP Strict Transport Security)
- Secure headers (XSS protection, content type sniffing)
- CSRF protection
- Secure cookie settings

### Environment Variable Security

- Sensitive variables (`SECRET_KEY`, `RENDER_API_KEY`) are marked as `sync: false` in render.yaml
- These must be set manually in the Render dashboard
- Never commit secrets to version control

## 🧪 Testing

### Running Tests
```bash
cd backend
python manage.py test
```

### Development Testing
```bash
# Test without Celery worker
export CELERY_TASK_ALWAYS_EAGER=True
python manage.py test
```

## 📊 Monitoring

### Health Checks
- **Endpoint**: `/api/health/`
- **Purpose**: Render deployment monitoring
- **Response**: Service status and uptime

### Logging
- Django logging configured for production
- Celery task logging with detailed error tracking
- Database connection monitoring

## 🔄 Background Tasks

### Infrastructure Provisioning
- **Task**: `provision_tenant_infrastructure`
- **Queue**: `infrastructure`
- **Process**: Creates Render services using tenant-specific blueprints

### Infrastructure Cleanup
- **Task**: `cleanup_tenant_infrastructure`
- **Queue**: `infrastructure`
- **Process**: Removes all tenant services from Render

## 🚧 Development Roadmap

### Completed ✅
- [x] Django REST API setup
- [x] Tenant model and management
- [x] Celery background task integration
- [x] Render deployment configuration
- [x] PostgreSQL production database setup
- [x] Health check endpoints
- [x] Security hardening for production

### In Progress 🔄
- [ ] Render API integration for actual service provisioning
- [ ] Tenant-specific environment variable management
- [ ] Cost tracking and reporting

### Planned 📋
- [ ] Authentication and authorization system
- [ ] Tenant suspension and reactivation
- [ ] Monitoring and alerting integration
- [ ] Backup and restore functionality
- [ ] Multi-region deployment support
- [ ] API rate limiting and throttling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/api/`
- Review the Django admin interface at `/admin/`

---

**Built with ❤️ for multi-tenant SaaS platforms**