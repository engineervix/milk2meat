import os
import uuid

from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager
from upload_validator import FileTypeValidator

from milk2meat.bible.models import Book
from milk2meat.core.models import BaseModel, TypeMixin, UUIDTaggedItem
from milk2meat.core.utils.constants import ALLOWED_DOCUMENT_TYPES, ALLOWED_IMAGE_TYPES
from milk2meat.core.utils.validators import FileSizeValidator


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


class NoteType(TypeMixin):
    """
    This allows for categorizing notes
    """

    class Meta(TypeMixin.Meta):
        db_table = "core_notetype"  # Explicitly use the existing table name


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
    referenced_books = models.ManyToManyField(
        Book, blank=True, related_name="notes", db_table="core_note_referenced_books"
    )
    owner = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="notes")

    objects = NoteManager()

    class Meta:
        ordering = ["-updated_at", "-created_at"]
        constraints = [models.UniqueConstraint(fields=["slug", "owner"], name="unique_owner_slug")]
        db_table = "core_note"  # Explicitly use the existing table name

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

    def get_secure_file_url(self, user):
        """
        Get a secure URL for the uploaded file, but only if the user has permission.

        Args:
            user: The user requesting access

        Returns:
            A URL or None if no file or permission denied
        """
        if not self.upload:
            return None

        # Only allow access if user is the owner of the note
        if user != self.owner:
            return None

        # Get the URL - Django will use the appropriate storage backend
        # In dev mode, this will return a regular file URL
        # In production, this will use S3Boto3Storage which returns a signed URL
        return self.upload.url
