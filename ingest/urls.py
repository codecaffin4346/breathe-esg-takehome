from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NormalizedEmissionViewSet, AuditLogViewSet

router = DefaultRouter()
router.register(r'emissions', NormalizedEmissionViewSet)
router.register(r'audits', AuditLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
