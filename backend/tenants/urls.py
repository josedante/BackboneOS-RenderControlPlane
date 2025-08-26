from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TenantViewSet, health_check

router = DefaultRouter()
router.register(r'tenants', TenantViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/health/', health_check, name='health_check'),
]
