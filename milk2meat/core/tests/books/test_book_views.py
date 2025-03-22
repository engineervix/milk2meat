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


class TestBookEditPageView:
    def test_login_required(self, client):
        """Test that login is required to view the book edit page"""
        book = BookFactory()
        url = reverse("core:book_edit", kwargs={"pk": book.pk})
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login page

    def test_book_edit_page_view_get(self, client):
        """Test getting the book edit page"""
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
        assert response.context["book_update_url"] == reverse("core:book_update_ajax", kwargs={"pk": book.pk})
        assert response.context["current_book_id"] == book.pk

    # Note: POST tests have been moved to test_book_ajax.py since form submission happens via AJAX
