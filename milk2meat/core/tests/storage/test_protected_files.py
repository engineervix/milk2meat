import json
from unittest import mock

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from milk2meat.core.factories import NoteFactory, NoteTypeFactory
from milk2meat.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestServeProtectedFileView:
    """Test the serve_protected_file view"""

    def test_login_required(self, client):
        """Test that the view requires login"""
        # Create a note
        user = UserFactory()
        note = NoteFactory(owner=user)

        # Try to access the endpoint without logging in
        url = reverse("core:serve_protected_file", kwargs={"note_id": note.pk})
        response = client.get(url)

        # Should redirect to login
        assert response.status_code == 302
        assert "login" in response.url

    def test_serve_own_file(self, client):
        """Test serving the user's own file"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Create a note type
        note_type = NoteTypeFactory()

        # Create a test PDF
        pdf_content = b"%PDF-1.4\nTest PDF"
        test_file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")

        # Create a note with an upload
        note = NoteFactory(title="Test Note", owner=user, note_type=note_type, upload=test_file)

        # Mock the get_secure_file_url method
        with mock.patch("milk2meat.core.models.Note.get_secure_file_url") as mock_get_url:
            mock_get_url.return_value = "https://example.com/signed-url"

            # Request the file
            url = reverse("core:serve_protected_file", kwargs={"note_id": note.pk})
            response = client.get(url)

            # Check the response
            assert response.status_code == 200

            # Parse the JSON response
            data = json.loads(response.content)
            assert "url" in data
            assert data["url"] == "https://example.com/signed-url"

            # Verify the method was called with the correct user
            mock_get_url.assert_called_once_with(user)

    def test_cannot_serve_other_users_file(self, client):
        """Test that a user cannot access another user's files"""
        # Create two users
        user1 = UserFactory()
        user2 = UserFactory()

        # Log in as user1
        client.force_login(user1)

        # Create a note owned by user2
        note_type = NoteTypeFactory()
        pdf_content = b"%PDF-1.4\nTest PDF"
        test_file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")

        note = NoteFactory(title="Test Note", owner=user2, note_type=note_type, upload=test_file)

        # Request the file
        url = reverse("core:serve_protected_file", kwargs={"note_id": note.pk})
        response = client.get(url)

        # Should return 404 as user1 doesn't own the note
        assert response.status_code == 404

    def test_note_with_no_file(self, client):
        """Test requesting a note that has no file"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Create a note without a file
        note_type = NoteTypeFactory()
        note = NoteFactory(title="Test Note", owner=user, note_type=note_type, upload=None)

        # Request the file
        url = reverse("core:serve_protected_file", kwargs={"note_id": note.pk})
        response = client.get(url)

        # Should return 404 as there's no file
        assert response.status_code == 404

        # Parse the JSON response
        data = json.loads(response.content)
        assert "error" in data
        assert "no attached file" in data["error"].lower()

    def test_nonexistent_note(self, client):
        """Test requesting a file for a note that doesn't exist"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Request a file for a nonexistent note
        url = reverse("core:serve_protected_file", kwargs={"note_id": "00000000-0000-0000-0000-000000000000"})
        response = client.get(url)

        # Should return 404
        assert response.status_code == 404

    def test_secure_url_returns_none(self, client):
        """Test when get_secure_file_url returns None (denied access)"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Create a note with a file
        note_type = NoteTypeFactory()
        pdf_content = b"%PDF-1.4\nTest PDF"
        test_file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")

        note = NoteFactory(title="Test Note", owner=user, note_type=note_type, upload=test_file)

        # Mock get_secure_file_url to return None
        with mock.patch("milk2meat.core.models.Note.get_secure_file_url", return_value=None):
            # Request the file
            url = reverse("core:serve_protected_file", kwargs={"note_id": note.pk})
            response = client.get(url)

            # Should return 403 Forbidden
            assert response.status_code == 403

            # Parse the JSON response
            data = json.loads(response.content)
            assert "error" in data
            assert "permission" in data["error"].lower()
