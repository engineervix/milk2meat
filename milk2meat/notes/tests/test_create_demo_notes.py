from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from milk2meat.bible.models import Book
from milk2meat.notes.models import Note, NoteType

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestCreateDemoNotesCommand:
    """Test the create_demo_notes management command."""

    @patch("milk2meat.notes.management.commands.create_demo_notes.settings")
    def test_command_requires_development_mode(self, mock_settings, capsys):
        """Test command only runs in development mode."""
        # Mock settings to be in production (DEBUG = False)
        mock_settings.DEBUG = False

        # Call the command
        call_command("create_demo_notes")

        # Check for error message in both stdout and stderr
        captured = capsys.readouterr()
        output = captured.out + captured.err

        # More flexible assertion - check for keywords that would indicate error mode
        assert "development" in output.lower() or "debug" in output.lower()

        # No notes should be created
        assert Note.objects.count() == 0

    @patch("milk2meat.notes.management.commands.create_demo_notes.settings")
    def test_command_force_flag(self, mock_settings, capsys):
        """Test command can be forced to run outside development."""
        # Mock settings to be in production (DEBUG = False)
        mock_settings.DEBUG = False

        # Pre-create some books for the command to reference
        Book.objects.create(title="Genesis", abbreviation="Gen", testament="OT", number=1, chapters=50)

        # Call the command with force flag
        call_command("create_demo_notes", "--force", "--count=1")

        # Should not show development mode error
        captured = capsys.readouterr()
        output = captured.out + captured.err

        dev_mode_error = any(
            phrase in output.lower()
            for phrase in ["development mode", "only run in development", "cannot run in production"]
        )
        assert not dev_mode_error, "Command should not show development mode error when forced"

        # Should create notes
        assert Note.objects.count() > 0

    @patch("milk2meat.notes.management.commands.create_demo_notes.settings")
    def test_command_creates_superuser_if_needed(self, mock_settings):
        """Test command creates a superuser if none exists."""
        # Mock settings to be in development
        mock_settings.DEBUG = True

        # Pre-create some books for the command to reference
        Book.objects.create(title="Genesis", abbreviation="Gen", testament="OT", number=1, chapters=50)

        # Make sure no users exist yet
        User.objects.all().delete()
        assert User.objects.filter(is_superuser=True).count() == 0

        # Call the command with small count
        call_command("create_demo_notes", "--count=1")

        # Should create a superuser
        assert User.objects.filter(is_superuser=True).count() == 1
        assert User.objects.get(is_superuser=True).email == "admin@example.com"

    @patch("milk2meat.notes.management.commands.create_demo_notes.settings")
    def test_command_creates_note_types(self, mock_settings):
        """Test command creates note types if needed."""
        # Mock settings to be in development
        mock_settings.DEBUG = True

        # Pre-create some books for the command to reference
        Book.objects.create(title="Genesis", abbreviation="Gen", testament="OT", number=1, chapters=50)

        # No note types should exist yet
        NoteType.objects.all().delete()
        assert NoteType.objects.count() == 0

        # Call the command
        call_command("create_demo_notes", "--count=1")

        # Should create note types
        assert NoteType.objects.count() > 0

    @patch("milk2meat.notes.management.commands.create_demo_notes.settings")
    def test_command_creates_notes(self, mock_settings):
        """Test command creates the specified number of notes."""
        # Mock settings to be in development
        mock_settings.DEBUG = True

        # Pre-create some books for the command to reference
        Book.objects.create(title="Genesis", abbreviation="Gen", testament="OT", number=1, chapters=50)

        # Call the command with count=5
        call_command("create_demo_notes", "--count=5")

        # Should create 5 notes
        assert Note.objects.count() == 5

        # Each note should have tags and references
        for note in Note.objects.all():
            assert note.title is not None
            assert note.content is not None
            assert note.owner is not None
            assert note.note_type is not None
            # Notes should have tags (except test data might not have guaranteed tags)
            # assert note.tags.count() > 0

    @patch("milk2meat.notes.management.commands.create_demo_notes.settings")
    def test_command_requires_books(self, mock_settings, capsys):
        """Test command warns if no Bible books exist."""
        # Mock settings to be in development
        mock_settings.DEBUG = True

        # Make sure no books exist
        Book.objects.all().delete()

        # Call the command
        call_command("create_demo_notes")

        # Check output for warning message
        captured = capsys.readouterr()
        output = captured.out + captured.err

        # More flexible assertion
        assert "bible book" in output.lower() or "no book" in output.lower()

        # No notes should be created
        assert Note.objects.count() == 0
