from django.apps import AppConfig


class WorkOrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.work_orders'
    verbose_name = 'Work Orders'

    def ready(self):
        """Import signals when app is ready."""
        import apps.work_orders.signals  # noqa
