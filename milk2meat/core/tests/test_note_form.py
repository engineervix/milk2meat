import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import ValidationError

from milk2meat.core.factories import BookFactory, NoteFactory, NoteTypeFactory
from milk2meat.core.forms import NoteForm
from milk2meat.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestNoteForm:
    def test_form_valid(self):
        """Test that a valid form passes validation"""
        user = UserFactory()
        note_type = NoteTypeFactory()

        form_data = {
            "title": "My Test Note",
            "note_type": note_type.id,
            "content": "# This is a test note\n\nWith some content",
            "tags_input": "faith,grace,salvation",
            "referenced_books_json": "[]",
        }

        form = NoteForm(data=form_data, user=user)
        assert form.is_valid(), f"Form errors: {form.errors}"

    def test_form_required_fields(self):
        """Test validation of required fields"""
        user = UserFactory()

        # Empty form
        form_data = {}
        form = NoteForm(data=form_data, user=user)
        assert not form.is_valid()
        assert "title" in form.errors
        assert "note_type" in form.errors

        # Just title
        form_data = {"title": "My Test Note"}
        form = NoteForm(data=form_data, user=user)
        assert not form.is_valid()
        assert "title" not in form.errors
        assert "note_type" in form.errors

    def test_form_file_upload(self):
        """Test form with file upload"""
        user = UserFactory()
        note_type = NoteTypeFactory()

        # Create a simple PDF file for testing
        pdf_content = b"%PDF-1.4\nThis is a test PDF file"
        pdf_file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")

        form_data = {
            "title": "Note with PDF",
            "note_type": note_type.id,
            "content": "# Note with attachment",
            "tags_input": "pdf,attachment",
            "referenced_books_json": "[]",
        }
        file_data = {"upload": pdf_file}

        form = NoteForm(data=form_data, files=file_data, user=user)
        assert form.is_valid(), f"Form errors: {form.errors}"

    def test_referenced_books_validation(self):
        """Test validation of referenced_books_json field"""
        user = UserFactory()
        note_type = NoteTypeFactory()
        book1 = BookFactory(title="Genesis")
        book2 = BookFactory(title="Exodus")

        base_data = {
            "title": "Bible Study Note",
            "note_type": note_type.id,
            "content": "# Bible Study Content",
        }

        # Invalid JSON
        form_data = {**base_data, "referenced_books_json": "{not valid json"}
        form = NoteForm(data=form_data, user=user)
        assert not form.is_valid()
        assert "referenced_books_json" in form.errors

        # Valid JSON but not a list
        form_data = {**base_data, "referenced_books_json": json.dumps({"not": "a list"})}
        form = NoteForm(data=form_data, user=user)
        assert not form.is_valid()
        assert "referenced_books_json" in form.errors

        # Valid JSON with referenced books
        form_data = {
            **base_data,
            "referenced_books_json": json.dumps(
                [{"id": book1.id, "title": book1.title}, {"id": book2.id, "title": book2.title}]
            ),
        }
        form = NoteForm(data=form_data, user=user)
        assert form.is_valid(), f"Form errors: {form.errors}"

        # Check that the cleaned data contains just the IDs
        assert sorted(form.cleaned_data["referenced_books_json"]) == sorted([book1.id, book2.id])

    def test_tags_input_processing(self):
        """Test processing of tags_input field"""
        user = UserFactory()
        note_type = NoteTypeFactory()

        base_data = {
            "title": "Tagged Note",
            "note_type": note_type.id,
            "content": "# Tagged Note Content",
            "referenced_books_json": "[]",
        }

        # Empty tags
        form_data = {**base_data, "tags_input": ""}
        form = NoteForm(data=form_data, user=user)
        assert form.is_valid(), f"Form errors: {form.errors}"
        assert form.cleaned_data["tags_input"] == []

        # Multiple tags
        form_data = {**base_data, "tags_input": "faith,grace,salvation"}
        form = NoteForm(data=form_data, user=user)
        assert form.is_valid(), f"Form errors: {form.errors}"
        assert set(form.cleaned_data["tags_input"]) == {"faith", "grace", "salvation"}

        # Tags with spaces
        form_data = {**base_data, "tags_input": "faith, grace , salvation "}
        form = NoteForm(data=form_data, user=user)
        assert form.is_valid(), f"Form errors: {form.errors}"
        assert set(form.cleaned_data["tags_input"]) == {"faith", "grace", "salvation"}

    def test_form_save_with_user(self):
        """Test saving form sets the owner correctly"""
        user = UserFactory()
        note_type = NoteTypeFactory()

        form_data = {
            "title": "My Test Note",
            "note_type": note_type.id,
            "content": "# This is a test note\n\nWith some content",
            "tags_input": "faith,grace",
            "referenced_books_json": "[]",
        }

        form = NoteForm(data=form_data, user=user)
        assert form.is_valid(), f"Form errors: {form.errors}"

        # Set the owner explicitly
        form.instance.owner = user

        note = form.save(commit=True)
        assert note.owner == user
        assert note.title == "My Test Note"
        assert note.note_type == note_type
        assert {tag.name for tag in note.tags.all()} == {"faith", "grace"}

    def test_form_saving_without_user_fails(self):
        """Test that saving a form without user fails"""
        note_type = NoteTypeFactory()

        form_data = {
            "title": "My Test Note",
            "note_type": note_type.id,
            "content": "# This is a test note\n\nWith some content",
        }

        # Create form without user
        form = NoteForm(data=form_data)
        assert form.is_valid(), f"Form errors: {form.errors}"

        # Saving should raise ValidationError about owner
        with pytest.raises(ValidationError) as exc_info:
            form.save(commit=True)

        # Check that the error is about the owner field
        assert "owner" in str(exc_info.value)

    def test_form_for_existing_note(self):
        """Test editing an existing note"""
        user = UserFactory()
        note_type = NoteTypeFactory()
        book = BookFactory()

        # Create a note with tags and references
        note = NoteFactory(title="Original Title", content="Original content", note_type=note_type, owner=user)
        note.tags.add("original", "tag")
        note.referenced_books.add(book)

        # Now update it
        form_data = {
            "title": "Updated Title",
            "note_type": note_type.id,
            "content": "Updated content",
            "tags_input": "updated,tags",
            "referenced_books_json": "[]",  # Remove all references
        }

        form = NoteForm(data=form_data, instance=note, user=user)
        assert form.is_valid(), f"Form errors: {form.errors}"

        updated_note = form.save()
        assert updated_note.pk == note.pk  # Same note
        assert updated_note.title == "Updated Title"
        assert updated_note.content == "Updated content"
        assert updated_note.note_type == note_type
        assert updated_note.owner == user
        assert {tag.name for tag in updated_note.tags.all()} == {"updated", "tags"}
        assert updated_note.referenced_books.count() == 0  # References removed
