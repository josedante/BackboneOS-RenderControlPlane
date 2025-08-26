# Render Control Plane - Backend

This Django backend provides a control plane for managing multi-tenant infrastructure on Render.

## Features

- **Tenant Management**: Create and manage tenants with automatic infrastructure provisioning
- **Background Processing**: Celery-based background tasks for infrastructure creation
- **REST API**: Full REST API for tenant operations
- **Status Tracking**: Real-time status tracking for infrastructure provisioning

## Setup

### Prerequisites

- Python 3.8+
- Redis (for Celery message broker)
- PostgreSQL (recommended for production)

### Installation

1. **Clone the repository and navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start Redis (required for Celery):**
   ```bash
   # On macOS with Homebrew:
   brew install redis
   brew services start redis
   
   # On Ubuntu/Debian:
   sudo apt-get install redis-server
   sudo systemctl start redis
   ```

6. **Start the Celery worker (in a separate terminal):**
   ```bash
   cd backend
   source venv/bin/activate
   celery -A backend worker -l info
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

## API Usage

### Creating a Tenant

**POST** `/api/tenants/`

**Request Body:**
```json
{
    "name": "Acme Corporation",
    "slug": "acme-corp"  // Optional, will be auto-generated if not provided
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

### Checking Tenant Status

**GET** `/api/tenants/{id}/status/`

**Response:**
```json
{
    "id": 1,
    "name": "Acme Corporation",
    "slug": "acme-corp",
    "status": "ACTIVE",
    "render_service_ids": {
        "web_service": "web-acme-corp-1",
        "database": "db-acme-corp-1",
        "redis": "redis-acme-corp-1"
    },
    "created_at": "2024-01-15T10:30:00Z"
}
```

### Listing All Tenants

**GET** `/api/tenants/`

### Getting Tenant Details

**GET** `/api/tenants/{id}/`

## Tenant Statuses

- **PROVISIONING**: Infrastructure is being created
- **ACTIVE**: Infrastructure is ready and tenant is operational
- **SUSPENDED**: Tenant is suspended (infrastructure cleaned up)
- **ERROR**: An error occurred during provisioning

## Background Tasks

The system uses Celery for background processing of infrastructure provisioning:

- **provision_tenant_infrastructure**: Creates Render services for a tenant
- **cleanup_tenant_infrastructure**: Removes Render services for a tenant

### Task Queue

Tasks are routed to the `infrastructure` queue for better resource management.

## Configuration

### Environment Variables

Set these environment variables for production:

```bash
export DJANGO_SECRET_KEY="your-secret-key"
export CELERY_BROKER_URL="redis://your-redis-host:6379/0"
export DATABASE_URL="postgresql://user:password@host:port/dbname"
```

### Celery Configuration

The Celery configuration is in `backend/settings.py`. Key settings:

- `CELERY_BROKER_URL`: Redis connection string
- `CELERY_RESULT_BACKEND`: Redis for storing task results
- `CELERY_TASK_ALWAYS_EAGER`: Set to `True` for testing without Celery worker

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

This project follows PEP 8 style guidelines. Use a linter like `flake8` or `black` for code formatting.

## TODO

- [ ] Implement actual Render API integration
- [ ] Add authentication and authorization
- [ ] Add tenant-specific environment variables
- [ ] Implement tenant suspension and reactivation
- [ ] Add monitoring and alerting
- [ ] Add backup and restore functionality
