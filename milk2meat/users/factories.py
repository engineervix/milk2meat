import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from factory import Faker
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    """Factory for creating Django User objects"""

    email = Faker("email")
    password = factory.LazyFunction(lambda: make_password("password"))
    first_name = Faker("first_name")
    last_name = Faker("last_name")

    class Meta:
        model = get_user_model()
        django_get_or_create = ["email"]
