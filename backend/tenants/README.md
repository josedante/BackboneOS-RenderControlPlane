# BackboneOS Tenant Provisioning System

A robust, blueprint-driven infrastructure provisioning system for multi-tenant Django applications on Render.

## 🚀 Features

- **Blueprint-Driven Provisioning**: Uses Render Blueprints API to deploy complete infrastructure stacks
- **Custom Plugin Support**: Automatically integrates custom code repositories for personalized tenant experiences
- **Atomic Operations**: Database transactions ensure consistency during provisioning
- **Retry Logic**: Exponential backoff for handling transient failures
- **Service Monitoring**: Built-in health checks and status monitoring
- **Cleanup Operations**: Complete infrastructure teardown when tenants are suspended

## 📋 Prerequisites

1. **Render API Key**: Set the `RENDER_API_KEY` environment variable
2. **Blueprint Template**: The `base_crm_render.yaml` file must be present
3. **Dependencies**: Install required packages from `requirements.txt`

## 🏗️ Architecture

### Core Components

1. **RenderAPIClient** (`render_client.py`)
   - Handles all Render API interactions
   - Manages authentication and request/response handling
   - Provides blueprint customization and deployment

2. **Tenant Model** (`models.py`)
   - Stores tenant information and service IDs
   - Tracks provisioning status
   - Supports custom plugin repositories

3. **Celery Tasks** (`tasks.py`)
   - `provision_tenant_infrastructure`: Deploys tenant infrastructure
   - `cleanup_tenant_infrastructure`: Removes tenant infrastructure
   - `check_tenant_service_status`: Monitors service health

### Data Flow

```
Tenant Creation → Blueprint Customization → Render Deployment → Status Update
```

## 🔧 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export RENDER_API_KEY="your_render_api_key_here"
```

### 3. Run Migrations

```bash
python manage.py makemigrations tenants
python manage.py migrate
```

## 📖 Usage

### Basic Tenant Provisioning

```python
from tenants.models import Tenant
from tenants.tasks import provision_tenant_infrastructure

# Create a tenant
tenant = Tenant.objects.create(
    name="Acme Corporation",
    slug="acme-corp"
)

# Provision infrastructure (asynchronous)
provision_tenant_infrastructure.delay(tenant.id)
```

### Tenant with Custom Plugins

```python
# Create a tenant with custom plugins
tenant = Tenant.objects.create(
    name="Custom Company",
    slug="custom-co",
    custom_plugin_repo="https://github.com/company/custom-plugins.git"
)

# The provisioning system will automatically:
# 1. Clone the custom plugin repository during build
# 2. Set up the CUSTOM_PLUGINS_PATH environment variable
# 3. Integrate the plugins into the deployment
```

### Monitoring and Cleanup

```python
from tenants.tasks import check_tenant_service_status, cleanup_tenant_infrastructure

# Check service status
check_tenant_service_status.delay(tenant.id)

# Clean up infrastructure
cleanup_tenant_infrastructure.delay(tenant.id)
```

## 🔄 Blueprint Customization

The system automatically customizes the `base_crm_render.yaml` blueprint for each tenant:

### Service Naming
- Original: `backboneos-backend`
- Customized: `backboneos-backend-acme-corp`

### Environment Variables
- `TENANT_SLUG`: The tenant's unique identifier
- `TENANT_NAME`: Human-readable tenant name
- `CUSTOM_PLUGINS_PATH`: Path to custom plugins (if applicable)

### Custom Plugin Integration
When a tenant has a `custom_plugin_repo`, the system:

1. Modifies the build command to clone the repository
2. Sets up the plugin path environment variable
3. Ensures plugins are available during deployment

## 🛡️ Error Handling

### Retry Logic
- **Max Retries**: 3 attempts
- **Backoff Strategy**: Exponential (60s, 120s, 240s)
- **Error States**: Tenant status updated to `ERROR` on failure

### Transaction Safety
- All database operations wrapped in atomic transactions
- Rollback on failure ensures data consistency
- Service IDs only saved after successful deployment

## 📊 Monitoring

### Tenant Status Tracking
- `PROVISIONING`: Infrastructure being deployed
- `ACTIVE`: Infrastructure ready and operational
- `SUSPENDED`: Infrastructure cleaned up
- `ERROR`: Provisioning failed

### Service Health Checks
The `check_tenant_service_status` task provides:
- Service status information
- Service URLs
- Last deployment timestamps

## 🔍 Example Implementation

See `example_usage.py` for a complete demonstration of the system.

```bash
# Run the example
python tenants/example_usage.py
```

## 🚨 Important Notes

### Security
- Never commit API keys to version control
- Use environment variables for sensitive configuration
- Consider IP restrictions for production deployments

### Cost Management
- Monitor Render service usage
- Implement automatic cleanup for inactive tenants
- Use appropriate service plans for your needs

### Scaling Considerations
- Blueprint deployments can take several minutes
- Consider queue management for high-volume provisioning
- Implement rate limiting for API calls

## 🐛 Troubleshooting

### Common Issues

1. **Missing API Key**
   ```
   ValueError: RENDER_API_KEY environment variable is required
   ```
   Solution: Set the environment variable

2. **Blueprint Not Found**
   ```
   FileNotFoundError: Blueprint template not found
   ```
   Solution: Ensure `base_crm_render.yaml` is in the correct location

3. **Service Deletion Fails**
   ```
   Service not found (may already be deleted)
   ```
   This is normal - services may already be cleaned up

### Debug Mode

Enable detailed logging by setting the log level:

```python
import logging
logging.getLogger('tenants').setLevel(logging.DEBUG)
```

## 🤝 Contributing

1. Follow the existing code structure
2. Add comprehensive error handling
3. Include logging for all operations
4. Test with both standard and custom plugin tenants
5. Update documentation for new features

## 📄 License

This system is part of the BackboneOS project and follows the same licensing terms.
