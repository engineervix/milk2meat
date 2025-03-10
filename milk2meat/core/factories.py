import factory
from factory import Faker
from factory.django import DjangoModelFactory

from milk2meat.users.factories import UserFactory

from .models import Book, Note, NoteType, Testament


class NoteTypeFactory(DjangoModelFactory):
    """Factory for creating NoteType objects"""

    name = Faker("word")
    description = Faker("sentence")

    class Meta:
        model = NoteType
        django_get_or_create = ["name"]


class BookFactory(DjangoModelFactory):
    """Factory for creating Book objects"""

    title = Faker("word")
    abbreviation = Faker("pystr", max_chars=10)
    testament = factory.Iterator([Testament.OT, Testament.NT])
    number = factory.Sequence(lambda n: n + 1)  # Start at 1
    chapters = Faker("random_int", min=1, max=150)

    # Book introduction fields
    title_and_author = Faker("paragraph")
    date_and_occasion = Faker("paragraph")
    characteristics_and_themes = Faker("paragraph")
    christ_in_book = Faker("paragraph")
    outline = Faker("paragraph")
    timeline = factory.Dict({"events": []})

    class Meta:
        model = Book
        django_get_or_create = ["title", "number"]


class NoteFactory(DjangoModelFactory):
    """Factory for creating Note objects"""

    title = Faker("sentence")
    content = Faker("text")
    note_type = factory.SubFactory(NoteTypeFactory)
    owner = factory.SubFactory(UserFactory)

    class Meta:
        model = Note

    @factory.post_generation
    def referenced_books(self, create, extracted, **kwargs):
        """Add referenced books to the note"""
        if not create:
            return

        if extracted:
            for book in extracted:
                self.referenced_books.add(book)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        """Add tags to the note"""
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)
