from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from milk2meat.core.models import BaseModel


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
        db_table = "core_book"  # Explicitly use the existing table name

    def __str__(self):
        return self.title
