import pytest
from django.urls import reverse

from milk2meat.bible.factories import BookFactory
from milk2meat.notes.factories import NoteFactory, NoteTypeFactory
from milk2meat.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestTagListView:
    def test_login_required(self, client):
        """Test that login is required to view tag list"""
        url = reverse("notes:tag_list")
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login page

    def test_tag_list_view(self, client):
        """Test the tag list view displays user's tags"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Create another user (to verify we don't see their tags)
        other_user = UserFactory()

        # Create note type
        note_type = NoteTypeFactory()

        # Create notes with tags for both users
        note1 = NoteFactory(owner=user, note_type=note_type)
        note1.tags.add("faith", "grace", "salvation")

        note2 = NoteFactory(owner=user, note_type=note_type)
        note2.tags.add("gospel", "faith")  # 'faith' appears in two notes

        # Other user's note with different tags
        other_note = NoteFactory(owner=other_user, note_type=note_type)
        other_note.tags.add("other-tag", "private")

        # Get the tag list page
        url = reverse("notes:tag_list")
        response = client.get(url)

        # Check response
        assert response.status_code == 200
        content = response.content.decode()

        # Should show user's tags
        assert "faith" in content
        assert "grace" in content
        assert "salvation" in content
        assert "gospel" in content

        # Should not show other user's tags
        assert "other-tag" not in content
        assert "private" not in content

        # Check context
        tag_names = [tag.name for tag in response.context["tags"]]
        assert set(tag_names) == {"faith", "grace", "salvation", "gospel"}

        # Check tags_by_letter grouping
        assert "tags_by_letter" in response.context

        # Check tags_for_cloud
        assert "tags_for_cloud" in response.context

        # Check tag counts
        for tag in response.context["tags"]:
            if tag.name == "faith":
                assert tag.note_count == 2  # Faith appears in two notes
            else:
                assert tag.note_count == 1


class TestGlobalSearchView:
    def test_login_required(self, client):
        """Test that login is required to search"""
        url = reverse("core:global_search")
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login page

    def test_search_empty_query(self, client):
        """Test search with empty query"""
        user = UserFactory()
        client.force_login(user)

        url = reverse("core:global_search")
        response = client.get(url)

        # Check response
        assert response.status_code == 200
        assert response.context["search_results"] == []
        assert "search_query" in response.context
        assert response.context["search_query"] == ""

    def test_search_results(self, client):
        """Test search with results"""
        user = UserFactory()
        client.force_login(user)

        # Create another user (to verify we don't see their content)
        other_user = UserFactory()

        # Create note type
        note_type = NoteTypeFactory()

        # Create books
        genesis = BookFactory(
            title="Genesis",
            title_and_author="# Genesis\n\nWritten by Moses",
            characteristics_and_themes="Creation, Fall, Redemption",
        )

        # Create notes
        salvation_note = NoteFactory(
            title="Study on Salvation",
            content="This is about salvation through faith in Christ.",
            owner=user,
            note_type=note_type,
        )

        NoteFactory(
            title="Kingdom of God", content="This is about the kingdom of God.", owner=user, note_type=note_type
        )

        # Other user's note
        other_note = NoteFactory(
            title="Private Study on Salvation",
            content="This should not appear in search results.",
            owner=other_user,
            note_type=note_type,
        )

        # Search for "salvation"
        url = reverse("core:global_search") + "?q=salvation"
        response = client.get(url)

        # Check response
        assert response.status_code == 200
        assert response.context["search_query"] == "salvation"

        # Should find our salvation note
        search_results = list(response.context["search_results"])
        assert len(search_results) == 1
        assert search_results[0].object == salvation_note

        # Should not find other user's note
        for result in search_results:
            assert result.object != other_note

        # Search for "genesis"
        url = reverse("core:global_search") + "?q=genesis"
        response = client.get(url)

        # Check response
        assert response.status_code == 200

        # Should find the Genesis book
        search_results = list(response.context["search_results"])
        assert len(search_results) == 1
        assert search_results[0].object == genesis

        # Search for "creation" - should find book with creation in characteristics
        url = reverse("core:global_search") + "?q=creation"
        response = client.get(url)

        # Check we find the Genesis book due to "Creation" in its characteristics
        search_results = list(response.context["search_results"])
        assert len(search_results) == 1
        assert search_results[0].object == genesis

    def test_search_pagination(self, client):
        """Test search pagination"""
        user = UserFactory()
        client.force_login(user)

        # Create note type
        note_type = NoteTypeFactory()

        # Create 25 notes with the same search term (more than the pagination limit of 20)
        for i in range(25):
            NoteFactory(
                title=f"Search Term Note {i}",
                content="This note contains the search term.",
                owner=user,
                note_type=note_type,
            )

        # Search for "search term"
        url = reverse("core:global_search") + "?q=search+term"
        response = client.get(url)

        # Check pagination
        assert response.status_code == 200
        assert response.context["is_paginated"] is True
        assert response.context["page_obj"].number == 1
        assert len(response.context["search_results"]) == 20  # First page has 20 results
        assert response.context["page_obj"].paginator.count == 25  # Total of 25 results

        # Check second page
        url = reverse("core:global_search") + "?q=search+term&page=2"
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["page_obj"].number == 2
        assert len(response.context["search_results"]) == 5  # Second page has 5 results
