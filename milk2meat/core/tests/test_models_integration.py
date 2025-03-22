import pytest

from milk2meat.bible.factories import BookFactory
from milk2meat.bible.models import Book
from milk2meat.notes.factories import NoteFactory, NoteTypeFactory
from milk2meat.notes.models import Note, NoteType
from milk2meat.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestModelIntegration:
    """Integration tests for the core models."""

    def test_full_note_creation_flow(self):
        """Test the complete flow of creating a note with references and tags."""
        # Create a user
        user = UserFactory(email="studier@example.com")

        # Create note type
        note_type = NoteTypeFactory(name="Bible Study", description="In-depth study of Bible passages")

        # Create some books
        genesis = BookFactory(title="Genesis", abbreviation="Gen.", testament="OT", number=1, chapters=50)
        exodus = BookFactory(title="Exodus", abbreviation="Ex.", testament="OT", number=2, chapters=40)

        # Create a note referencing the books
        note = NoteFactory(
            title="Creation Study",
            content="# Creation\n\nIn the beginning, God created the heavens and the earth...",
            note_type=note_type,
            owner=user,
            referenced_books=[genesis, exodus],
        )

        # Add tags to the note
        note.tags.add("creation", "genesis", "beginning")

        # Verify all relationships are correct
        assert Note.objects.count() == 1
        assert Book.objects.count() == 2
        assert NoteType.objects.count() == 1

        # Check note details
        retrieved_note = Note.objects.get(pk=note.pk)
        assert retrieved_note.title == "Creation Study"
        assert retrieved_note.owner == user
        assert retrieved_note.note_type == note_type
        assert retrieved_note.referenced_books.count() == 2
        assert list(retrieved_note.referenced_books.all().order_by("number")) == [genesis, exodus]
        assert retrieved_note.tags.count() == 3
        assert {tag.name for tag in retrieved_note.tags.all()} == {"creation", "genesis", "beginning"}

        # Check slug was created correctly
        assert retrieved_note.slug == "creation-study"
