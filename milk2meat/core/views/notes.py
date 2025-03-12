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

from ..forms import NoteForm, NoteTypeForm
from ..models import Book, Note, NoteType
from ..utils.markdown import parse_markdown

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
            logger.exception("Error updating note")
            messages.error(self.request, f"Error updating note: {str(e)}")
            return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("core:note_detail", kwargs={"pk": self.object.pk})


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
