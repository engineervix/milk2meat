from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HomeConfig(AppConfig):
    name = "milk2meat.home"
    label = "home"
    verbose_name = _("Home")
