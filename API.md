# API Documentation

This document provides comprehensive documentation for the Render Control Plane API.

## 📋 Overview

- **Base URL**: `https://your-app-name.onrender.com` (production) or `http://localhost:8000` (development)
- **Content Type**: `application/json`
- **Authentication**: Currently open (implement authentication for production)

## 🔗 Endpoints

### Health Check

#### GET `/api/health/`

Returns the health status of the API service.

**Response:**
```json
{
    "status": "healthy",
    "message": "Control Plane API is running"
}
```

**Status Codes:**
- `200 OK`: Service is healthy

---

### Tenant Management

#### GET `/api/tenants/`

Retrieve a list of all tenants.

**Query Parameters:**
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page (default: 10)

**Response:**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
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
            "custom_plugin_repo": "",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:35:00Z"
        },
        {
            "id": 2,
            "name": "Tech Startup Inc",
            "slug": "tech-startup",
            "status": "PROVISIONING",
            "render_service_ids": {},
            "custom_plugin_repo": "",
            "created_at": "2024-01-15T11:00:00Z",
            "updated_at": "2024-01-15T11:00:00Z"
        }
    ]
}
```

**Status Codes:**
- `200 OK`: Successfully retrieved tenants

---

#### POST `/api/tenants/`

Create a new tenant and initiate infrastructure provisioning.

**Request Body:**
```json
{
    "name": "Acme Corporation",
    "slug": "acme-corp"
}
```

**Field Descriptions:**
- `name` (required): Customer/tenant name (minimum 2 characters)
- `slug` (optional): Custom slug for the tenant (auto-generated if not provided)

**Response (201 Created):**
```json
{
    "id": 1,
    "name": "Acme Corporation",
    "slug": "acme-corp",
    "status": "PROVISIONING",
    "render_service_ids": {},
    "custom_plugin_repo": "",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `201 Created`: Tenant created successfully
- `400 Bad Request`: Validation error

**Error Response (400):**
```json
{
    "error": "Customer name is required"
}
```

**Common Error Messages:**
- `"Customer name is required"`
- `"Customer name must be at least 2 characters long"`
- `"A tenant with this name already exists"`
- `"A tenant with this slug already exists"`

---

#### GET `/api/tenants/{id}/`

Retrieve details of a specific tenant.

**Path Parameters:**
- `id`: Tenant ID (integer)

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
    "custom_plugin_repo": "",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
}
```

**Status Codes:**
- `200 OK`: Successfully retrieved tenant
- `404 Not Found`: Tenant not found

---

#### GET `/api/tenants/{id}/status/`

Get the current status of a tenant's infrastructure provisioning.

**Path Parameters:**
- `id`: Tenant ID (integer)

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

**Status Codes:**
- `200 OK`: Successfully retrieved status
- `404 Not Found`: Tenant not found

---

#### PUT `/api/tenants/{id}/`

Update an existing tenant.

**Path Parameters:**
- `id`: Tenant ID (integer)

**Request Body:**
```json
{
    "name": "Acme Corporation Updated",
    "custom_plugin_repo": "https://github.com/acme/custom-plugins"
}
```

**Field Descriptions:**
- `name` (optional): Updated tenant name
- `custom_plugin_repo` (optional): URL to custom plugin repository

**Response:**
```json
{
    "id": 1,
    "name": "Acme Corporation Updated",
    "slug": "acme-corp",
    "status": "ACTIVE",
    "render_service_ids": {
        "web_service": "web-acme-corp-1",
        "database": "db-acme-corp-1",
        "redis": "redis-acme-corp-1"
    },
    "custom_plugin_repo": "https://github.com/acme/custom-plugins",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Tenant updated successfully
- `400 Bad Request`: Validation error
- `404 Not Found`: Tenant not found

---

#### DELETE `/api/tenants/{id}/`

Delete a tenant and clean up its infrastructure.

**Path Parameters:**
- `id`: Tenant ID (integer)

**Response:**
```json
{
    "message": "Tenant deletion initiated",
    "tenant_id": 1
}
```

**Status Codes:**
- `202 Accepted`: Deletion initiated successfully
- `404 Not Found`: Tenant not found

---

## 📊 Data Models

### Tenant Model

```json
{
    "id": "integer",
    "name": "string (max 255 characters)",
    "slug": "string (unique, URL-safe)",
    "status": "string (PROVISIONING|ACTIVE|SUSPENDED|ERROR)",
    "render_service_ids": "object (JSON)",
    "custom_plugin_repo": "string (URL, optional)",
    "created_at": "datetime (ISO 8601)",
    "updated_at": "datetime (ISO 8601)"
}
```

### Tenant Status Values

- **PROVISIONING**: Infrastructure is being created
- **ACTIVE**: Infrastructure is ready and operational
- **SUSPENDED**: Tenant is suspended (infrastructure cleaned up)
- **ERROR**: An error occurred during provisioning

### Render Service IDs Structure

```json
{
    "web_service": "string",
    "database": "string",
    "redis": "string",
    "worker": "string"
}
```

## 🔄 Background Tasks

### Infrastructure Provisioning

When a tenant is created, the following background task is triggered:

- **Task Name**: `provision_tenant_infrastructure`
- **Queue**: `infrastructure`
- **Process**: Creates Render services using tenant-specific blueprints

### Infrastructure Cleanup

When a tenant is deleted, the following background task is triggered:

- **Task Name**: `cleanup_tenant_infrastructure`
- **Queue**: `infrastructure`
- **Process**: Removes all tenant services from Render

## 🚨 Error Handling

### Standard Error Response Format

```json
{
    "error": "Error message description",
    "detail": "Additional error details (optional)",
    "field": "field_name (for validation errors)"
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `202 Accepted`: Request accepted for processing
- `400 Bad Request`: Client error (validation, malformed request)
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Common Error Scenarios

1. **Validation Errors (400)**
   - Missing required fields
   - Invalid field values
   - Duplicate names/slugs

2. **Not Found Errors (404)**
   - Tenant ID doesn't exist
   - Resource not found

3. **Server Errors (500)**
   - Database connection issues
   - External service failures
   - Background task failures

## 📝 Usage Examples

### cURL Examples

**Create a new tenant:**
```bash
curl -X POST https://your-app-name.onrender.com/api/tenants/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "slug": "acme-corp"
  }'
```

**Get all tenants:**
```bash
curl -X GET https://your-app-name.onrender.com/api/tenants/
```

**Get tenant status:**
```bash
curl -X GET https://your-app-name.onrender.com/api/tenants/1/status/
```

**Update tenant:**
```bash
curl -X PUT https://your-app-name.onrender.com/api/tenants/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation Updated"
  }'
```

**Delete tenant:**
```bash
curl -X DELETE https://your-app-name.onrender.com/api/tenants/1/
```

### Python Examples

**Using requests library:**
```python
import requests

BASE_URL = "https://your-app-name.onrender.com/api"

# Create tenant
response = requests.post(f"{BASE_URL}/tenants/", json={
    "name": "Acme Corporation",
    "slug": "acme-corp"
})
tenant = response.json()

# Get tenant status
tenant_id = tenant["id"]
status_response = requests.get(f"{BASE_URL}/tenants/{tenant_id}/status/")
status = status_response.json()

# List all tenants
tenants_response = requests.get(f"{BASE_URL}/tenants/")
tenants = tenants_response.json()["results"]
```

### JavaScript Examples

**Using fetch API:**
```javascript
const BASE_URL = "https://your-app-name.onrender.com/api";

// Create tenant
async function createTenant(name, slug) {
    const response = await fetch(`${BASE_URL}/tenants/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, slug })
    });
    return response.json();
}

// Get tenant status
async function getTenantStatus(tenantId) {
    const response = await fetch(`${BASE_URL}/tenants/${tenantId}/status/`);
    return response.json();
}

// List all tenants
async function listTenants() {
    const response = await fetch(`${BASE_URL}/tenants/`);
    const data = await response.json();
    return data.results;
}
```

## 🔒 Security Considerations

### Current State
- API is currently open (no authentication)
- Suitable for development and testing

### Production Recommendations
- Implement authentication (JWT, API keys, OAuth)
- Add rate limiting
- Enable CORS configuration
- Implement request validation
- Add audit logging

## 📊 Monitoring and Health

### Health Check
- **Endpoint**: `/api/health/`
- **Purpose**: Monitor service availability
- **Frequency**: Check every 30 seconds
- **Expected Response**: `{"status": "healthy", "message": "Control Plane API is running"}`

### Performance Metrics
- Response times
- Error rates
- Background task completion rates
- Database connection health

## 🔄 Webhooks (Future Feature)

Planned webhook endpoints for real-time notifications:

- **Tenant Created**: `POST /api/webhooks/tenant-created`
- **Tenant Updated**: `POST /api/webhooks/tenant-updated`
- **Tenant Deleted**: `POST /api/webhooks/tenant-deleted`
- **Provisioning Complete**: `POST /api/webhooks/provisioning-complete`
- **Provisioning Failed**: `POST /api/webhooks/provisioning-failed`

---

For deployment and setup instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).
