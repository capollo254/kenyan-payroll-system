# apps/compliance/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .compliance_views import StatutoryRateViewSet

router = DefaultRouter()
router.register(r'statutory-rates', StatutoryRateViewSet, basename='statutory-rate')

urlpatterns = [
    path('', include(router.urls)),
]