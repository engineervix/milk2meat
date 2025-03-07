import json

import nh3
from django import forms
from django.core.exceptions import ValidationError

from .models import Book
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
