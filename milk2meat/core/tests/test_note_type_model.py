import pytest
from django.db import IntegrityError

from milk2meat.core.factories import NoteTypeFactory
from milk2meat.core.models import NoteType

pytestmark = pytest.mark.django_db


class TestNoteTypeModel:
    def test_note_type_creation(self):
        """Test that a note type can be created"""
        note_type = NoteTypeFactory()
        assert isinstance(note_type, NoteType)
        assert note_type.name
        assert note_type.description

    def test_note_type_string_representation(self):
        """Test the string representation of a note type"""
        note_type = NoteTypeFactory(name="Bible Study")
        assert str(note_type) == "Bible Study"

    def test_note_type_unique_name(self):
        """Test that note type names must be unique"""
        # Create directly using the model instead of factory to avoid get_or_create behavior
        NoteType.objects.create(name="Bible Study", description="Description 1")

        # Attempting to create another with the same name should fail
        with pytest.raises(IntegrityError):
            NoteType.objects.create(name="Bible Study", description="Description 2")

    def test_blank_description_allowed(self):
        """Test that a blank description is allowed"""
        note_type = NoteTypeFactory(description="")
        assert note_type.description == ""
