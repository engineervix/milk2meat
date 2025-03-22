from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BibleConfig(AppConfig):
    name = "milk2meat.bible"
    label = "bible"
    verbose_name = _("Bible")
