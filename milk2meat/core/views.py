import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from watson import search as watson

from milk2meat.bible.models import Book
from milk2meat.notes.models import Note

logger = logging.getLogger(__name__)


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
