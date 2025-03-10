from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestTurnstileLoginView:
    def test_login_view_get(self, client):
        """Test getting the login page"""
        url = reverse("auth:login")
        response = client.get(url)

        # Check response
        assert response.status_code == 200
        assert "form" in response.context
        assert "turnstile_site_key" in response.context
        assert "turnstile_enabled" in response.context

    def test_login_success(self, client):
        """Test successful login"""
        # Create a user
        User.objects.create_user(email="test@example.com", password="password123")

        # Mock the turnstile validation to always return True
        with patch("milk2meat.auth.views.validate_turnstile", return_value=True):
            # Submit login form
            login_data = {
                "username": "test@example.com",
                "password": "password123",
                "cf-turnstile-response": "mock-token",  # Mock token
            }

            url = reverse("auth:login")
            response = client.post(url, login_data)

            # Should redirect to dashboard
            assert response.status_code == 302
            assert response.url == reverse("dashboard")

            # Check user is authenticated
            user_is_authenticated = client.session.get("_auth_user_id") is not None
            assert user_is_authenticated

    def test_login_wrong_password(self, client):
        """Test login with wrong password"""
        # Create a user
        User.objects.create_user(email="test@example.com", password="password123")

        # Mock the turnstile validation to always return True
        with patch("milk2meat.auth.views.validate_turnstile", return_value=True):
            # Submit login form with wrong password
            login_data = {
                "username": "test@example.com",
                "password": "wrongpassword",
                "cf-turnstile-response": "mock-token",
            }

            url = reverse("auth:login")
            response = client.post(url, login_data)

            # Should show form errors
            assert response.status_code == 200
            assert "form" in response.context
            assert response.context["form"].errors

            # Check user is not authenticated
            user_is_authenticated = client.session.get("_auth_user_id") is not None
            assert not user_is_authenticated

    @patch("milk2meat.auth.views.settings.TURNSTILE_SKIP_VALIDATION", False)
    def test_login_turnstile_failed(self, client):
        """Test login with failed turnstile validation"""
        # Create a user
        User.objects.create_user(email="test@example.com", password="password123")

        # Mock the turnstile validation to fail
        with patch("milk2meat.auth.views.validate_turnstile", return_value=False):
            # Submit login form
            login_data = {
                "username": "test@example.com",
                "password": "password123",
                "cf-turnstile-response": "mock-token",
            }

            url = reverse("auth:login")
            response = client.post(url, login_data)

            # Should show error message
            assert response.status_code == 200

            # Check user is not authenticated
            user_is_authenticated = client.session.get("_auth_user_id") is not None
            assert not user_is_authenticated

    @patch("milk2meat.auth.views.settings.TURNSTILE_SKIP_VALIDATION", False)
    def test_login_turnstile_validation_error(self, client):
        """Test login with turnstile validation error"""
        # Create a user
        User.objects.create_user(email="test@example.com", password="password123")

        # Mock the turnstile validation to raise an exception
        with patch("milk2meat.auth.views.validate_turnstile", side_effect=Exception("Validation error")):
            # Submit login form
            login_data = {
                "username": "test@example.com",
                "password": "password123",
                "cf-turnstile-response": "mock-token",
            }

            url = reverse("auth:login")
            response = client.post(url, login_data)

            # Should show error message
            assert response.status_code == 200

            # Check user is not authenticated
            user_is_authenticated = client.session.get("_auth_user_id") is not None
            assert not user_is_authenticated

    def test_redirect_authenticated_user(self, client):
        """Test redirecting already authenticated users"""
        # Create and log in user
        user = User.objects.create_user(email="test@example.com", password="password123")
        client.force_login(user)

        # Try to access login page
        url = reverse("auth:login")
        response = client.get(url)

        # Should redirect to dashboard
        assert response.status_code == 302
        assert response.url == reverse("dashboard")


class TestLogoutView:
    def test_logout(self, client):
        """Test logging out"""
        # Create and log in user
        user = User.objects.create_user(email="test@example.com", password="password123")
        client.force_login(user)

        # Verify user is authenticated
        user_is_authenticated = client.session.get("_auth_user_id") is not None
        assert user_is_authenticated

        # Logout
        url = reverse("auth:logout")
        response = client.post(url)

        # Should redirect to login page
        assert response.status_code == 302
        assert response.url == reverse("auth:login")

        # Check user is no longer authenticated
        user_is_authenticated = client.session.get("_auth_user_id") is not None
        assert not user_is_authenticated

    def test_logout_requires_post(self, client):
        """Test that logout requires POST method"""
        # Create and log in user
        user = User.objects.create_user(email="test@example.com", password="password123")
        client.force_login(user)

        # Try to logout with GET
        url = reverse("auth:logout")
        response = client.get(url)

        # Should return method not allowed
        assert response.status_code == 405  # Method Not Allowed

        # User should still be authenticated
        user_is_authenticated = client.session.get("_auth_user_id") is not None
        assert user_is_authenticated
