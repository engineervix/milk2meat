from unittest.mock import MagicMock, patch

import pytest
from django.http import HttpRequest

from milk2meat.auth.turnstile import TurnstileValidationError, validate_turnstile


class TestTurnstileValidation:
    """Test the Turnstile validation function."""

    @patch("milk2meat.auth.turnstile.settings")
    def test_skip_validation_in_development(self, mock_settings):
        """Test validation is skipped in development mode."""
        # Configure settings to skip validation
        mock_settings.TURNSTILE_SKIP_VALIDATION = True
        mock_settings.TURNSTILE_SECRET_KEY = "test_secret_key"

        # Create a mock request
        request = HttpRequest()
        request.POST = {}

        # Validation should be skipped and return True
        result = validate_turnstile(request)
        assert result is True

    @patch("milk2meat.auth.turnstile.settings")
    def test_missing_secret_key(self, mock_settings):
        """Test error raised when secret key is not configured."""
        # Configure settings without a secret key
        mock_settings.TURNSTILE_SKIP_VALIDATION = False
        mock_settings.TURNSTILE_SECRET_KEY = None

        # Create a mock request
        request = HttpRequest()
        request.POST = {}

        # Should raise TurnstileValidationError
        with pytest.raises(TurnstileValidationError, match="Turnstile secret key not configured"):
            validate_turnstile(request)

    @patch("milk2meat.auth.turnstile.settings")
    def test_missing_token_in_request(self, mock_settings):
        """Test validation fails when token is missing from request."""
        # Configure settings
        mock_settings.TURNSTILE_SKIP_VALIDATION = False
        mock_settings.TURNSTILE_SECRET_KEY = "test_secret_key"

        # Create a mock request with empty POST
        request = HttpRequest()
        request.POST = {}
        request.META = {"REMOTE_ADDR": "127.0.0.1"}

        # Validation should fail due to missing token
        result = validate_turnstile(request)
        assert result is False

    @patch("milk2meat.auth.turnstile.settings")
    @patch("milk2meat.auth.turnstile.requests.post")
    def test_successful_validation(self, mock_post, mock_settings):
        """Test successful validation with valid token."""
        # Configure settings
        mock_settings.TURNSTILE_SKIP_VALIDATION = False
        mock_settings.TURNSTILE_SECRET_KEY = "test_secret_key"
        mock_settings.TURNSTILE_VERIFY_URL = "https://verify-test-url.com"

        # Create a mock request with token
        request = HttpRequest()
        request.POST = {"cf-turnstile-response": "valid_token"}
        request.META = {"REMOTE_ADDR": "127.0.0.1"}

        # Mock the response from Cloudflare
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        # Validation should succeed
        result = validate_turnstile(request)
        assert result is True

        # Check the request to Cloudflare was made correctly
        mock_post.assert_called_once_with(
            mock_settings.TURNSTILE_VERIFY_URL,
            data={
                "secret": "test_secret_key",
                "response": "valid_token",
                "remoteip": "127.0.0.1",
            },
            timeout=5,
        )

    @patch("milk2meat.auth.turnstile.settings")
    @patch("milk2meat.auth.turnstile.requests.post")
    def test_failed_validation(self, mock_post, mock_settings):
        """Test failed validation with invalid token."""
        # Configure settings
        mock_settings.TURNSTILE_SKIP_VALIDATION = False
        mock_settings.TURNSTILE_SECRET_KEY = "test_secret_key"
        mock_settings.TURNSTILE_VERIFY_URL = "https://verify-test-url.com"

        # Create a mock request with token
        request = HttpRequest()
        request.POST = {"cf-turnstile-response": "invalid_token"}
        request.META = {"REMOTE_ADDR": "127.0.0.1"}

        # Mock the response from Cloudflare
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": False, "error-codes": ["invalid-input-response"]}
        mock_post.return_value = mock_response

        # Validation should fail
        result = validate_turnstile(request)
        assert result is False

    @patch("milk2meat.auth.turnstile.settings")
    @patch("milk2meat.auth.turnstile.requests.post")
    def test_request_exception(self, mock_post, mock_settings):
        """Test handling of request exceptions."""
        # Configure settings
        mock_settings.TURNSTILE_SKIP_VALIDATION = False
        mock_settings.TURNSTILE_SECRET_KEY = "test_secret_key"
        mock_settings.TURNSTILE_VERIFY_URL = "https://verify-test-url.com"

        # Create a mock request with token
        request = HttpRequest()
        request.POST = {"cf-turnstile-response": "valid_token"}
        request.META = {"REMOTE_ADDR": "127.0.0.1"}

        # Mock a requests.RequestException
        from requests.exceptions import RequestException

        mock_post.side_effect = RequestException("Connection error")

        # Should raise TurnstileValidationError
        with pytest.raises(TurnstileValidationError, match="Turnstile validation request failed"):
            validate_turnstile(request)
