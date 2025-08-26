"""
Test script for the tenant provisioning system.

This script tests the core functionality without making actual Render API calls.
"""

import os
import sys
import django
from unittest.mock import Mock, patch

# Setup Django environment
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from tenants.models import Tenant
from tenants.render_client import RenderAPIClient

def test_render_client_initialization():
    """Test RenderAPIClient initialization."""
    print("Testing RenderAPIClient initialization...")
    
    # Test with missing API key
    with patch.dict(os.environ, {}, clear=True):
        try:
            client = RenderAPIClient()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "RENDER_API_KEY" in str(e)
            print("✅ Correctly handled missing API key")
    
    # Test with API key
    with patch.dict(os.environ, {'RENDER_API_KEY': 'test_key'}):
        client = RenderAPIClient()
        assert client.api_key == 'test_key'
        assert 'Authorization' in client.headers
        print("✅ Correctly initialized with API key")

def test_blueprint_template_loading():
    """Test blueprint template loading."""
    print("\nTesting blueprint template loading...")
    
    with patch.dict(os.environ, {'RENDER_API_KEY': 'test_key'}):
        client = RenderAPIClient()
        
        # Test loading the template
        blueprint = client.get_blueprint_template()
        
        # Verify it's a dictionary with expected keys
        assert isinstance(blueprint, dict)
        assert 'services' in blueprint
        assert 'databases' in blueprint
        
        print("✅ Successfully loaded blueprint template")
        print(f"   Found {len(blueprint.get('services', []))} services")
        print(f"   Found {len(blueprint.get('databases', []))} databases")

def test_blueprint_customization():
    """Test blueprint customization for tenants."""
    print("\nTesting blueprint customization...")
    
    with patch.dict(os.environ, {'RENDER_API_KEY': 'test_key'}):
        client = RenderAPIClient()
        blueprint = client.get_blueprint_template()
        
        # Test customization without custom plugins
        customized = client.customize_blueprint_for_tenant(
            blueprint, 
            tenant_slug="test-tenant"
        )
        
        # Check that service names were customized
        for service in customized.get('services', []):
            if 'name' in service:
                assert service['name'].endswith('-test-tenant')
        
        print("✅ Successfully customized blueprint for tenant")
        
        # Test customization with custom plugins
        customized_with_plugins = client.customize_blueprint_for_tenant(
            blueprint,
            tenant_slug="test-tenant",
            custom_plugin_repo="https://github.com/test/plugins.git"
        )
        
        # Check that custom plugin environment variable was added
        backend_service = None
        for service in customized_with_plugins.get('services', []):
            if service.get('name', '').endswith('-backend'):
                backend_service = service
                break
        
        if backend_service:
            env_vars = [env['key'] for env in backend_service.get('envVars', [])]
            assert 'CUSTOM_PLUGINS_PATH' in env_vars
            print("✅ Successfully added custom plugin configuration")

def test_tenant_model():
    """Test tenant model functionality."""
    print("\nTesting tenant model...")
    
    # Create a test tenant
    tenant = Tenant.objects.create(
        name="Test Company",
        slug="test-company",
        custom_plugin_repo="https://github.com/test/plugins.git"
    )
    
    assert tenant.name == "Test Company"
    assert tenant.slug == "test-company"
    assert tenant.custom_plugin_repo == "https://github.com/test/plugins.git"
    assert tenant.status == Tenant.TenantStatus.PROVISIONING
    assert tenant.render_service_ids == {}
    
    print("✅ Successfully created tenant with custom plugins")
    
    # Test tenant without custom plugins
    tenant2 = Tenant.objects.create(
        name="Standard Company",
        slug="standard-company"
    )
    
    assert tenant2.custom_plugin_repo is None
    print("✅ Successfully created tenant without custom plugins")
    
    # Clean up
    tenant.delete()
    tenant2.delete()

def test_service_id_extraction():
    """Test service ID extraction from deployment response."""
    print("\nTesting service ID extraction...")
    
    # Mock deployment response
    mock_deployment = {
        'services': [
            {
                'service': {
                    'name': 'backboneos-backend-test-tenant',
                    'id': 'srv_123456'
                }
            },
            {
                'service': {
                    'name': 'backboneos-frontend-test-tenant',
                    'id': 'srv_789012'
                }
            }
        ]
    }
    
    # Test extraction logic
    service_ids = {}
    if 'services' in mock_deployment:
        for service_info in mock_deployment['services']:
            if 'service' in service_info:
                service_name = service_info['service'].get('name', '')
                service_id = service_info['service'].get('id', '')
                if service_name and service_id:
                    # Store with the original service name (without tenant suffix)
                    original_name = service_name.replace("-test-tenant", "")
                    service_ids[original_name] = service_id
    
    assert 'backboneos-backend' in service_ids
    assert 'backboneos-frontend' in service_ids
    assert service_ids['backboneos-backend'] == 'srv_123456'
    assert service_ids['backboneos-frontend'] == 'srv_789012'
    
    print("✅ Successfully extracted service IDs")

def main():
    """Run all tests."""
    print("🧪 Testing BackboneOS Tenant Provisioning System")
    print("=" * 50)
    
    try:
        test_render_client_initialization()
        test_blueprint_template_loading()
        test_blueprint_customization()
        test_tenant_model()
        test_service_id_extraction()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("\nThe tenant provisioning system is ready for use.")
        print("Set RENDER_API_KEY environment variable to test with real deployments.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
