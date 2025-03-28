import json
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView

from milk2meat.bible.forms import BookEditForm
from milk2meat.bible.models import Book, Testament
from milk2meat.core.utils.markdown import parse_markdown

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
    template_name = "bible/book_detail.html"
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


class BookEditPageView(LoginRequiredMixin, TemplateView):
    """View for rendering the book edit page"""

    template_name = "bible/book_edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the book instance
        book_id = self.kwargs.get("pk")
        book = get_object_or_404(Book, pk=book_id)

        # Add the book and form to the context
        context["book"] = book
        context["form"] = BookEditForm(instance=book)

        # Add timeline data as JSON string for the form
        if book.timeline:
            context["timeline_json"] = json.dumps(book.timeline)
        else:
            context["timeline_json"] = json.dumps({"events": []})

        # Add the update URL for AJAX form submission
        context["book_update_url"] = reverse("bible:book_update_ajax", kwargs={"pk": book.pk})
        context["current_book_id"] = book.pk

        return context


@require_POST
@login_required
def book_save_ajax(request, pk):
    """
    AJAX view for updating books without page reload.

    This view handles updating existing books through AJAX,
    allowing for a smoother user experience where books can be saved without navigating
    away from the editing page.

    Parameters:
        request: The HTTP request object
        pk (int): The primary key of the book to update

    Request Data:
        - All standard BookEditForm fields (title_and_author, date_and_occasion, etc.)
        - timeline: JSON string of timeline events

    Returns:
        JsonResponse with the following structure:
        - On success:
            {
                "success": true,
                "book": {
                    "id": <book-id>,
                    "title": "<book-title>",
                    "detail_url": "<url>"
                },
                "message": "Book saved successfully."
            }
        - On validation error:
            {"success": false, "errors": {field_errors}}
        - On permission error:
            {"success": false, "error": "error message"}

    Status Codes:
        - 200: Success
        - 400: Validation error
        - 404: Book not found
        - 500: Server error
    """
    try:
        # Get the book to update
        try:
            book = get_object_or_404(Book, pk=pk)
        except Exception:
            return JsonResponse({"success": False, "error": "Book not found"}, status=404)

        # Initialize the form with request data and the book instance
        form = BookEditForm(request.POST, instance=book)

        if form.is_valid():
            # Save the book
            book = form.save()

            # Build response data
            data = {
                "success": True,
                "book": {
                    "id": book.pk,
                    "title": book.title,
                    "detail_url": reverse("bible:book_detail", kwargs={"pk": book.pk}),
                },
                "message": f"{book.title} saved successfully.",
            }

            return JsonResponse(data)
        else:
            # Return form errors
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    except Exception as e:
        logger.exception("Error saving book via AJAX")
        return JsonResponse({"success": False, "error": str(e)}, status=500)
