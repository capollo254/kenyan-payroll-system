from django.apps import AppConfig


class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reports'
    verbose_name = 'Reports'
    
    def ready(self):
        """Import admin when app is ready"""
        try:
            import apps.reports.admin  # Import admin to register models
        except ImportError:
            pass