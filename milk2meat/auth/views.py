import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from .forms import TurnstileLoginForm
from .turnstile import TurnstileValidationError, validate_turnstile

logger = logging.getLogger(__name__)


class TurnstileLoginView(LoginView):
    """Custom login view with Turnstile validation"""

    template_name = "auth/login.html"
    form_class = TurnstileLoginForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["turnstile_site_key"] = settings.TURNSTILE_SITE_KEY
        context["turnstile_enabled"] = not settings.TURNSTILE_SKIP_VALIDATION and settings.TURNSTILE_SITE_KEY
        return context

    def form_valid(self, form):
        """Override form_valid to add Turnstile validation"""
        # Skip validation in development or when configured to skip
        if not settings.TURNSTILE_SKIP_VALIDATION and settings.TURNSTILE_SITE_KEY:
            try:
                is_valid = validate_turnstile(self.request)
                if not is_valid:
                    messages.error(self.request, "Security verification failed. Please try again.")
                    return self.form_invalid(form)
            except TurnstileValidationError as e:
                logger.error(f"Turnstile validation error: {str(e)}", exc_info=True)
                messages.error(self.request, "Security verification service unavailable. Please try again later.")
                return self.form_invalid(form)

        # If Turnstile validation passes or is skipped, proceed with login
        return super().form_valid(form)


@require_http_methods(["POST"])
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect(reverse_lazy("auth:login"))
