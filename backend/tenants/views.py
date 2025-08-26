from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.text import slugify
from django.db import transaction
from .models import Tenant
from .serializers import TenantSerializer
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Tenant instances.
    
    The create method handles tenant creation with validation and background
    infrastructure provisioning.
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new tenant with validation and background infrastructure provisioning.
        
        Expected data:
        - name: Customer name (required)
        - slug: Optional custom slug, will be auto-generated if not provided
        
        Returns:
        - 201 Created with tenant data if successful
        - 400 Bad Request if validation fails
        """
        # Validate incoming data
        name = request.data.get('name')
        if not name:
            return Response(
                {'error': 'Customer name is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Clean and validate the name
        name = name.strip()
        if len(name) < 2:
            return Response(
                {'error': 'Customer name must be at least 2 characters long'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if tenant with this name already exists
        if Tenant.objects.filter(name__iexact=name).exists():
            return Response(
                {'error': 'A tenant with this name already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate or use provided slug
        slug = request.data.get('slug')
        if not slug:
            slug = slugify(name)
            # Ensure slug is unique
            counter = 1
            original_slug = slug
            while Tenant.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
        else:
            # Validate provided slug
            slug = slugify(slug)
            if Tenant.objects.filter(slug=slug).exists():
                return Response(
                    {'error': 'A tenant with this slug already exists'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            with transaction.atomic():
                # Create tenant with PROVISIONING status
                tenant_data = {
                    'name': name,
                    'slug': slug,
                    'status': Tenant.TenantStatus.PROVISIONING,
                    'render_service_ids': {}
                }
                
                serializer = self.get_serializer(data=tenant_data)
                serializer.is_valid(raise_exception=True)
                tenant = serializer.save()
                
                # Trigger background task for infrastructure creation
                self._trigger_infrastructure_provisioning(tenant)
                
                logger.info(f"Tenant '{tenant.name}' created with ID {tenant.id}, triggering infrastructure provisioning")
                
                return Response(
                    serializer.data, 
                    status=status.HTTP_201_CREATED
                )
                
        except Exception as e:
            logger.error(f"Error creating tenant '{name}': {str(e)}")
            return Response(
                {'error': 'Failed to create tenant. Please try again.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _trigger_infrastructure_provisioning(self, tenant):
        """
        Trigger background task for infrastructure provisioning on Render.
        
        This method integrates with Celery for asynchronous infrastructure creation.
        """
        try:
            from .tasks import provision_tenant_infrastructure
            # Trigger the background task
            provision_tenant_infrastructure.delay(tenant.id)
            logger.info(f"Infrastructure provisioning task queued for tenant: {tenant.name} (ID: {tenant.id})")
        except ImportError:
            # Fallback if Celery is not configured
            logger.warning("Celery not configured, skipping background task")
        except Exception as e:
            logger.error(f"Failed to queue infrastructure provisioning task for tenant {tenant.id}: {str(e)}")
            # Don't fail the tenant creation if task queuing fails
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """
        Get the current status of a tenant's infrastructure provisioning.
        """
        tenant = self.get_object()
        return Response({
            'id': tenant.id,
            'name': tenant.name,
            'slug': tenant.slug,
            'status': tenant.status,
            'render_service_ids': tenant.render_service_ids,
            'created_at': tenant.created_at
        })
