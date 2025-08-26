import logging
from celery import shared_task
from django.db import transaction
from .models import Tenant
from .render_client import RenderAPIClient

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def provision_tenant_infrastructure(self, tenant_id):
    """
    Background task to provision infrastructure for a tenant on Render.
    
    This task will:
    1. Load and customize the render.yaml blueprint for the tenant
    2. Deploy the blueprint to Render via the Blueprints API
    3. Update the tenant status based on the provisioning result
    4. Store the Render service IDs in the tenant recorddeactivate
    
    Args:
        tenant_id: The ID of the tenant to provision infrastructure for
    """
    try:
        with transaction.atomic():
            tenant = Tenant.objects.get(id=tenant_id)
            
            # Ensure tenant is in PROVISIONING status
            if tenant.status != Tenant.TenantStatus.PROVISIONING:
                logger.warning(f"Tenant {tenant_id} is not in PROVISIONING status. Current status: {tenant.status}")
                return
            
            logger.info(f"Starting infrastructure provisioning for tenant: {tenant.name} (ID: {tenant_id})")
            
            # Initialize Render API client
            render_client = RenderAPIClient()
            
            # Load the base blueprint template
            blueprint = render_client.get_blueprint_template()
            
            # Customize the blueprint for this tenant
            customized_blueprint = render_client.customize_blueprint_for_tenant(
                blueprint=blueprint,
                tenant_slug=tenant.slug,
                custom_plugin_repo=tenant.custom_plugin_repo
            )
            
            # Deploy the blueprint to Render
            deployment_data = render_client.deploy_blueprint(customized_blueprint)
            
            # Extract service IDs from the deployment response
            service_ids = {}
            if 'services' in deployment_data:
                for service_info in deployment_data['services']:
                    if 'service' in service_info:
                        service_name = service_info['service'].get('name', '')
                        service_id = service_info['service'].get('id', '')
                        if service_name and service_id:
                            # Store with the original service name (without tenant suffix)
                            original_name = service_name.replace(f"-{tenant.slug}", "")
                            service_ids[original_name] = service_id
            
            # Update tenant with service IDs and mark as ACTIVE
            tenant.render_service_ids = service_ids
            tenant.status = Tenant.TenantStatus.ACTIVE
            tenant.save()
            
            logger.info(f"Successfully provisioned infrastructure for tenant: {tenant.name} (ID: {tenant_id})")
            logger.info(f"Deployed services: {list(service_ids.keys())}")
            
    except Tenant.DoesNotExist:
        logger.error(f"Tenant with ID {tenant_id} not found")
        raise
    except ValueError as exc:
        # Configuration error (e.g., missing API key)
        logger.error(f"Configuration error for tenant {tenant_id}: {str(exc)}")
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            tenant.status = Tenant.TenantStatus.ERROR
            tenant.save()
        except Tenant.DoesNotExist:
            pass
        raise
    except Exception as exc:
        logger.error(f"Error provisioning infrastructure for tenant {tenant_id}: {str(exc)}")
        
        # Update tenant status to ERROR
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            tenant.status = Tenant.TenantStatus.ERROR
            tenant.save()
        except Tenant.DoesNotExist:
            pass
        
        # Retry the task with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@shared_task
def cleanup_tenant_infrastructure(tenant_id):
    """
    Background task to clean up infrastructure for a tenant on Render.
    
    This task will delete all Render services associated with the tenant.
    
    Args:
        tenant_id: The ID of the tenant to clean up infrastructure for
    """
    try:
        tenant = Tenant.objects.get(id=tenant_id)
        
        logger.info(f"Starting infrastructure cleanup for tenant: {tenant.name} (ID: {tenant_id})")
        
        # Initialize Render API client
        render_client = RenderAPIClient()
        
        # Delete all services associated with this tenant
        _delete_render_services(tenant, render_client)
        
        # Update tenant status
        tenant.status = Tenant.TenantStatus.SUSPENDED
        tenant.render_service_ids = {}
        tenant.save()
        
        logger.info(f"Successfully cleaned up infrastructure for tenant: {tenant.name} (ID: {tenant_id})")
        
    except Tenant.DoesNotExist:
        logger.error(f"Tenant with ID {tenant_id} not found")
        raise
    except Exception as exc:
        logger.error(f"Error cleaning up infrastructure for tenant {tenant_id}: {str(exc)}")
        raise

def _delete_render_services(tenant, render_client):
    """
    Delete Render services for the tenant.
    
    Args:
        tenant: The Tenant instance
        render_client: The RenderAPIClient instance
    """
    if not tenant.render_service_ids:
        logger.info(f"No services to delete for tenant {tenant.name}")
        return
    
    logger.info(f"Deleting Render services for tenant: {tenant.name}")
    
    deleted_count = 0
    for service_name, service_id in tenant.render_service_ids.items():
        try:
            render_client.delete_service(service_id)
            deleted_count += 1
            logger.info(f"Deleted service {service_name} (ID: {service_id})")
        except Exception as e:
            logger.error(f"Failed to delete service {service_name} (ID: {service_id}): {e}")
    
    logger.info(f"Deleted {deleted_count} out of {len(tenant.render_service_ids)} services for tenant {tenant.name}")

@shared_task
def check_tenant_service_status(tenant_id):
    """
    Background task to check the status of all services for a tenant.
    
    This task can be used for monitoring and health checks.
    
    Args:
        tenant_id: The ID of the tenant to check service status for
    """
    try:
        tenant = Tenant.objects.get(id=tenant_id)
        
        if not tenant.render_service_ids:
            logger.info(f"No services to check for tenant {tenant.name}")
            return
        
        render_client = RenderAPIClient()
        
        service_statuses = {}
        for service_name, service_id in tenant.render_service_ids.items():
            status_info = render_client.get_service_status(service_id)
            if status_info:
                service_statuses[service_name] = {
                    'status': status_info.get('status'),
                    'url': status_info.get('service', {}).get('serviceUrl'),
                    'last_deploy': status_info.get('service', {}).get('updatedAt')
                }
        
        logger.info(f"Service statuses for tenant {tenant.name}: {service_statuses}")
        
        # You could store these statuses in the tenant model or send alerts
        # based on the status information
        
    except Tenant.DoesNotExist:
        logger.error(f"Tenant with ID {tenant_id} not found")
        raise
    except Exception as exc:
        logger.error(f"Error checking service status for tenant {tenant_id}: {str(exc)}")
        raise
