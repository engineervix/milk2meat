import factory
from factory import Faker
from factory.django import DjangoModelFactory

from milk2meat.users.factories import UserFactory

from .models import Note, NoteType


class NoteTypeFactory(DjangoModelFactory):
    """Factory for creating NoteType objects"""

    name = Faker("word")
    description = Faker("sentence")

    class Meta:
        model = NoteType
        django_get_or_create = ["name"]


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
