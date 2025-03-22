from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from milk2meat.notes.models import Note


class HomeView(TemplateView):
    template_name = "home/home_page.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "home/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get recent notes (5) for the dashboard
        context["recent_notes"] = (
            Note.objects.get_queryset_for_user(self.request.user)
            .select_related("note_type")
            .order_by("-updated_at")[:5]
        )

        context["page_title"] = "Dashboard"
        return context
