import pytest
from django.urls import reverse

from milk2meat.core.factories import NoteFactory, NoteTypeFactory
from milk2meat.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestHomeView:
    def test_home_view_anonymous(self, client):
        """Test that anonymous users can access the home page"""
        url = reverse("home")
        response = client.get(url)

        # Check response
        assert response.status_code == 200

        # Home page should have login link for anonymous users
        content = response.content.decode()
        assert "Login" in content
        assert reverse("auth:login") in content

        # Should not have dashboard link for anonymous users
        assert "Dashboard" not in content

    def test_home_view_authenticated(self, client):
        """Test that authenticated users see dashboard link"""
        # Create and log in user
        user = UserFactory()
        client.force_login(user)

        url = reverse("home")
        response = client.get(url)

        # Check response
        assert response.status_code == 200

        # Home page should have dashboard link for authenticated users
        content = response.content.decode()
        assert "Dashboard" in content
        assert reverse("dashboard") in content

        # Should not have login link for authenticated users
        assert "Login" not in content


class TestDashboardView:
    def test_login_required(self, client):
        """Test that login is required to access dashboard"""
        url = reverse("dashboard")
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login page

    def test_dashboard_view(self, client):
        """Test the dashboard view"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Create some notes
        note_type = NoteTypeFactory()
        for i in range(6):  # Create 6 notes, but dashboard should show only 5
            NoteFactory(title=f"Test Note {i}", owner=user, note_type=note_type)

        # Get the dashboard page
        url = reverse("dashboard")
        response = client.get(url)

        # Check response
        assert response.status_code == 200
        content = response.content.decode()

        # Check user's name in welcome message
        assert user.first_name in content

        # Check recent notes section
        assert "Recent Notes" in content

        # Check context
        assert "recent_notes" in response.context
        assert len(response.context["recent_notes"]) == 5  # Should show 5 most recent notes

        # Check quick actions
        assert "Quick Actions" in content
        assert reverse("core:book_list") in content
        assert reverse("core:note_list") in content
        assert reverse("core:note_create") in content
        assert reverse("core:tag_list") in content

    def test_dashboard_no_notes(self, client):
        """Test the dashboard view when user has no notes"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Get the dashboard page
        url = reverse("dashboard")
        response = client.get(url)

        # Check response
        assert response.status_code == 200
        content = response.content.decode()

        # Check "no notes" message
        assert "You don't have any notes yet." in content

        # Check create note button
        assert "Create Note" in content
        assert reverse("core:note_create") in content
