# Generated by Django 5.1.6 on 2025-03-11 22:21

import django.core.validators
import django.db.models.deletion
import milk2meat.core.models
import milk2meat.core.utils.validators
import taggit.managers
import upload_validator
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("taggit", "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=55, unique=True)),
                ("abbreviation", models.CharField(max_length=10, unique=True)),
                (
                    "testament",
                    models.CharField(choices=[("OT", "Old Testament"), ("NT", "New Testament")], max_length=2),
                ),
                (
                    "number",
                    models.PositiveSmallIntegerField(
                        help_text="Position in the ordering of the Bible (1-66)",
                        unique=True,
                        validators=[
                            django.core.validators.MinValueValidator(1, message="Value must be at least 1"),
                            django.core.validators.MaxValueValidator(66, message="Value cannot be greater than 66"),
                        ],
                    ),
                ),
                (
                    "chapters",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MaxValueValidator(
                                150, message="There's no Book of the Bible with more than 150 chapters"
                            )
                        ]
                    ),
                ),
                ("title_and_author", models.TextField(blank=True)),
                ("date_and_occasion", models.TextField(blank=True)),
                ("characteristics_and_themes", models.TextField(blank=True)),
                ("christ_in_book", models.TextField(blank=True)),
                ("timeline", models.JSONField(blank=True, default=dict)),
                ("outline", models.TextField(blank=True)),
            ],
            options={
                "ordering": ["number"],
            },
        ),
        migrations.CreateModel(
            name="NoteType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="UUIDTaggedItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("object_id", models.UUIDField(db_index=True, verbose_name="object ID")),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(app_label)s_%(class)s_tagged_items",
                        to="contenttypes.contenttype",
                        verbose_name="content type",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(app_label)s_%(class)s_items",
                        to="taggit.tag",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tag",
                "verbose_name_plural": "Tags",
            },
        ),
        migrations.CreateModel(
            name="Note",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(max_length=255)),
                ("content", models.TextField(blank=True)),
                (
                    "upload",
                    models.FileField(
                        blank=True,
                        help_text="You could upload handwritten notes from iPad as PDF or image",
                        null=True,
                        upload_to=milk2meat.core.models.user_note_upload_path,
                        validators=[
                            upload_validator.FileTypeValidator(
                                allowed_types=[
                                    "image/jpeg",
                                    "image/png",
                                    "image/webp",
                                    "image/bmp",
                                    "image/svg+xml",
                                    "application/pdf",
                                    "application/msword",
                                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    "application/rtf",
                                    "application/vnd.oasis.opendocument.text",
                                    "application/vnd.ms-excel",
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    "application/vnd.oasis.opendocument.spreadsheet",
                                    "text/csv",
                                    "application/vnd.ms-powerpoint",
                                    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                    "application/vnd.oasis.opendocument.presentation",
                                ]
                            ),
                            milk2meat.core.utils.validators.FileSizeValidator(),
                        ],
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="notes", to=settings.AUTH_USER_MODEL
                    ),
                ),
                ("referenced_books", models.ManyToManyField(blank=True, related_name="notes", to="core.book")),
                (
                    "note_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="notes", to="core.notetype"
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        through="core.UUIDTaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at", "-created_at"],
                "constraints": [models.UniqueConstraint(fields=("slug", "owner"), name="unique_owner_slug")],
            },
        ),
    ]
