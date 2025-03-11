import pytest
from django.core.exceptions import ValidationError

from milk2meat.core.factories import BookFactory
from milk2meat.core.models import Book, Testament

pytestmark = pytest.mark.django_db


class TestBookModel:
    def test_book_creation(self):
        """Test that a book can be created"""
        book = BookFactory()
        assert isinstance(book, Book)
        assert book.title
        assert book.number > 0
        assert book.testament in [Testament.OT, Testament.NT]

    def test_book_string_representation(self):
        """Test the string representation of a book"""
        book = BookFactory(title="Genesis")
        assert str(book) == "Genesis"

    def test_book_ordering(self):
        """Test that books are ordered by number"""
        BookFactory(title="Genesis", number=1)
        BookFactory(title="Exodus", number=2)
        BookFactory(title="Leviticus", number=3)

        books = Book.objects.all()
        assert books[0].title == "Genesis"
        assert books[1].title == "Exodus"
        assert books[2].title == "Leviticus"

    def test_book_number_validators(self):
        """Test the validators for the book number field"""
        # Test minimum value
        with pytest.raises(ValidationError):
            book = BookFactory(number=0)
            book.full_clean()

        # Test maximum value
        with pytest.raises(ValidationError):
            book = BookFactory(number=67)
            book.full_clean()

        # Test valid values
        book1 = BookFactory(number=1)
        book1.full_clean()
        book66 = BookFactory(number=66)
        book66.full_clean()

    def test_book_chapters_validator(self):
        """Test the validator for the chapters field"""
        # Test maximum value
        with pytest.raises(ValidationError):
            book = BookFactory(chapters=151)
            book.full_clean()

        # Test valid values
        book = BookFactory(chapters=150)  # Maximum chapters (Psalms)
        book.full_clean()

    def test_book_timeline_json(self):
        """Test the timeline JSON field"""
        timeline_data = {
            "events": [
                {"date": "4000 B.C.", "description": "Creation"},
                {"date": "2500 B.C.", "description": "Noah's Flood"},
            ]
        }
        book = BookFactory(timeline=timeline_data)
        assert book.timeline == timeline_data
        assert len(book.timeline["events"]) == 2
        assert book.timeline["events"][0]["date"] == "4000 B.C."
