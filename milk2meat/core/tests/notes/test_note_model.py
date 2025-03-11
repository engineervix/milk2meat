import pytest
from django.utils.text import slugify

from milk2meat.core.factories import BookFactory, NoteFactory, NoteTypeFactory
from milk2meat.core.models import Note
from milk2meat.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestNoteModel:
    def test_note_creation(self):
        """Test that a note can be created"""
        note = NoteFactory()
        assert isinstance(note, Note)
        assert note.title
        assert note.content
        assert note.note_type
        assert note.owner
        assert note.slug == slugify(note.title)

    def test_note_string_representation(self):
        """Test the string representation of a note"""
        note = NoteFactory(title="My Bible Study Note")
        assert str(note) == "My Bible Study Note"

    def test_note_ordering(self):
        """Test that notes are ordered by updated_at and created_at descending"""
        # We'll have to manipulate the created_at and updated_at fields directly
        # because they're automatically set
        note1 = NoteFactory()
        note2 = NoteFactory()
        note3 = NoteFactory()

        # Manually update the dates in the database to test ordering
        # Setting note3 as most recently updated, note2 as second, note1 as oldest
        Note.objects.filter(pk=note3.pk).update(updated_at="2023-01-03 12:00:00+00:00")
        Note.objects.filter(pk=note2.pk).update(updated_at="2023-01-02 12:00:00+00:00")
        Note.objects.filter(pk=note1.pk).update(updated_at="2023-01-01 12:00:00+00:00")

        # Refresh from database
        note1.refresh_from_db()
        note2.refresh_from_db()
        note3.refresh_from_db()

        # Check ordering
        notes = Note.objects.all()
        assert notes[0].pk == note3.pk  # Most recently updated
        assert notes[1].pk == note2.pk
        assert notes[2].pk == note1.pk  # Oldest update

    def test_unique_slug_per_owner(self):
        """Test that slugs are unique per owner"""
        user1 = UserFactory()
        user2 = UserFactory()
        note_type = NoteTypeFactory()

        # Create two notes with the same title but different owners
        note1 = NoteFactory(title="My Note", owner=user1, note_type=note_type)
        note2 = NoteFactory(title="My Note", owner=user2, note_type=note_type)

        # Slugs should be the same because they belong to different owners
        assert note1.slug == note2.slug == "my-note"

        # Create another note with the same title for user1
        note3 = NoteFactory(title="My Note", owner=user1, note_type=note_type)

        # Slug should be different because user1 already has a note with that slug
        assert note3.slug == "my-note-1"

        # And one more to make sure the numbering works
        note4 = NoteFactory(title="My Note", owner=user1, note_type=note_type)
        assert note4.slug == "my-note-2"

    def test_note_with_referenced_books(self):
        """Test that a note can reference books"""
        book1 = BookFactory(title="Genesis")
        book2 = BookFactory(title="Exodus")

        note = NoteFactory(referenced_books=[book1, book2])

        assert note.referenced_books.count() == 2
        assert book1 in note.referenced_books.all()
        assert book2 in note.referenced_books.all()

    def test_note_with_tags(self):
        """Test that a note can have tags"""
        note = NoteFactory()

        # Add tags
        note.tags.add("salvation", "grace", "faith")

        assert note.tags.count() == 3
        assert "salvation" in [tag.name for tag in note.tags.all()]
        assert "grace" in [tag.name for tag in note.tags.all()]
        assert "faith" in [tag.name for tag in note.tags.all()]

    def test_get_queryset_for_user(self):
        """Test the custom manager method for getting user-specific notes"""
        user1 = UserFactory()
        user2 = UserFactory()

        # Create notes for both users
        note1 = NoteFactory(owner=user1)
        note2 = NoteFactory(owner=user1)
        note3 = NoteFactory(owner=user2)

        # Get notes for user1
        user1_notes = Note.objects.get_queryset_for_user(user1)
        assert user1_notes.count() == 2
        assert note1 in user1_notes
        assert note2 in user1_notes
        assert note3 not in user1_notes

        # Get notes for user2
        user2_notes = Note.objects.get_queryset_for_user(user2)
        assert user2_notes.count() == 1
        assert note3 in user2_notes
        assert note1 not in user2_notes
        assert note2 not in user2_notes

    def test_slug_is_updated_when_title_changes(self):
        """Test that the slug is updated when the title changes"""
        note = NoteFactory(title="Original Title")
        assert note.slug == "original-title"

        # Change the title and save
        note.title = "New Title"
        note.save()

        # Slug should be updated
        assert note.slug == "new-title"
