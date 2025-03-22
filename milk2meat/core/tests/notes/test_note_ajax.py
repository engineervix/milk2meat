"""
Tests for the AJAX-based note creation and editing functionality.

This test module verifies the backend implementation of AJAX endpoints for note creation
and editing, which allows users to save notes without page reloads. The tests cover:

1. Authentication requirements for AJAX endpoints
2. Creating notes via AJAX with tags, content, and file attachments
3. Updating existing notes via AJAX
4. Permission validation (users can only edit their own notes)
5. Validation error handling
"""

import json
import uuid

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from milk2meat.core.factories import NoteFactory, NoteTypeFactory
from milk2meat.core.models import Note
from milk2meat.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestNoteAjaxViews:
    def test_login_required_for_create(self, client):
        """Test that login is required for AJAX note creation"""
        url = reverse("core:note_create_ajax")
        response = client.post(url, {}, content_type="application/json")
        assert response.status_code == 302  # Redirect to login page

    def test_login_required_for_update(self, client):
        """Test that login is required for AJAX note update"""
        note = NoteFactory()
        url = reverse("core:note_update_ajax", kwargs={"pk": note.pk})
        response = client.post(url, {}, content_type="application/json")
        assert response.status_code == 302  # Redirect to login page

    def test_create_note_ajax_success(self, client):
        """Test successful creation of a note via AJAX"""
        user = UserFactory()
        client.force_login(user)
        note_type = NoteTypeFactory()

        # Prepare form data
        form_data = {
            "title": "Test Note via AJAX",
            "note_type": note_type.id,
            "content": "This is a test note created via AJAX",
            "tags_input": "ajax,test",
            "referenced_books_json": "[]",
        }

        url = reverse("core:note_create_ajax")
        response = client.post(url, form_data)

        # Verify response
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["success"] is True
        assert data["is_new"] is True
        assert "id" in data["note"]
        assert data["note"]["title"] == "Test Note via AJAX"

        # Verify note was created in database
        note_id = uuid.UUID(data["note"]["id"])
        note = Note.objects.get(pk=note_id)
        assert note.title == "Test Note via AJAX"
        assert note.content == "This is a test note created via AJAX"
        assert note.owner == user
        assert sorted(note.tags.names()) == ["ajax", "test"]

    def test_update_note_ajax_success(self, client):
        """Test successful update of a note via AJAX"""
        user = UserFactory()
        note_type = NoteTypeFactory()
        note = NoteFactory(owner=user, note_type=note_type, title="Original Title")

        client.force_login(user)

        # Prepare update data
        form_data = {
            "title": "Updated Title via AJAX",
            "note_type": note_type.id,
            "content": "This is updated content",
            "tags_input": "updated,ajax",
            "referenced_books_json": "[]",
        }

        url = reverse("core:note_update_ajax", kwargs={"pk": note.pk})
        response = client.post(url, form_data)

        # Verify response
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["success"] is True
        assert data["is_new"] is False
        assert data["note"]["title"] == "Updated Title via AJAX"

        # Verify note was updated in database
        note.refresh_from_db()
        assert note.title == "Updated Title via AJAX"
        assert note.content == "This is updated content"
        assert sorted(note.tags.names()) == ["ajax", "updated"]

    def test_update_other_users_note_forbidden(self, client):
        """Test that users cannot update notes owned by others via AJAX"""
        user1 = UserFactory()
        user2 = UserFactory()
        note = NoteFactory(owner=user2)  # Note owned by user2

        # Log in as user1
        client.force_login(user1)

        form_data = {
            "title": "Trying to update someone else's note",
            "note_type": note.note_type.id,
        }

        url = reverse("core:note_update_ajax", kwargs={"pk": note.pk})
        response = client.post(url, form_data)

        # Should return permission denied
        assert response.status_code == 403
        data = json.loads(response.content)
        assert data["success"] is False

    def test_create_note_ajax_with_validation_errors(self, client):
        """Test AJAX note creation with validation errors"""
        user = UserFactory()
        client.force_login(user)

        # Submit incomplete form data (missing required fields)
        form_data = {
            # Title is missing
            # Note type is missing
        }

        url = reverse("core:note_create_ajax")
        response = client.post(url, form_data)

        # Should return validation errors
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data["success"] is False
        assert "errors" in data
        assert "title" in data["errors"]  # Title is required
        assert "note_type" in data["errors"]  # Note type is required

    def test_create_note_ajax_with_file_upload(self, client):
        """Test note creation with file upload via AJAX"""
        user = UserFactory()
        client.force_login(user)
        note_type = NoteTypeFactory()

        # Create a test file
        test_file = SimpleUploadedFile(
            name="test_file.pdf",
            content=b"%PDF-1.5\n%\xff\xff\xff\xff\ntest pdf content",
            content_type="application/pdf",
        )

        # Prepare form data with file
        form_data = {
            "title": "Note with File",
            "note_type": note_type.id,
            "content": "This note has a file attachment",
            "tags_input": "file,upload",
            "upload": test_file,
            "referenced_books_json": json.dumps([]),
        }

        url = reverse("core:note_create_ajax")
        response = client.post(url, form_data, format="multipart")

        # Verify response
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["success"] is True

        # Verify file was attached to note
        note_id = uuid.UUID(data["note"]["id"])
        note = Note.objects.get(pk=note_id)
        assert note.upload is not None
        assert "test_file.pdf" in note.upload.name

    def test_update_note_ajax_with_file_deletion(self, client):
        """Test successful deletion of a file attachment via AJAX"""
        user = UserFactory()
        note_type = NoteTypeFactory()

        # Create a test file
        test_file = SimpleUploadedFile(
            name="test_file.pdf",
            content=b"%PDF-1.5\n%\xff\xff\xff\xff\ntest pdf content",
            content_type="application/pdf",
        )

        # Create note with attached file
        note = NoteFactory(owner=user, note_type=note_type, title="Note with File", upload=test_file)

        # Verify file exists
        assert note.upload is not None

        client.force_login(user)

        # Prepare update data with delete_upload=true
        form_data = {
            "title": "Updated Title - File Deleted",
            "note_type": note_type.id,
            "content": "This note had a file attachment that was deleted",
            "tags_input": "file,deleted",
            "referenced_books_json": "[]",
            "delete_upload": "true",
        }

        url = reverse("core:note_update_ajax", kwargs={"pk": note.pk})
        response = client.post(url, form_data)

        # Verify response
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["success"] is True

        # Verify file was deleted
        note.refresh_from_db()
        assert note.upload is None or note.upload == ""
