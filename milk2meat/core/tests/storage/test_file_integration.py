from unittest import mock

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from milk2meat.notes.factories import NoteFactory, NoteTypeFactory
from milk2meat.notes.models import Note
from milk2meat.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestNoteFileIntegration:
    """Integration tests for notes with files"""

    def test_note_upload_path(self):
        """Test the upload path generation for notes"""
        # Create a user and note type
        user = UserFactory()
        note_type = NoteTypeFactory()

        # Create a note with a pre-defined ID for testing
        test_uuid = "test-uuid"
        with mock.patch("uuid.uuid4", return_value=test_uuid):
            # We need to manually create the note object and set the ID
            note = Note(title="Test Note", owner=user, note_type=note_type)
            note.id = test_uuid  # Explicitly set the ID

            # Get the upload_to function from the field
            upload_to_func = note.upload.field.upload_to

            # Generate the upload path
            test_filename = "test file.pdf"
            upload_path = upload_to_func(note, test_filename)

            # Path should include user ID and note ID
            assert f"notes/{user.id}/test-uuid/test-file.pdf" == upload_path

    def test_get_secure_file_url_owner_access(self):
        """Test access to file URL for the note owner"""
        # Create a user and note with an uploaded file
        user = UserFactory()
        note_type = NoteTypeFactory()

        # Create a test PDF
        pdf_content = b"%PDF-1.4\nTest PDF"
        SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")

        # Create the note with the file - but with mocking
        # This approach bypasses actually creating the file and directly tests the URL access
        note = NoteFactory(title="Test Note", owner=user, note_type=note_type)

        # Instead of storing a real file, we'll mock the whole file field
        # Create a mock FieldFile with a controlled URL property
        mock_file = mock.MagicMock()
        mock_file.url = "/test-url/"

        # Replace the upload field with our mock
        with mock.patch.object(note, "upload", mock_file):
            url = note.get_secure_file_url(user)
            assert url == "/test-url/"

    def test_get_secure_file_url_other_user_access(self):
        """Test access to file URL for non-owner users"""
        # Create users and note with file
        owner = UserFactory()
        other_user = UserFactory()
        note_type = NoteTypeFactory()

        # Create a test PDF
        pdf_content = b"%PDF-1.4\nTest PDF"
        test_file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")

        note = NoteFactory(title="Test Note", owner=owner, note_type=note_type, upload=test_file)

        # Non-owner should get None
        url = note.get_secure_file_url(other_user)
        assert url is None

    def test_get_secure_file_url_no_file(self):
        """Test URL access when note has no file"""
        user = UserFactory()
        note_type = NoteTypeFactory()

        # Create note without a file
        note = NoteFactory(title="Test Note", owner=user, note_type=note_type, upload=None)

        # Should return None when no file exists
        url = note.get_secure_file_url(user)
        assert url is None

    def test_file_url_in_development(self):
        """Test file URL generation in development environment"""
        # Create a user and note with a file
        user = UserFactory()
        note_type = NoteTypeFactory()

        # Create the note but use a mock for testing
        note = NoteFactory(title="Test Note", owner=user, note_type=note_type)

        # Create a mock file field
        mock_file = mock.MagicMock()
        mock_file.url = "/files/test.pdf"

        # Replace the note's upload field with our mock
        with mock.patch.object(note, "upload", mock_file):
            # Verify the URL is returned correctly
            with mock.patch("django.conf.settings.DEBUG", True):
                url = note.get_secure_file_url(user)
                assert url == "/files/test.pdf"

    def test_file_url_in_production(self):
        """Test file URL generation in production environment"""
        # Create a user and note with a file
        user = UserFactory()
        note_type = NoteTypeFactory()

        # Create the note but use a mock for testing
        note = NoteFactory(title="Test Note", owner=user, note_type=note_type)

        # Create a mock file field
        mock_file = mock.MagicMock()
        mock_file.url = "https://example.com/signed-url"

        # Replace the note's upload field with our mock
        with mock.patch.object(note, "upload", mock_file):
            # Verify the URL is returned correctly
            with mock.patch("django.conf.settings.DEBUG", False):
                url = note.get_secure_file_url(user)
                assert url == "https://example.com/signed-url"
