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
    # Optional custom plugin repository URL for personalized code
    custom_plugin_repo = models.URLField(blank=True, null=True, help_text="Git repository URL for custom plugins")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
        ordering = ['-created_at']  # Most recent first
        indexes = [
            models.Index(fields=['status']),  # For filtering by status
            models.Index(fields=['created_at']),  # For date-based queries
            models.Index(fields=['name']),  # For name searches
            models.Index(fields=['status', 'created_at']),  # Composite index for status + date queries
        ]

    def __str__(self):
        return self.name