from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


class TurnstileLoginForm(AuthenticationForm):
    """
    Custom authentication form with Turnstile integration
    """

    # We don't need an actual field for the Turnstile widget
    # It will be rendered in the template and validated separately

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add DaisyUI-compatible attributes to form fields for better styling
        self.fields["username"].widget.attrs.update(
            {"class": "input input-bordered w-full", "placeholder": "email@example.com", "autocomplete": "email"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "input input-bordered w-full", "placeholder": "••••••••", "autocomplete": "current-password"}
        )

    def clean(self):
        # The actual Turnstile validation happens in the view
        # But we can add additional form-level validation here if needed
        return super().clean()
