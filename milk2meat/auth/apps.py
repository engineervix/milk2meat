from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthConfig(AppConfig):
    name = "milk2meat.auth"
    label = "milk2meat_auth"
    verbose_name = _("Authentication")
