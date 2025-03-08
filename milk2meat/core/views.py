import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import BookEditForm, NoteForm, NoteTypeForm
from .models import Book, Note, NoteType, Testament
from .utils.markdown import parse_markdown


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
        """Filter notes by the current user"""
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
            queryset = queryset.filter(title__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add note types for filter dropdown
        context["note_types"] = NoteType.objects.all()

        # Add Bible books for filter dropdown
        context["bible_books"] = Book.objects.all()

        # Add filter parameters to maintain state
        context["current_filters"] = {
            "type": self.request.GET.get("type", ""),
            "book": self.request.GET.get("book", ""),
            "tag": self.request.GET.get("tag", ""),
            "q": self.request.GET.get("q", ""),
        }

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
