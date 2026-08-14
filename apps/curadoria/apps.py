from django.apps import AppConfig


class CuradoriaConfig(AppConfig):
    """Área restrita de curadoria dos dados públicos (RF15, RN14)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.curadoria"
    verbose_name = "curadoria"
