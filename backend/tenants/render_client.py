import os
import yaml
import requests
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class RenderAPIClient:
    """
    Client for interacting with the Render API.
    
    Handles authentication, blueprint deployment, and service management.
    """
    
    def __init__(self):
        self.api_key = os.getenv('RENDER_API_KEY')
        if not self.api_key:
            raise ValueError("RENDER_API_KEY environment variable is required")
        
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
    
    def deploy_blueprint(self, blueprint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy a blueprint to Render.
        
        Args:
            blueprint_data: The blueprint configuration as a dictionary
            
        Returns:
            Dict containing the deployment response with service information
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = urljoin(self.base_url, "blueprints")
        
        logger.info("Deploying blueprint to Render")
        response = requests.post(url, headers=self.headers, json=blueprint_data)
        response.raise_for_status()
        
        deployment_data = response.json()
        logger.info(f"Successfully deployed blueprint. Deployment ID: {deployment_data.get('id')}")
        
        return deployment_data
    
    def delete_service(self, service_id: str) -> bool:
        """
        Delete a service from Render.
        
        Args:
            service_id: The ID of the service to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = urljoin(self.base_url, f"services/{service_id}")
        
        logger.info(f"Deleting service {service_id} from Render")
        response = requests.delete(url, headers=self.headers)
        
        if response.status_code == 404:
            logger.warning(f"Service {service_id} not found (may already be deleted)")
            return True
        
        response.raise_for_status()
        logger.info(f"Successfully deleted service {service_id}")
        
        return True
    
    def get_service_status(self, service_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a service.
        
        Args:
            service_id: The ID of the service
            
        Returns:
            Service status information or None if not found
        """
        url = urljoin(self.base_url, f"services/{service_id}")
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get service status for {service_id}: {e}")
            return None
    
    def get_blueprint_template(self) -> Dict[str, Any]:
        """
        Load the base blueprint template from the render.yaml file.
        
        Returns:
            The blueprint configuration as a dictionary
        """
        blueprint_path = os.path.join(
            os.path.dirname(__file__), 
            'base_crm_render.yaml'
        )
        
        try:
            with open(blueprint_path, 'r') as f:
                blueprint = yaml.safe_load(f)
            logger.info("Successfully loaded blueprint template")
            return blueprint
        except FileNotFoundError:
            raise FileNotFoundError(f"Blueprint template not found at {blueprint_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in blueprint template: {e}")
    
    def customize_blueprint_for_tenant(
        self, 
        blueprint: Dict[str, Any], 
        tenant_slug: str,
        custom_plugin_repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Customize the blueprint for a specific tenant.
        
        Args:
            blueprint: The base blueprint configuration
            tenant_slug: The tenant's unique slug
            custom_plugin_repo: Optional custom plugin repository URL
            
        Returns:
            The customized blueprint configuration
        """
        # Create a deep copy to avoid modifying the original
        customized_blueprint = yaml.safe_load(yaml.dump(blueprint))
        
        # Customize service names to avoid conflicts
        for service in customized_blueprint.get('services', []):
            if 'name' in service:
                service['name'] = f"{service['name']}-{tenant_slug}"
        
        # Customize database names
        for database in customized_blueprint.get('databases', []):
            if 'name' in database:
                database['name'] = f"{database['name']}-{tenant_slug}"
        
        # Customize environment variables to include tenant-specific values
        for service in customized_blueprint.get('services', []):
            if service.get('type') == 'web' and 'envVars' in service:
                # Add tenant-specific environment variables
                service['envVars'].extend([
                    {'key': 'TENANT_SLUG', 'value': tenant_slug},
                    {'key': 'TENANT_NAME', 'value': f"tenant-{tenant_slug}"}
                ])
                
                # If custom plugin repo is provided, modify the build command
                if custom_plugin_repo and service.get('name', '').endswith('-backend'):
                    current_build_command = service.get('buildCommand', '')
                    if current_build_command:
                        # Add git clone command for custom plugins
                        plugin_setup = f"git clone {custom_plugin_repo} /app/custom-plugins && "
                        service['buildCommand'] = plugin_setup + current_build_command
                        
                        # Add environment variable for custom plugins path
                        service['envVars'].append({
                            'key': 'CUSTOM_PLUGINS_PATH', 
                            'value': '/app/custom-plugins'
                        })
        
        logger.info(f"Customized blueprint for tenant {tenant_slug}")
        return customized_blueprint
