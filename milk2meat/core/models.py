import os
import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase
from upload_validator import FileTypeValidator

from .storage import PrivateMediaStorage
from .utils.constants import ALLOWED_DOCUMENT_TYPES, ALLOWED_IMAGE_TYPES
from .utils.validators import FileSizeValidator


def user_note_upload_path(instance, filename):
    """
    Generate file path for user uploads.
    Structure: notes/{user_id}/{note_id}/{filename}
    This structure makes it easier to implement access control.
    """
    # Get file extension and sanitize filename
    _, extension = os.path.splitext(filename)
    sanitized_filename = slugify(os.path.splitext(filename)[0])[:40] + extension

    # Create path with user_id/note_id structure
    return f"notes/{instance.owner.id}/{instance.id}/{sanitized_filename}"


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


class Testament(models.TextChoices):
    OT = "OT", "Old Testament"
    NT = "NT", "New Testament"


class Book(BaseModel):
    """
    Represents a book of the Bible
    """

    # ----------------------------------------------------------------------
    # Core
    # ----------------------------------------------------------------------
    title = models.CharField(max_length=55, unique=True)
    abbreviation = models.CharField(max_length=10, unique=True)
    testament = models.CharField(max_length=2, choices=Testament.choices)
    number = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message="Value must be at least 1"),
            MaxValueValidator(66, message="Value cannot be greater than 66"),
        ],
        unique=True,
        help_text="Position in the ordering of the Bible (1-66)",
    )
    chapters = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(150, message="There's no Book of the Bible with more than 150 chapters"),
        ]
    )

    # ----------------------------------------------------------------------
    # Book intro from The Reformation Study Bible - Condensed Edition
    # ----------------------------------------------------------------------
    title_and_author = models.TextField(blank=True)
    date_and_occasion = models.TextField(blank=True)
    characteristics_and_themes = models.TextField(blank=True)
    christ_in_book = models.TextField(blank=True)

    # ----------------------------------------------------------------------
    # Book intro (selected) from The ESV Global Study Bible
    # ----------------------------------------------------------------------
    timeline = models.JSONField(default=dict, blank=True)
    outline = models.TextField(blank=True)

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return self.title


class NoteType(TypeMixin):
    """
    This allows for categorizing notes
    """

    pass


class NoteManager(models.Manager):
    """
    Custom manager for Notes to help with user-specific queries
    """

    def get_queryset_for_user(self, user):
        """
        Returns only notes owned by the specified user
        """
        return super().get_queryset().filter(owner=user)


class Note(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255)
    content = models.TextField(blank=True)
    upload = models.FileField(
        upload_to=user_note_upload_path,
        storage=PrivateMediaStorage(),
        blank=True,
        null=True,
        help_text="You could upload handwritten notes from iPad as PDF or image",
        validators=[
            FileTypeValidator(
                allowed_types=ALLOWED_IMAGE_TYPES + ALLOWED_DOCUMENT_TYPES,
            ),
            FileSizeValidator(),
        ],
    )
    note_type = models.ForeignKey(NoteType, on_delete=models.PROTECT, related_name="notes")
    tags = TaggableManager(through=UUIDTaggedItem, blank=True)
    referenced_books = models.ManyToManyField(Book, blank=True, related_name="notes")
    owner = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="notes")

    objects = NoteManager()

    class Meta:
        ordering = ["-updated_at", "-created_at"]
        constraints = [models.UniqueConstraint(fields=["slug", "owner"], name="unique_owner_slug")]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug or (self.pk and self.title != self.__class__.objects.get(pk=self.pk).title):
            self.slug = self._generate_unique_slug()
        self.full_clean()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        """Generate a unique slug by appending a number if needed."""
        slug = slugify(self.title)
        unique_slug = slug
        num = 1

        # Skip owner uniqueness check if owner is not set
        if not hasattr(self, "owner") or self.owner is None:
            return unique_slug

        # Check uniqueness only within this user's notes
        while self.__class__.objects.filter(slug=unique_slug, owner=self.owner).exists():
            unique_slug = f"{slug}-{num}"
            num += 1

        return unique_slug

    def get_secure_file_url(self, user, expire=300):
        """
        Get a secure URL for the uploaded file, but only if the user has permission.

        Args:
            user: The user requesting access
            expire: Expiration time in seconds

        Returns:
            A signed URL or None if no file or permission denied
        """
        if not self.upload:
            return None

        # Only allow access if user is the owner of the note
        if user != self.owner:
            return None

        # Generate a signed URL with expiration
        storage = PrivateMediaStorage()
        return storage.url(self.upload.name, expire=expire)
