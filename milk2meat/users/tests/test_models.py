import pytest
from django.db import IntegrityError

from milk2meat.users.factories import UserFactory
from milk2meat.users.models import User

pytestmark = pytest.mark.django_db


class TestUserModel:
    def test_user_factory(self):
        """Test that the user factory works properly"""
        user = UserFactory()
        assert isinstance(user, User)
        assert user.email
        assert user.password
        assert user.first_name
        assert user.last_name
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_user_email_is_unique(self):
        """Test that email addresses must be unique"""
        User.objects.create(email="test@example.com", password="password123", first_name="Test", last_name="User")

        # Attempting to create another user with the same email should fail
        with pytest.raises(IntegrityError):
            User.objects.create(
                email="test@example.com", password="password456", first_name="Another", last_name="User"
            )

    def test_user_string_representation(self):
        """Test the string representation of a user"""
        # User with first_name and last_name
        user1 = UserFactory(first_name="John", last_name="Doe", email="john@example.com")
        assert str(user1) == "John Doe"

        # User without first_name and last_name
        user2 = UserFactory(first_name="", last_name="", email="noreply@example.com")
        assert str(user2) == "noreply@example.com"

    def test_create_user_with_empty_email(self):
        """Test that creating a user with an empty email raises ValueError"""
        with pytest.raises(ValueError, match="The Email must be set"):
            User.objects.create_user(email="", password="password123")

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_user = User.objects.create_superuser(email="admin@example.com", password="admin123")
        assert admin_user.is_superuser is True
        assert admin_user.is_staff is True
        assert admin_user.is_active is True

    def test_create_superuser_with_invalid_flags(self):
        """Test that creating a superuser with invalid flags raises ValueError"""
        with pytest.raises(ValueError, match="Superuser must have is_staff=True"):
            User.objects.create_superuser(email="admin@example.com", password="admin123", is_staff=False)

        with pytest.raises(ValueError, match="Superuser must have is_superuser=True"):
            User.objects.create_superuser(email="admin@example.com", password="admin123", is_superuser=False)

    def test_username_field_is_none(self):
        """Test that the username field is None (using email instead)"""
        user = UserFactory()
        assert not hasattr(user, "username") or user.username is None

    def test_required_fields(self):
        """Test the required fields for user creation"""
        # USERNAME_FIELD should be 'email'
        assert User.USERNAME_FIELD == "email"

        # REQUIRED_FIELDS should be empty since email is the USERNAME_FIELD
        # and password is required by default
        assert User.REQUIRED_FIELDS == []
