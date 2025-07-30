from django.apps import AppConfig


class SharedServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared_service'

    def ready(self):
        from . import signals