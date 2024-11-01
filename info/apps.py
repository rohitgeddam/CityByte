from django.apps import AppConfig


class InfoConfig(AppConfig):
    """
    Configuration for the 'info' application.
    This class sets the default auto field type and the application name.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "info"
