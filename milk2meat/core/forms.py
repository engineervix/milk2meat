import json

import nh3
from django import forms
from django.core.exceptions import ValidationError

from .models import Book, Note, NoteType
from .utils.markdown import parse_markdown


class BookEditForm(forms.ModelForm):
    """Form for editing Bible Book information"""

    timeline = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Book
        fields = [
            "title_and_author",
            "date_and_occasion",
            "characteristics_and_themes",
            "christ_in_book",
            "outline",
            "timeline",
        ]

    def clean_title_and_author(self):
        """Sanitize markdown content"""
        data = self.cleaned_data.get("title_and_author", "")
        # We parse (and sanitize) the markdown to ensure it doesn't contain harmful content
        # But we store the original markdown text for editing
        if data:
            parse_markdown(data)  # This will raise an exception if content can't be sanitized
        return data

    def clean_date_and_occasion(self):
        """Sanitize markdown content"""
        data = self.cleaned_data.get("date_and_occasion", "")
        if data:
            parse_markdown(data)
        return data

    def clean_characteristics_and_themes(self):
        """Sanitize markdown content"""
        data = self.cleaned_data.get("characteristics_and_themes", "")
        if data:
            parse_markdown(data)
        return data

    def clean_christ_in_book(self):
        """Sanitize markdown content"""
        data = self.cleaned_data.get("christ_in_book", "")
        if data:
            parse_markdown(data)
        return data

    def clean_outline(self):
        """Sanitize markdown content"""
        data = self.cleaned_data.get("outline", "")
        if data:
            parse_markdown(data)
        return data

    def clean_timeline(self):
        """Validate timeline JSON data"""
        data = self.cleaned_data.get("timeline", "")

        if not data:
            return {}

        try:
            timeline_data = json.loads(data)

            # Validate structure (should have 'events' key with a list of event objects)
            if not isinstance(timeline_data, dict):
                raise ValidationError("Timeline data must be a JSON object")

            events = timeline_data.get("events", [])
            if not isinstance(events, list):
                raise ValidationError("Timeline events must be a list")

            # Validate each event (should have 'date' and 'description' fields)
            for event in events:
                if not isinstance(event, dict):
                    raise ValidationError("Each event must be an object")

                if "date" not in event or "description" not in event:
                    raise ValidationError("Each event must have 'date' and 'description' fields")

                # Sanitize event description as it may contain HTML
                if event.get("description"):
                    event["description"] = nh3.clean(event["description"], tags=set())

            return timeline_data

        except json.JSONDecodeError as e:
            raise ValidationError("Invalid JSON format") from e

    def save(self, commit=True):
        """Override save to handle the timeline field"""
        book = super().save(commit=False)

        # Save the timeline data to the model's JSONField
        book.timeline = self.cleaned_data.get("timeline", {})

        if commit:
            book.save()

        return book


class NoteTypeForm(forms.ModelForm):
    """Form for creating a new Note Type"""

    class Meta:
        model = NoteType
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_name(self):
        """Ensure name is unique (case-insensitive)"""
        name = self.cleaned_data.get("name")
        if name:
            if NoteType.objects.filter(name__iexact=name).exists():
                raise ValidationError("A note type with this name already exists.")
        return name


class NoteForm(forms.ModelForm):
    """Form for creating and editing Notes"""

    # A hidden field to store selected book references as JSON
    referenced_books_json = forms.CharField(widget=forms.HiddenInput(), required=False)

    # A hidden field to store selected tags
    tags_input = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Note
        fields = [
            "title",
            "note_type",
            "content",
            "upload",
            "referenced_books_json",
            "tags_input",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "input input-bordered", "placeholder": "Enter note title"}),
            "content": forms.Textarea(attrs={"data-editor": "content", "class": "textarea textarea-bordered h-40"}),
            "upload": forms.FileInput(attrs={"class": "hidden", "id": "file-upload"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Limit note_type choices to existing types
        self.fields["note_type"].queryset = NoteType.objects.all()
        self.fields["note_type"].widget.attrs.update({"class": "select select-bordered"})

        # If we're editing an existing note, populate the hidden fields
        if self.instance.pk:
            # Populate referenced books
            if self.instance.referenced_books.exists():
                books_data = [{"id": book.id, "title": book.title} for book in self.instance.referenced_books.all()]
                self.initial["referenced_books_json"] = json.dumps(books_data)

            # Populate tags
            if self.instance.tags.exists():
                tags_list = [tag.name for tag in self.instance.tags.all()]
                self.initial["tags_input"] = ",".join(tags_list)

    def clean_content(self):
        """Sanitize markdown content"""
        data = self.cleaned_data.get("content", "")
        if data:
            # Parse and sanitize the markdown to ensure it's safe
            parse_markdown(data)
        return data

    def clean_referenced_books_json(self):
        """Validate and process the referenced books JSON"""
        data = self.cleaned_data.get("referenced_books_json", "")

        if not data:
            return []

        try:
            books_data = json.loads(data)

            # Validate structure (should be a list of objects with id)
            if not isinstance(books_data, list):
                raise ValidationError("Referenced books data must be a list")

            # Extract just the IDs for saving to the many-to-many relationship
            book_ids = [book["id"] for book in books_data if "id" in book]
            return book_ids

        except json.JSONDecodeError as e:
            raise ValidationError("Invalid JSON format for referenced books") from e

    def clean_tags_input(self):
        """Process the tags input"""
        data = self.cleaned_data.get("tags_input", "")
        if not data:
            return []

        # Split by comma and strip whitespace
        tags = [tag.strip() for tag in data.split(",") if tag.strip()]
        return tags

    def save(self, commit=True):
        """Override save to handle referenced books and tags"""
        note = super().save(commit=False)

        # Set the owner if creating a new note
        if not note.pk and self.user:
            note.owner = self.user

        if commit:
            note.save()

            # Handle referenced books (clear and add)
            book_ids = self.cleaned_data.get("referenced_books_json", [])
            note.referenced_books.clear()
            if book_ids:
                note.referenced_books.add(*book_ids)

            # Handle tags (clear and add)
            tags = self.cleaned_data.get("tags_input", [])
            note.tags.clear()
            if tags:
                note.tags.add(*tags)

        return note
