# apps/reports/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet, P9ViewSet

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'p9', P9ViewSet, basename='p9')

urlpatterns = [
    path('', include(router.urls)),
]