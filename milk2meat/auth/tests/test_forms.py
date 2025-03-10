import pytest
from django.contrib.auth import get_user_model

from milk2meat.auth.forms import TurnstileLoginForm

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestTurnstileLoginForm:
    def test_form_init(self):
        """Test that the form initializes with correct attributes"""
        form = TurnstileLoginForm()

        # Check username field has the expected attributes
        assert form.fields["username"].widget.attrs.get("class") == "input input-bordered w-full"
        assert form.fields["username"].widget.attrs.get("placeholder") == "email@example.com"
        assert form.fields["username"].widget.attrs.get("autocomplete") == "email"

        # Check password field
        assert form.fields["password"].widget.attrs.get("class") == "input input-bordered w-full"
        assert form.fields["password"].widget.attrs.get("placeholder") == "••••••••"
        assert form.fields["password"].widget.attrs.get("autocomplete") == "current-password"

    def test_form_validation_valid_credentials(self):
        """Test form validation with valid credentials"""
        # Create a user for testing
        user = User.objects.create_user(email="test@example.com", password="correctpassword")

        # Form data with correct credentials
        form_data = {
            "username": "test@example.com",
            "password": "correctpassword",
        }

        form = TurnstileLoginForm(data=form_data)
        assert form.is_valid(), f"Form errors: {form.errors}"

        # Check that form.get_user() returns the correct user
        assert form.get_user() == user

    def test_form_validation_invalid_credentials(self):
        """Test form validation with invalid credentials"""
        # Create a user for testing
        User.objects.create_user(email="test@example.com", password="correctpassword")

        # Form data with incorrect password
        form_data = {
            "username": "test@example.com",
            "password": "wrongpassword",
        }

        form = TurnstileLoginForm(data=form_data)
        assert not form.is_valid()
        assert form.non_field_errors()

    def test_form_validation_nonexistent_user(self):
        """Test form validation with nonexistent user"""
        form_data = {
            "username": "nonexistent@example.com",
            "password": "anypassword",
        }

        form = TurnstileLoginForm(data=form_data)
        assert not form.is_valid()
        assert form.non_field_errors()

    def test_form_empty_fields(self):
        """Test form validation with empty fields"""
        # Empty form
        form = TurnstileLoginForm(data={})
        assert not form.is_valid()
        assert "username" in form.errors
        assert "password" in form.errors

        # Empty username
        form_data = {
            "password": "anypassword",
        }
        form = TurnstileLoginForm(data=form_data)
        assert not form.is_valid()
        assert "username" in form.errors

        # Empty password
        form_data = {
            "username": "test@example.com",
        }
        form = TurnstileLoginForm(data=form_data)
        assert not form.is_valid()
        assert "password" in form.errors
