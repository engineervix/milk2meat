import factory
from factory import Faker
from factory.django import DjangoModelFactory

from .models import Book, Testament


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
