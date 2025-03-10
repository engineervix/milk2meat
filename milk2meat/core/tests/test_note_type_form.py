import pytest

from milk2meat.core.forms import NoteTypeForm
from milk2meat.core.models import NoteType

pytestmark = pytest.mark.django_db


class TestNoteTypeForm:
    def test_form_valid(self):
        """Test that a valid form passes validation"""
        form_data = {
            "name": "Sermon Notes",
            "description": "Notes taken during sermons",
        }

        form = NoteTypeForm(data=form_data)
        assert form.is_valid(), f"Form errors: {form.errors}"

    def test_form_empty_description(self):
        """Test that an empty description is allowed"""
        form_data = {
            "name": "Sermon Notes",
            "description": "",
        }

        form = NoteTypeForm(data=form_data)
        assert form.is_valid(), f"Form errors: {form.errors}"

    def test_name_required(self):
        """Test that name is required"""
        form_data = {
            "description": "Some description",
        }

        form = NoteTypeForm(data=form_data)
        assert not form.is_valid()
        assert "name" in form.errors

    def test_name_uniqueness(self):
        """Test that name must be unique (case-insensitive)"""
        # Create a note type first
        NoteType.objects.create(name="Bible Study", description="Study of Bible passages")

        # Try to create another with the same name (different case)
        form_data = {
            "name": "bible study",  # lowercase version
            "description": "Another description",
        }

        form = NoteTypeForm(data=form_data)
        assert not form.is_valid()
        assert "name" in form.errors

        # Make sure a different name passes
        form_data["name"] = "Sermon Notes"
        form = NoteTypeForm(data=form_data)
        assert form.is_valid(), f"Form errors: {form.errors}"
