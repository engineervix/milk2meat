import json

import pytest
from django.urls import reverse

from milk2meat.bible.factories import BookFactory
from milk2meat.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestBookSaveAjax:
    def test_login_required(self, client):
        """Test that login is required for AJAX book update"""
        book = BookFactory()
        url = reverse("bible:book_update_ajax", kwargs={"pk": book.pk})
        response = client.post(url, {}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        assert response.status_code == 302  # Redirect to login page

    def test_ajax_update_book_valid(self, client):
        """Test updating a book with valid data via AJAX"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Create a book
        book = BookFactory(title="Genesis")
        original_title_and_author = book.title_and_author

        # Prepare update data
        timeline_data = {"events": [{"date": "4000 BC", "description": "Creation"}]}

        post_data = {
            "title_and_author": "# Genesis\n\nWritten by Moses",
            "date_and_occasion": "Around 1400 BC",
            "characteristics_and_themes": "Creation, Fall, Redemption",
            "christ_in_book": "Promised seed in Genesis 3:15",
            "outline": "1. Creation\n2. Fall",
            "timeline": json.dumps(timeline_data),
        }

        # Submit the form via AJAX
        url = reverse("bible:book_update_ajax", kwargs={"pk": book.pk})
        response = client.post(url, post_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        # Check response
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["success"] is True
        assert data["book"]["id"] == book.pk
        assert data["book"]["title"] == book.title
        assert data["message"] == f"{book.title} saved successfully."

        # Check that the book was updated
        book.refresh_from_db()
        assert book.title_and_author == "# Genesis\n\nWritten by Moses"
        assert book.date_and_occasion == "Around 1400 BC"
        assert book.timeline == timeline_data
        assert book.title_and_author != original_title_and_author

    def test_ajax_update_book_invalid(self, client):
        """Test updating a book with invalid data via AJAX"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Create a book
        book = BookFactory(title="Genesis")
        original_timeline = book.timeline

        # Prepare invalid data (invalid timeline JSON)
        post_data = {
            "title_and_author": "# Genesis\n\nWritten by Moses",
            "timeline": "not valid json",  # Invalid JSON
        }

        # Submit the form via AJAX
        url = reverse("bible:book_update_ajax", kwargs={"pk": book.pk})
        response = client.post(url, post_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        # Check response (should be validation error)
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data["success"] is False
        assert "errors" in data
        assert "timeline" in data["errors"]

        # Check that the book was not updated
        book.refresh_from_db()
        assert book.timeline == original_timeline

    def test_ajax_update_nonexistent_book(self, client):
        """Test updating a non-existent book via AJAX"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Use a non-existent book ID
        url = reverse("bible:book_update_ajax", kwargs={"pk": 9999})
        response = client.post(url, {}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        # Check response (should be not found)
        assert response.status_code == 404
        data = json.loads(response.content)
        assert data["success"] is False
        assert "error" in data
        assert data["error"] == "Book not found"
