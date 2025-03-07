import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import DetailView, ListView, UpdateView

from .forms import BookEditForm
from .models import Book, Testament
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
