import pytest
from django.core.management import call_command

from milk2meat.core.models import Book, Testament

pytestmark = pytest.mark.django_db


class TestPopulateBibleBooksCommand:
    """Test the populate_bible_books management command."""

    def test_command_creates_books(self):
        """Test the command creates all 66 Bible books."""
        # Make sure no books exist initially
        Book.objects.all().delete()
        assert Book.objects.count() == 0

        # Call the command
        call_command("populate_bible_books")

        # Should create 66 books
        assert Book.objects.count() == 66

        # Check for correct distribution between testaments
        assert Book.objects.filter(testament=Testament.OT).count() == 39
        assert Book.objects.filter(testament=Testament.NT).count() == 27

        # Check for specific books
        assert Book.objects.filter(title="Genesis").exists()
        assert Book.objects.filter(title="Revelation").exists()
        assert Book.objects.filter(title="Psalms", chapters=150).exists()

        # Verify book attributes
        genesis = Book.objects.get(title="Genesis")
        assert genesis.testament == Testament.OT
        assert genesis.number == 1
        assert genesis.chapters == 50
        assert genesis.abbreviation == "Gen."

        matthew = Book.objects.get(title="Matthew")
        assert matthew.testament == Testament.NT
        assert matthew.number == 40
        assert matthew.chapters == 28

    def test_command_aborts_if_books_exist(self, capsys):
        """Test the command aborts if books already exist in the database."""
        # Create a book
        Book.objects.create(title="Existing Book", abbreviation="Ex", testament=Testament.OT, number=1, chapters=10)

        # Call the command
        call_command("populate_bible_books")

        # Check output for warning message - capture both stdout and stderr
        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "already exist" in output.lower() or "abort" in output.lower()

        # Should still have just the one book we created
        assert Book.objects.count() == 1
        assert Book.objects.filter(title="Existing Book").exists()

    def test_command_creates_books_in_correct_order(self):
        """Test books are created with the correct numbering and order."""
        # Make sure no books exist initially
        Book.objects.all().delete()

        # Call the command
        call_command("populate_bible_books")

        # Check the order of books matches their canonical order
        books = Book.objects.all().order_by("number")

        # First book should be Genesis
        assert books[0].title == "Genesis"
        assert books[0].number == 1

        # Book #39 should be Malachi (last OT book)
        assert books[38].title == "Malachi"
        assert books[38].number == 39

        # Book #40 should be Matthew (first NT book)
        assert books[39].title == "Matthew"
        assert books[39].number == 40

        # Last book should be Revelation
        assert books[65].title == "Revelation"
        assert books[65].number == 66

    def test_special_case_books(self):
        """Test books with specific characteristics are created correctly."""
        # Call the command
        Book.objects.all().delete()
        call_command("populate_bible_books")

        # Psalms should have 150 chapters
        psalms = Book.objects.get(title="Psalms")
        assert psalms.chapters == 150

        # Obadiah should have 1 chapter
        obadiah = Book.objects.get(title="Obadiah")
        assert obadiah.chapters == 1

        # Books with same name but different numbers
        samuel1 = Book.objects.get(title="1 Samuel")
        samuel2 = Book.objects.get(title="2 Samuel")

        assert samuel1.number == 9
        assert samuel2.number == 10
        assert samuel1.abbreviation == "1 Sam."
        assert samuel2.abbreviation == "2 Sam."
