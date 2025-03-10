import json

import pytest

from milk2meat.core.factories import BookFactory
from milk2meat.core.forms import BookEditForm

pytestmark = pytest.mark.django_db


class TestBookEditForm:
    def test_form_valid(self):
        """Test that a valid form passes validation"""
        book = BookFactory()
        form_data = {
            "title_and_author": "# Genesis\n\nWritten by Moses",
            "date_and_occasion": "Around 1400 BC",
            "characteristics_and_themes": "Creation, Fall, Redemption",
            "christ_in_book": "Promised seed in Genesis 3:15",
            "outline": "1. Creation\n2. Fall\n3. Flood\n4. Abraham\n5. Isaac\n6. Jacob\n7. Joseph",
            "timeline": json.dumps({"events": [{"date": "4000 BC", "description": "Creation"}]}),
        }

        form = BookEditForm(data=form_data, instance=book)
        assert form.is_valid(), f"Form errors: {form.errors}"

    def test_form_empty_fields(self):
        """Test that empty fields are allowed (all fields are optional)"""
        book = BookFactory()
        form_data = {
            "title_and_author": "",
            "date_and_occasion": "",
            "characteristics_and_themes": "",
            "christ_in_book": "",
            "outline": "",
            "timeline": "",
        }

        form = BookEditForm(data=form_data, instance=book)
        assert form.is_valid(), f"Form errors: {form.errors}"

    def test_form_timeline_validation(self):
        """Test timeline JSON validation"""
        book = BookFactory()

        # Invalid JSON
        form_data = {
            "title_and_author": "",
            "date_and_occasion": "",
            "characteristics_and_themes": "",
            "christ_in_book": "",
            "outline": "",
            "timeline": "{not valid json",
        }
        form = BookEditForm(data=form_data, instance=book)
        assert not form.is_valid()
        assert "timeline" in form.errors

        # Valid JSON but wrong format (not an object)
        form_data = {
            "title_and_author": "",
            "date_and_occasion": "",
            "characteristics_and_themes": "",
            "christ_in_book": "",
            "outline": "",
            "timeline": json.dumps(["not", "an", "object"]),
        }
        form = BookEditForm(data=form_data, instance=book)
        assert not form.is_valid()
        assert "timeline" in form.errors

        # Valid JSON but missing events key
        form_data = {
            "title_and_author": "",
            "date_and_occasion": "",
            "characteristics_and_themes": "",
            "christ_in_book": "",
            "outline": "",
            "timeline": json.dumps({"wrong_key": []}),
        }
        form = BookEditForm(data=form_data, instance=book)
        assert not form.is_valid()
        assert "timeline" in form.errors

        # Valid JSON with events not being a list
        form_data = {
            "title_and_author": "",
            "date_and_occasion": "",
            "characteristics_and_themes": "",
            "christ_in_book": "",
            "outline": "",
            "timeline": json.dumps({"events": "not a list"}),
        }
        form = BookEditForm(data=form_data, instance=book)
        assert not form.is_valid()
        assert "timeline" in form.errors

        # Valid JSON with events missing required fields
        form_data = {
            "title_and_author": "",
            "date_and_occasion": "",
            "characteristics_and_themes": "",
            "christ_in_book": "",
            "outline": "",
            "timeline": json.dumps({"events": [{"wrong_field": "value"}]}),
        }
        form = BookEditForm(data=form_data, instance=book)
        assert not form.is_valid()
        assert "timeline" in form.errors

        # Valid JSON with properly formatted events
        form_data = {
            "title_and_author": "",
            "date_and_occasion": "",
            "characteristics_and_themes": "",
            "christ_in_book": "",
            "outline": "",
            "timeline": json.dumps(
                {
                    "events": [
                        {"date": "4000 BC", "description": "Creation"},
                        {"date": "2400 BC", "description": "Flood"},
                    ]
                }
            ),
        }
        form = BookEditForm(data=form_data, instance=book)
        assert form.is_valid(), f"Form errors: {form.errors}"

    def test_markdown_sanitization(self):
        """Test that markdown content is sanitized"""
        book = BookFactory()

        # Test with potentially harmful script content
        form_data = {
            "title_and_author": "# Title <script>alert('xss')</script>",
        }

        form = BookEditForm(data=form_data, instance=book)
        assert form.is_valid(), f"Form errors: {form.errors}"

        # The clean method should have sanitized the content by removing the script tag
        # but it doesn't modify the data, just validates it
        assert "<script>" in form.cleaned_data["title_and_author"]

        # When parsed, the script tag should be sanitized
        from milk2meat.core.utils.markdown import parse_markdown

        sanitized = parse_markdown(form.cleaned_data["title_and_author"])
        assert "<script>" not in sanitized
