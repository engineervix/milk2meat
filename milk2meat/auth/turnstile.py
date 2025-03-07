import logging

import requests
from django.conf import settings
from django.http import HttpRequest

logger = logging.getLogger(__name__)


class TurnstileValidationError(Exception):
    """Exception raised when Turnstile validation fails."""

    pass


def validate_turnstile(request: HttpRequest) -> bool:
    """
    Validate Cloudflare Turnstile token from request.

    Args:
        request: The HTTP request containing the Turnstile token

    Returns:
        bool: True if validation passes, False otherwise

    Raises:
        TurnstileValidationError: If validation fails due to configuration or network issues
    """
    # Skip validation in development mode or when explicitly configured to skip
    if settings.TURNSTILE_SKIP_VALIDATION:
        logger.debug("Skipping Turnstile validation in development mode")
        return True

    # Check if secret key is configured
    if not settings.TURNSTILE_SECRET_KEY:
        logger.error("Turnstile secret key not configured")
        raise TurnstileValidationError("Turnstile secret key not configured")

    # Get token from request
    token = request.POST.get("cf-turnstile-response")
    if not token:
        logger.info(
            "Missing Turnstile response token", extra={"ip": request.META.get("REMOTE_ADDR"), "path": request.path}
        )
        return False

    # Prepare validation data
    data = {
        "secret": settings.TURNSTILE_SECRET_KEY,
        "response": token,
        "remoteip": request.META.get("REMOTE_ADDR", ""),
    }

    try:
        # Make API request to Cloudflare
        response = requests.post(settings.TURNSTILE_VERIFY_URL, data=data, timeout=5)
        response.raise_for_status()
        result = response.json()

        if not result.get("success", False):
            error_codes = result.get("error-codes", [])
            logger.warning(
                "Failed Turnstile validation",
                extra={
                    "ip": request.META.get("REMOTE_ADDR"),
                    "path": request.path,
                    "errors": error_codes,
                },
            )
            return False

        return True

    except requests.RequestException as e:
        logger.error(
            f"Turnstile validation request error: {str(e)}",
            exc_info=True,
            extra={"ip": request.META.get("REMOTE_ADDR"), "path": request.path},
        )
        raise TurnstileValidationError(f"Turnstile validation request failed: {str(e)}") from e
