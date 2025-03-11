import json

import pytest
from django.urls import reverse

from milk2meat.core.factories import BookFactory
from milk2meat.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestBookListView:
    def test_login_required(self, client):
        """Test that login is required to view book list"""
        url = reverse("core:book_list")
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login page

    def test_book_list_view(self, client):
        """Test the book list view displays books correctly"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Create some books
        BookFactory(title="Genesis", testament="OT", number=1)
        BookFactory(title="Exodus", testament="OT", number=2)
        BookFactory(title="Matthew", testament="NT", number=40)

        # Get the book list page
        url = reverse("core:book_list")
        response = client.get(url)

        # Check response
        assert response.status_code == 200
        assert "Genesis" in response.content.decode()
        assert "Exodus" in response.content.decode()
        assert "Matthew" in response.content.decode()

        # Check context
        assert "old_testament" in response.context
        assert "new_testament" in response.context
        assert len(response.context["old_testament"]) == 2  # 2 OT books
        assert len(response.context["new_testament"]) == 1  # 1 NT book


class TestBookDetailView:
    def test_login_required(self, client):
        """Test that login is required to view book detail"""
        book = BookFactory()
        url = reverse("core:book_detail", kwargs={"pk": book.pk})
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login page

    def test_book_detail_view(self, client):
        """Test the book detail view displays book correctly"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Create a book with some data
        book = BookFactory(
            title="Genesis",
            testament="OT",
            number=1,
            chapters=50,
            title_and_author="# Genesis\n\nWritten by Moses",
            date_and_occasion="Around 1400 BC",
            christ_in_book="Promised seed in Genesis 3:15",
            outline="1. Creation\n2. Fall",
            timeline={"events": [{"date": "4000 BC", "description": "Creation"}]},
        )

        # Get the book detail page
        url = reverse("core:book_detail", kwargs={"pk": book.pk})
        response = client.get(url)

        # Check response
        assert response.status_code == 200
        assert "Genesis" in response.content.decode()

        # Check context
        assert response.context["book"] == book
        assert "title_and_author_html" in response.context
        assert "date_and_occasion_html" in response.context
        assert "christ_in_book_html" in response.context
        assert "outline_html" in response.context
        assert "timeline_data" in response.context
        assert len(response.context["timeline_data"]) == 1


class TestBookUpdateView:
    def test_login_required(self, client):
        """Test that login is required to update book"""
        book = BookFactory()
        url = reverse("core:book_edit", kwargs={"pk": book.pk})
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login page

    def test_book_update_view_get(self, client):
        """Test getting the book update form"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Create a book
        book = BookFactory(title="Genesis", timeline={"events": [{"date": "4000 BC", "description": "Creation"}]})

        # Get the book edit page
        url = reverse("core:book_edit", kwargs={"pk": book.pk})
        response = client.get(url)

        # Check response
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["timeline_json"] == json.dumps(book.timeline)

    def test_book_update_view_post(self, client):
        """Test updating a book"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Create a book
        book = BookFactory(title="Genesis")

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

        # Submit the form
        url = reverse("core:book_edit", kwargs={"pk": book.pk})
        response = client.post(url, post_data)

        # Should redirect to book detail view
        assert response.status_code == 302
        assert response.url == reverse("core:book_detail", kwargs={"pk": book.pk})

        # Check that the book was updated
        book.refresh_from_db()
        assert book.title_and_author == "# Genesis\n\nWritten by Moses"
        assert book.date_and_occasion == "Around 1400 BC"
        assert book.timeline == timeline_data

    def test_book_update_invalid_timeline(self, client):
        """Test submitting invalid timeline data"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Create a book
        book = BookFactory(title="Genesis")
        original_timeline = book.timeline

        # Prepare invalid update data
        post_data = {
            "title_and_author": "# Genesis\n\nWritten by Moses",
            "timeline": "not valid json",  # Invalid JSON
        }

        # Submit the form
        url = reverse("core:book_edit", kwargs={"pk": book.pk})
        response = client.post(url, post_data)

        # Should not redirect - form is invalid
        assert response.status_code == 200
        assert "form" in response.context
        assert "timeline" in response.context["form"].errors

        # Check that the book was not updated
        book.refresh_from_db()
        assert book.timeline == original_timeline
