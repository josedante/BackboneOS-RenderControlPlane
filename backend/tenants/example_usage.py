"""
Example usage of the tenant provisioning system.

This script demonstrates how to:
1. Create a tenant with custom plugins
2. Provision infrastructure using the blueprint
3. Clean up infrastructure when done
"""

import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from tenants.models import Tenant
from tenants.tasks import provision_tenant_infrastructure, cleanup_tenant_infrastructure, check_tenant_service_status

def create_tenant_with_custom_plugins():
    """
    Example: Create a tenant that needs custom plugins.
    """
    print("=== Creating Tenant with Custom Plugins ===")
    
    # Create a tenant with custom plugin repository
    tenant = Tenant.objects.create(
        name="Acme Corporation",
        slug="acme-corp",
        custom_plugin_repo="https://github.com/acme/custom-crm-plugins.git"
    )
    
    print(f"Created tenant: {tenant.name} (ID: {tenant.id})")
    print(f"Custom plugin repo: {tenant.custom_plugin_repo}")
    
    return tenant

def create_standard_tenant():
    """
    Example: Create a tenant without custom plugins.
    """
    print("=== Creating Standard Tenant ===")
    
    # Create a tenant without custom plugins
    tenant = Tenant.objects.create(
        name="Standard Company",
        slug="standard-co"
    )
    
    print(f"Created tenant: {tenant.name} (ID: {tenant.id})")
    print("No custom plugins configured")
    
    return tenant

def provision_tenant_example(tenant):
    """
    Example: Provision infrastructure for a tenant.
    """
    print(f"\n=== Provisioning Infrastructure for {tenant.name} ===")
    
    # Trigger the provisioning task
    # In a real application, this would be called asynchronously
    print("Starting provisioning task...")
    
    # For demonstration, we'll call it directly
    # In production, you would use: provision_tenant_infrastructure.delay(tenant.id)
    try:
        provision_tenant_infrastructure(tenant.id)
        print("✅ Provisioning completed successfully!")
        
        # Refresh the tenant object to see updated status
        tenant.refresh_from_db()
        print(f"Tenant status: {tenant.status}")
        print(f"Service IDs: {tenant.render_service_ids}")
        
    except Exception as e:
        print(f"❌ Provisioning failed: {e}")
        tenant.refresh_from_db()
        print(f"Tenant status: {tenant.status}")

def check_service_status_example(tenant):
    """
    Example: Check the status of tenant services.
    """
    print(f"\n=== Checking Service Status for {tenant.name} ===")
    
    try:
        check_tenant_service_status(tenant.id)
        print("✅ Service status check completed!")
    except Exception as e:
        print(f"❌ Service status check failed: {e}")

def cleanup_tenant_example(tenant):
    """
    Example: Clean up infrastructure for a tenant.
    """
    print(f"\n=== Cleaning Up Infrastructure for {tenant.name} ===")
    
    try:
        cleanup_tenant_infrastructure(tenant.id)
        print("✅ Cleanup completed successfully!")
        
        # Refresh the tenant object to see updated status
        tenant.refresh_from_db()
        print(f"Tenant status: {tenant.status}")
        print(f"Service IDs: {tenant.render_service_ids}")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

def main():
    """
    Main example function demonstrating the complete workflow.
    """
    print("🚀 BackboneOS Tenant Provisioning System Demo")
    print("=" * 50)
    
    # Set up environment variable for Render API (required for actual deployment)
    if not os.getenv('RENDER_API_KEY'):
        print("⚠️  RENDER_API_KEY not set. This demo will show the structure but won't make actual API calls.")
        print("   Set RENDER_API_KEY environment variable to test with real Render deployment.")
    
    # Example 1: Tenant with custom plugins
    tenant_with_plugins = create_tenant_with_custom_plugins()
    
    # Example 2: Standard tenant
    standard_tenant = create_standard_tenant()
    
    # Provision both tenants
    provision_tenant_example(tenant_with_plugins)
    provision_tenant_example(standard_tenant)
    
    # Check service status
    check_service_status_example(tenant_with_plugins)
    check_service_status_example(standard_tenant)
    
    # Clean up (comment out if you want to keep the infrastructure)
    # cleanup_tenant_example(tenant_with_plugins)
    # cleanup_tenant_example(standard_tenant)
    
    print("\n" + "=" * 50)
    print("✅ Demo completed!")
    print("\nKey Features Demonstrated:")
    print("• Blueprint-driven infrastructure provisioning")
    print("• Custom plugin repository integration")
    print("• Tenant-specific service naming")
    print("• Comprehensive error handling and retries")
    print("• Service status monitoring")
    print("• Infrastructure cleanup")

if __name__ == "__main__":
    main()
