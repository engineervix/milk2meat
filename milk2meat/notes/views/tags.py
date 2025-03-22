import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.views.generic import ListView
from taggit.models import Tag

from milk2meat.notes.models import Note

logger = logging.getLogger(__name__)


class TagListView(LoginRequiredMixin, ListView):
    """View for browsing tags"""

    template_name = "notes/tag_list.html"
    context_object_name = "tags"

    def get_queryset(self):
        """Get all tags used by the current user's notes with counts"""

        # Get all note IDs for the current user
        user_note_ids = Note.objects.get_queryset_for_user(self.request.user).values_list("id", flat=True)

        # Get tags with note counts using UUIDTaggedItem
        return (
            Tag.objects.filter(
                core_uuidtaggeditem_items__content_type__app_label="notes",
                core_uuidtaggeditem_items__content_type__model="note",
                core_uuidtaggeditem_items__object_id__in=user_note_ids,
            )
            .annotate(note_count=Count("core_uuidtaggeditem_items"))
            .order_by("name")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Organize tags by first letter for the alphabetical section
        tags_by_letter = {}
        for tag in context["tags"]:
            if tag.name:
                first_letter = tag.name[0].upper()
                if first_letter not in tags_by_letter:
                    tags_by_letter[first_letter] = []
                tags_by_letter[first_letter].append(tag)

        context["tags_by_letter"] = tags_by_letter

        # Get tags with count for the tag cloud (sorted by count)
        context["tags_for_cloud"] = context["tags"].order_by("-note_count")

        return context
