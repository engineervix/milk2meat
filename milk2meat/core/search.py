from watson import search as watson

from .models import Book, Note


def register_watson_models():
    """Register models with django-watson for full-text search"""

    # Register Note model with relevant fields
    watson.register(
        Note,
        fields=("title", "content"),
        store=("note_type__name", "updated_at"),
    )

    # Register Book model with relevant fields
    watson.register(
        Book,
        fields=(
            "title",
            "title_and_author",
            "date_and_occasion",
            "characteristics_and_themes",
            "christ_in_book",
            "outline",
        ),
        store=("testament", "chapters"),
    )
