from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotesConfig(AppConfig):
    name = "milk2meat.notes"
    label = "notes"
    verbose_name = _("Notes")
