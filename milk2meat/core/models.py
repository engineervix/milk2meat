from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    """
    Tagged item model for UUID-based models, using the built-in
    GenericUUIDTaggedItemBase provided by django-taggit.
    """

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TypeMixin(models.Model):
    """
    Mixin that can be used to create taxonomies, e.g. different model types
    """

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
