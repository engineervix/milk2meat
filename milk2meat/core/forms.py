import json

from django import forms
from django.core.exceptions import ValidationError

from .models import Book


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
