import json

from django import forms
from django.core.exceptions import ValidationError

from milk2meat.core.utils.markdown import parse_markdown
from milk2meat.notes.models import Note, NoteType


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

    # A hidden field to track if the upload file should be deleted
    delete_upload = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Note
        fields = [
            "title",
            "note_type",
            "content",
            "upload",
            "referenced_books_json",
            "tags_input",
            "delete_upload",
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

        # Set the owner if creating a new note and owner isn't already set
        if not note.pk:
            # First, check if owner is already set by the view
            # (which might happen through form.instance.owner = user)
            if hasattr(note, "owner") and note.owner is not None:
                pass  # Owner already set by the view
            elif self.user:
                # Set from self.user if available
                note.owner = self.user
            else:
                # If we still don't have an owner, give up
                raise ValueError("Cannot create note: Couldn't determine who the owner is")

        # Handle file deletion if requested
        if self.cleaned_data.get("delete_upload") and note.upload:
            # Store the file to delete after saving
            file_to_delete = note.upload
            note.upload = None
        else:
            file_to_delete = None

        if commit:
            note.save()

            # Delete the file if needed
            if file_to_delete:
                # This will also remove the file from storage
                file_to_delete.delete(save=False)

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
