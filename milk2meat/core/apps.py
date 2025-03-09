from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    name = "milk2meat.core"
    label = "core"
    verbose_name = _("Core")

    def ready(self):
        # Register models with django-watson
        from .search import register_watson_models

        register_watson_models()
