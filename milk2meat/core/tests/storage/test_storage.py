from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings

from milk2meat.core.storage import PrivateS3Storage, user_can_access_file
from milk2meat.users.factories import UserFactory

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestPrivateS3Storage:
    """Test the PrivateS3Storage class (used in production)"""

    def test_init_with_default_settings(self):
        """Test that storage can initialize with default settings"""
        # Should work even without explicit AWS settings
        storage = PrivateS3Storage()

        # Check defaults are applied
        assert storage.location == "files"
        assert storage.file_overwrite is False
        assert storage.signature_version == "s3v4"
        assert storage.addressing_style == "path"

    @override_settings(
        AWS_LOCATION="custom-files",
        AWS_S3_FILE_OVERWRITE=True,
        AWS_S3_SIGNATURE_VERSION="s3",
        AWS_S3_ADDRESSING_STYLE="path",
    )
    def test_init_with_custom_settings(self):
        """Test that storage uses custom settings when provided"""
        storage = PrivateS3Storage()

        # Check custom settings are applied
        assert storage.location == "custom-files"
        assert storage.file_overwrite is True
        assert storage.signature_version == "s3"
        assert storage.addressing_style == "path"

    @mock.patch("storages.backends.s3boto3.S3Boto3Storage.url")
    def test_url_method_with_expiration(self, mock_url):
        """Test the URL method generates signed URLs with expiration"""
        # Set up mock
        mock_url.return_value = "https://example.com/signed-url"

        # Create storage and call url
        storage = PrivateS3Storage()
        url = storage.url("test.pdf", expire=600)

        # Verify correct params are passed
        mock_url.assert_called_once_with("test.pdf", parameters={"ResponseContentDisposition": "inline"}, expire=600)

        # Check return value
        assert url == "https://example.com/signed-url"

    @mock.patch("storages.backends.s3boto3.S3Boto3Storage.url")
    def test_url_method_with_default_expiration(self, mock_url):
        """Test the URL method uses default expiration when not specified"""
        # Set up mock
        mock_url.return_value = "https://example.com/signed-url"

        # Create storage and call url with no explicit expiration
        with override_settings(AWS_SIGNED_URL_EXPIRE_SECONDS=400):
            storage = PrivateS3Storage()
            storage.url("test.pdf")

            # Verify correct default expiration is used
            mock_url.assert_called_once_with(
                "test.pdf", parameters={"ResponseContentDisposition": "inline"}, expire=400
            )

    @mock.patch("storages.backends.s3boto3.S3Boto3Storage.url")
    def test_url_method_handles_errors(self, mock_url):
        """Test the URL method handles errors properly"""
        # Set up mock to raise a specific exception
        test_error_message = "Test S3 connection error"
        mock_url.side_effect = ConnectionError(test_error_message)

        # Create storage
        storage = PrivateS3Storage()

        # Call should re-raise the exception with the same message
        with pytest.raises(ConnectionError, match=test_error_message):
            storage.url("test.pdf")


class TestAccessControl:
    """Test file access control functionality"""

    def test_user_can_access_file_owner(self):
        """Test that a user can access their own files"""
        user = UserFactory()
        file_path = f"notes/{user.id}/123/test.pdf"

        # User should be able to access their own file
        assert user_can_access_file(file_path, user) is True

    def test_user_cannot_access_other_users_file(self):
        """Test that a user cannot access another user's files"""
        user1 = UserFactory()
        user2 = UserFactory()

        file_path = f"notes/{user2.id}/123/test.pdf"

        # User1 should not be able to access User2's file
        assert user_can_access_file(file_path, user1) is False

    def test_user_cannot_access_non_notes_file(self):
        """Test that a user cannot access files outside the notes directory"""
        user = UserFactory()
        file_path = f"other_dir/{user.id}/123/test.pdf"

        # Files outside the notes directory should be inaccessible
        assert user_can_access_file(file_path, user) is False

    def test_unauthenticated_user_cannot_access_files(self):
        """Test that unauthenticated users cannot access files"""
        user = UserFactory()
        file_path = f"notes/{user.id}/123/test.pdf"

        # Create an unauthenticated user mock
        unauthenticated_user = mock.MagicMock()
        unauthenticated_user.is_authenticated = False

        # Unauthenticated users should not have access
        assert user_can_access_file(file_path, unauthenticated_user) is False
