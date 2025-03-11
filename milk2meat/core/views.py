import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from taggit.models import Tag
from watson import search as watson

from .forms import BookEditForm, NoteForm, NoteTypeForm
from .models import Book, Note, NoteType, Testament
from .utils.markdown import parse_markdown

logger = logging.getLogger(__name__)


class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = "core/book_list.html"
    context_object_name = "books"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Organize books by testament
        context["old_testament"] = Book.objects.filter(testament=Testament.OT).order_by("number")
        context["new_testament"] = Book.objects.filter(testament=Testament.NT).order_by("number")
        return context


class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = "core/book_detail.html"
    context_object_name = "book"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Parse and render markdown fields
        book = self.object
        if book.title_and_author:
            context["title_and_author_html"] = mark_safe(parse_markdown(book.title_and_author))
        if book.date_and_occasion:
            context["date_and_occasion_html"] = mark_safe(parse_markdown(book.date_and_occasion))
        if book.characteristics_and_themes:
            context["characteristics_and_themes_html"] = mark_safe(parse_markdown(book.characteristics_and_themes))
        if book.christ_in_book:
            context["christ_in_book_html"] = mark_safe(parse_markdown(book.christ_in_book))
        if book.outline:
            context["outline_html"] = mark_safe(parse_markdown(book.outline))

        # Add timeline data if it exists
        if self.object.timeline:
            context["timeline_data"] = self.object.timeline.get("events", [])

        return context


class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookEditForm
    template_name = "core/book_edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add timeline data as JSON string for the form
        if self.object.timeline:
            context["timeline_json"] = json.dumps(self.object.timeline)
        else:
            context["timeline_json"] = json.dumps({"events": []})

        return context

    def form_valid(self, form):
        """Process the form data and save"""
        try:
            response = super().form_valid(form)
            messages.success(self.request, f"Successfully updated {self.object.title}.")
            return response
        except Exception as e:
            messages.error(self.request, f"Error saving book: {str(e)}")
            return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("core:book_detail", kwargs={"pk": self.object.pk})


class NoteListView(LoginRequiredMixin, ListView):
    """View for listing user's notes with filtering options"""

    model = Note
    template_name = "core/note_list.html"
    context_object_name = "notes"
    paginate_by = 12  # Show 12 notes per page

    def get_queryset(self):
        """Filter notes by the current user with enhanced search"""
        queryset = (
            Note.objects.get_queryset_for_user(self.request.user)
            .select_related("note_type", "owner")
            .prefetch_related("referenced_books", "tags")
        )

        # Apply filters if provided
        note_type = self.request.GET.get("type")
        book_id = self.request.GET.get("book")
        tag = self.request.GET.get("tag")
        search_query = self.request.GET.get("q")

        if note_type:
            queryset = queryset.filter(note_type__name__iexact=note_type)

        if book_id:
            queryset = queryset.filter(referenced_books__id=book_id)

        if tag:
            queryset = queryset.filter(tags__name__iexact=tag)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(content__icontains=search_query)
                | Q(tags__name__icontains=search_query)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add note types for filter dropdown
        context["note_types"] = NoteType.objects.all()

        # Add Bible books for filter dropdown
        context["bible_books"] = Book.objects.all()

        # Add search query to context for UI feedback
        search_query = self.request.GET.get("q", "")
        context["search_query"] = search_query

        # Add filter parameters to maintain state
        context["current_filters"] = {
            "type": self.request.GET.get("type", ""),
            "book": self.request.GET.get("book", ""),
            "tag": self.request.GET.get("tag", ""),
            "q": search_query,
        }

        # Get all note IDs for the current user
        user_note_ids = Note.objects.get_queryset_for_user(self.request.user).values_list("id", flat=True)

        # Get tags with note counts
        context["tags"] = (
            Tag.objects.filter(
                core_uuidtaggeditem_items__content_type__app_label="core",
                core_uuidtaggeditem_items__content_type__model="note",
                core_uuidtaggeditem_items__object_id__in=user_note_ids,
            )
            .annotate(count=Count("core_uuidtaggeditem_items"))
            .order_by("name")
        )

        # Add count of search results if search is active
        if search_query:
            context["is_search_active"] = True
            context["result_count"] = context["paginator"].count

        return context


class NoteDetailView(LoginRequiredMixin, DetailView):
    """View for displaying a single note"""

    model = Note
    template_name = "core/note_detail.html"
    context_object_name = "note"

    def get_queryset(self):
        """Ensure user can only view their own notes"""
        return Note.objects.get_queryset_for_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Convert markdown content to HTML
        if self.object.content:
            context["content_html"] = mark_safe(parse_markdown(self.object.content))

        # Add secure URL for file if present
        if self.object.upload:
            context["secure_file_url"] = self.object.get_secure_file_url(self.request.user)

        return context


class NoteCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new note"""

    model = Note
    form_class = NoteForm
    template_name = "core/note_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["note_types"] = NoteType.objects.all()
        context["bible_books"] = Book.objects.all()
        context["is_create"] = True
        return context

    def form_valid(self, form):
        """Process the form data and save"""
        try:
            # Explicitly set the owner before saving
            form.instance.owner = self.request.user

            # Call the parent class's form_valid which calls form.save()
            response = super().form_valid(form)
            messages.success(self.request, "Note created successfully.")
            return response
        except Exception as e:
            messages.error(self.request, f"Error creating note: {str(e)}")
            return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("core:note_detail", kwargs={"pk": self.object.pk})


class NoteUpdateView(LoginRequiredMixin, UpdateView):
    """View for editing an existing note"""

    model = Note
    form_class = NoteForm
    template_name = "core/note_form.html"

    def get_queryset(self):
        """Ensure user can only edit their own notes"""
        return Note.objects.get_queryset_for_user(self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["note_types"] = NoteType.objects.all()
        context["bible_books"] = Book.objects.all()
        context["is_create"] = False
        return context

    def form_valid(self, form):
        """Process the form data and save"""
        try:
            response = super().form_valid(form)
            messages.success(self.request, f"Note '{self.object.title}' updated successfully.")
            return response
        except Exception as e:
            messages.error(self.request, f"Error updating note: {str(e)}")
            return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("core:note_detail", kwargs={"pk": self.object.pk})


class TagListView(LoginRequiredMixin, ListView):
    """View for browsing tags"""

    template_name = "core/tag_list.html"
    context_object_name = "tags"

    def get_queryset(self):
        """Get all tags used by the current user's notes with counts"""
        from django.db.models import Count
        from taggit.models import Tag

        # Get all note IDs for the current user
        user_note_ids = Note.objects.get_queryset_for_user(self.request.user).values_list("id", flat=True)

        # Get tags with note counts using UUIDTaggedItem
        return (
            Tag.objects.filter(
                core_uuidtaggeditem_items__content_type__app_label="core",
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


class GlobalSearchView(LoginRequiredMixin, ListView):
    template_name = "core/search_results.html"
    context_object_name = "search_results"
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get("q", "")

        if not query:
            return []

        # Perform search with watson
        search_results = watson.search(
            query,
            # Limit search to user's own notes
            models=(
                Note.objects.get_queryset_for_user(self.request.user),
                Book.objects.all(),
            ),
        )

        return search_results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add search query to context
        query = self.request.GET.get("q", "")
        context["search_query"] = query

        if query:
            # For accurate result counting, we need to get the total count
            # from the paginator rather than the page object
            context["total_count"] = context["paginator"].count

            # Add pagination info
            page_obj = context["page_obj"]
            if page_obj.has_next() or page_obj.has_previous():
                start_index = page_obj.start_index()
                end_index = page_obj.end_index()
                context["showing_range"] = {
                    "start": start_index,
                    "end": end_index,
                }

            # Group results by model type (only for current page)
            if context["search_results"]:
                from itertools import groupby

                # Group results by model type
                results_by_type = {}
                for model_name, group in groupby(
                    context["search_results"], key=lambda x: x.content_type.model_class().__name__
                ):
                    results_by_type[model_name] = list(group)

                context["results_by_type"] = results_by_type

        return context


@require_POST
def create_note_type_ajax(request):
    """AJAX view for dynamically creating a new note type"""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Authentication required"}, status=403)

    form = NoteTypeForm(request.POST)

    if form.is_valid():
        note_type = form.save()
        return JsonResponse(
            {
                "success": True,
                "id": note_type.id,
                "name": note_type.name,
            }
        )
    else:
        # Return form errors
        return JsonResponse({"success": False, "errors": form.errors}, status=400)


@require_POST
@login_required
def note_delete_view(request, pk):
    """View for deleting a note"""
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    title = note.title  # Save the title for the success message
    note.delete()
    messages.success(request, f"Note '{title}' has been deleted.")
    return redirect(reverse_lazy("core:note_list"))


@login_required
@require_GET
def serve_protected_file(request, note_id):
    """
    Serve a protected file through a URL.

    This view checks permissions and returns an appropriate URL:
    - In development: returns the normal file URL
    - In production: returns a signed URL with expiration
    """
    try:
        # Get the note and verify ownership
        note = get_object_or_404(Note, pk=note_id, owner=request.user)

        if not note.upload:
            raise Http404("This note has no attached file")

        # Get the file URL - will be handled differently based on environment
        file_url = note.get_secure_file_url(request.user)

        if not file_url:
            raise PermissionDenied("You don't have permission to access this file")

        # Return JSON response with the URL
        return JsonResponse({"url": file_url})

    except (Note.DoesNotExist, PermissionDenied) as e:
        return JsonResponse({"error": str(e)}, status=403)
    except Http404 as e:
        return JsonResponse({"error": str(e)}, status=404)
    except Exception:
        logger.exception("Error serving protected file")
        return JsonResponse({"error": "Server error"}, status=500)
