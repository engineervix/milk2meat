import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import DetailView, ListView, TemplateView
from taggit.models import Tag

from milk2meat.bible.models import Book
from milk2meat.core.utils.markdown import parse_markdown
from milk2meat.notes.forms import NoteForm, NoteTypeForm
from milk2meat.notes.models import Note, NoteType

logger = logging.getLogger(__name__)


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
    template_name = "notes/note_detail.html"
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


class NoteCreatePageView(LoginRequiredMixin, TemplateView):
    """View for rendering the note creation page"""

    template_name = "notes/note_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add an empty form for creating a new note
        context["form"] = NoteForm(user=self.request.user)

        # Add other context data
        context["note_types"] = NoteType.objects.all()
        context["bible_books"] = Book.objects.all()
        context["is_create"] = True
        return context


class NoteEditPageView(LoginRequiredMixin, TemplateView):
    """View for rendering the note edit page"""

    template_name = "notes/note_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the note instance
        note_id = self.kwargs.get("pk")
        note = get_object_or_404(Note, pk=note_id)

        # Verify the user has permission to edit this note
        if note.owner != self.request.user:
            raise PermissionDenied("You don't have permission to edit this note")

        # Add the note and form to the context
        context["note"] = note
        context["form"] = NoteForm(instance=note, user=self.request.user)

        # Add other context data
        context["note_types"] = NoteType.objects.all()
        context["bible_books"] = Book.objects.all()
        context["is_create"] = False
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
def note_save_ajax(request, pk=None):
    """
    AJAX view for creating or updating notes without page reload.

    This view handles both creation of new notes and updating existing ones through AJAX,
    allowing for a smoother user experience where notes can be saved without navigating
    away from the editing page.

    Parameters:
        request: The HTTP request object
        pk (UUID, optional): The primary key of the note to update. If None, creates a new note.

    Request Data:
        - All standard NoteForm fields (title, note_type, content, etc.)
        - tags_input: Comma-separated list of tags
        - referenced_books_json: JSON string of book IDs to reference
        - upload: Optional file attachment

    Returns:
        JsonResponse with the following structure:
        - On success:
            {
                "success": true,
                "is_new": true/false,
                "note": {
                    "id": "<note-uuid>",
                    "title": "<note-title>",
                    "detail_url": "<url>",
                    "edit_url": "<url>"
                },
                "message": "Note saved successfully."
            }
        - On validation error:
            {"success": false, "errors": {field_errors}}
        - On permission error:
            {"success": false, "error": "error message"}

    Status Codes:
        - 200: Success
        - 400: Validation error
        - 403: Permission denied
        - 404: Note not found
        - 500: Server error
    """
    try:
        # Initialize the form with data, files, and owner
        if pk:
            # Update existing note - get the note and verify ownership
            try:
                note = get_object_or_404(Note, pk=pk)
                # Check if the user is the owner
                if note.owner != request.user:
                    return JsonResponse(
                        {"success": False, "error": "You don't have permission to edit this note"}, status=403
                    )
                form = NoteForm(request.POST, request.FILES, instance=note, user=request.user)
                is_new = False
            except Http404:
                return JsonResponse({"success": False, "error": "Note not found"}, status=404)
        else:
            # Create new note
            form = NoteForm(request.POST, request.FILES, user=request.user)
            is_new = True

        if form.is_valid():
            # For new notes, set the owner before saving
            note = form.save(commit=False)
            if is_new:
                note.owner = request.user
            note.save()

            # We need to manually handle tags and referenced books instead of using form.save_m2m()
            # because we're saving with commit=False

            # Handle referenced books
            book_ids = form.cleaned_data.get("referenced_books_json", [])
            note.referenced_books.clear()
            if book_ids:
                note.referenced_books.add(*book_ids)

            # Handle tags
            tags = form.cleaned_data.get("tags_input", [])
            note.tags.clear()
            if tags:
                note.tags.add(*tags)

            # Build response data
            data = {
                "success": True,
                "is_new": is_new,
                "note": {
                    "id": str(note.pk),
                    "title": note.title,
                    "detail_url": reverse("notes:note_detail", kwargs={"pk": note.pk}),
                    "edit_url": reverse("notes:note_edit", kwargs={"pk": note.pk}),
                },
                "message": "Note saved successfully.",
            }

            return JsonResponse(data)
        else:
            # Return form errors
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    except PermissionDenied as e:
        return JsonResponse({"success": False, "error": str(e)}, status=403)
    except Exception as e:
        logger.exception("Error saving note via AJAX")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_POST
@login_required
def note_delete_view(request, pk):
    """View for deleting a note"""
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    title = note.title  # Save the title for the success message
    note.delete()
    messages.success(request, f"Note '{title}' has been deleted.")
    return redirect(reverse_lazy("notes:note_list"))


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
