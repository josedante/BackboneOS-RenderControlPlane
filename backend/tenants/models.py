from django.db import models

class Tenant(models.Model):
    class TenantStatus(models.TextChoices):
        PROVISIONING = 'PROVISIONING', 'Provisioning'
        ACTIVE = 'ACTIVE', 'Active'
        SUSPENDED = 'SUSPENDED', 'Suspended'
        ERROR = 'ERROR', 'Error'

    name = models.CharField(max_length=255)
    # The unique name for the Render services, e.g., 'customer-a'
    slug = models.SlugField(unique=True) 
    status = models.CharField(
        max_length=20, 
        choices=TenantStatus.choices, 
        default=TenantStatus.PROVISIONING
    )
    # Stores the unique IDs of all Render services for this tenant
    render_service_ids = models.JSONField(default=dict, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name