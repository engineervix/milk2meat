import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager


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
        upload_to="notes/",
        blank=True,
        null=True,
        help_text="You could upload handwritten notes from iPad as PDF or image",
    )
    note_type = models.ForeignKey(NoteType, on_delete=models.PROTECT, related_name="notes")
    tags = TaggableManager(blank=True)
    referenced_books = models.ManyToManyField(Book, blank=True, related_name="notes")
    owner = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="notes")

    objects = NoteManager()

    class Meta:
        ordering = ["-updated_at", "-created_at"]
        unique_together = ["slug", "owner"]

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

        # Check uniqueness only within this user's notes
        while self.__class__.objects.filter(slug=unique_slug, owner=self.owner).exists():
            unique_slug = f"{slug}-{num}"
            num += 1

        return unique_slug
