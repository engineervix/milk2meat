import json

import pytest
from django.urls import reverse

from milk2meat.core.factories import BookFactory, NoteFactory, NoteTypeFactory
from milk2meat.core.models import Note
from milk2meat.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestNoteListView:
    def test_login_required(self, client):
        """Test that login is required to view note list"""
        url = reverse("core:note_list")
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login page

    def test_note_list_view(self, client):
        """Test the note list view displays user's notes"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Create another user (to verify we don't see their notes)
        other_user = UserFactory()

        # Create note type
        note_type = NoteTypeFactory(name="Bible Study")

        # Create notes for both users
        note1 = NoteFactory(title="User's Note 1", owner=user, note_type=note_type)
        note2 = NoteFactory(title="User's Note 2", owner=user, note_type=note_type)
        other_note = NoteFactory(title="Other User's Note", owner=other_user, note_type=note_type)

        # Add tags to one note
        note1.tags.add("salvation", "grace")

        # Get the note list page
        url = reverse("core:note_list")
        response = client.get(url)

        # Check response
        assert response.status_code == 200
        content = response.content.decode()
        assert "User&#x27;s Note 1" in content
        assert "User&#x27;s Note 2" in content
        assert "Other User&#x27;s Note" not in content  # Should not see other user's notes

        # Check context
        assert len(response.context["notes"]) == 2  # Only user's notes
        assert note1 in response.context["notes"]
        assert note2 in response.context["notes"]
        assert other_note not in response.context["notes"]

    def test_note_list_filter_by_type(self, client):
        """Test filtering notes by type"""
        user = UserFactory()
        client.force_login(user)

        # Create note types
        bible_study = NoteTypeFactory(name="Bible Study")
        sermon_notes = NoteTypeFactory(name="Sermon Notes")

        # Create notes with different types
        note1 = NoteFactory(title="Bible Study Note", owner=user, note_type=bible_study)
        note2 = NoteFactory(title="Sermon Note", owner=user, note_type=sermon_notes)

        # Filter by Bible Study type
        url = reverse("core:note_list") + "?type=Bible+Study"
        response = client.get(url)

        # Check filtering
        assert response.status_code == 200
        assert len(response.context["notes"]) == 1
        assert note1 in response.context["notes"]
        assert note2 not in response.context["notes"]

        # Filter by Sermon Notes type
        url = reverse("core:note_list") + "?type=Sermon+Notes"
        response = client.get(url)

        # Check filtering
        assert response.status_code == 200
        assert len(response.context["notes"]) == 1
        assert note2 in response.context["notes"]
        assert note1 not in response.context["notes"]

    def test_note_list_filter_by_book(self, client):
        """Test filtering notes by referenced book"""
        user = UserFactory()
        client.force_login(user)

        # Create note type
        note_type = NoteTypeFactory()

        # Create books
        genesis = BookFactory(title="Genesis")
        exodus = BookFactory(title="Exodus")

        # Create notes referencing different books
        note1 = NoteFactory(title="Genesis Note", owner=user, note_type=note_type)
        note1.referenced_books.add(genesis)

        note2 = NoteFactory(title="Exodus Note", owner=user, note_type=note_type)
        note2.referenced_books.add(exodus)

        # Filter by Genesis
        url = reverse("core:note_list") + f"?book={genesis.id}"
        response = client.get(url)

        # Check filtering
        assert response.status_code == 200
        assert len(response.context["notes"]) == 1
        assert note1 in response.context["notes"]
        assert note2 not in response.context["notes"]

    def test_note_list_filter_by_tag(self, client):
        """Test filtering notes by tag"""
        user = UserFactory()
        client.force_login(user)

        # Create note type
        note_type = NoteTypeFactory()

        # Create notes with different tags
        note1 = NoteFactory(title="Faith Note", owner=user, note_type=note_type)
        note1.tags.add("faith")

        note2 = NoteFactory(title="Grace Note", owner=user, note_type=note_type)
        note2.tags.add("grace")

        # Filter by faith tag
        url = reverse("core:note_list") + "?tag=faith"
        response = client.get(url)

        # Check filtering
        assert response.status_code == 200
        assert len(response.context["notes"]) == 1
        assert note1 in response.context["notes"]
        assert note2 not in response.context["notes"]

    def test_note_list_search(self, client):
        """Test searching notes"""
        user = UserFactory()
        client.force_login(user)

        # Create note type
        note_type = NoteTypeFactory()

        # Create notes with searchable content
        note1 = NoteFactory(
            title="Salvation Study", content="This is about salvation through faith.", owner=user, note_type=note_type
        )

        note2 = NoteFactory(title="Grace Study", content="This is about God's grace.", owner=user, note_type=note_type)

        # Search for "salvation"
        url = reverse("core:note_list") + "?q=salvation"
        response = client.get(url)

        # Check search results
        assert response.status_code == 200
        assert len(response.context["notes"]) == 1
        assert note1 in response.context["notes"]
        assert note2 not in response.context["notes"]
        assert response.context["is_search_active"] is True
        assert response.context["search_query"] == "salvation"
        assert response.context["result_count"] == 1


class TestNoteDetailView:
    def test_login_required(self, client):
        """Test that login is required to view note detail"""
        note = NoteFactory()
        url = reverse("core:note_detail", kwargs={"pk": note.pk})
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login page

    def test_note_detail_view_own_note(self, client):
        """Test viewing own note details"""
        # Create a user and log in
        user = UserFactory()
        client.force_login(user)

        # Create a note type
        note_type = NoteTypeFactory(name="Bible Study")

        # Create a note with references and tags
        book = BookFactory(title="Genesis")
        note = NoteFactory(
            title="Genesis Study", content="# Genesis 1:1\n\nIn the beginning...", owner=user, note_type=note_type
        )
        note.referenced_books.add(book)
        note.tags.add("creation", "genesis")

        # Get the note detail page
        url = reverse("core:note_detail", kwargs={"pk": note.pk})
        response = client.get(url)

        # Check response
        assert response.status_code == 200
        content = response.content.decode()
        assert "Genesis Study" in content
        assert "Genesis 1:1" in content
        assert "In the beginning" in content
        assert "Bible Study" in content  # Note type

        # Check content HTML is generated
        assert "content_html" in response.context
        assert "<h1>Genesis 1:1</h1>" in response.context["content_html"]

    def test_cannot_view_other_users_notes(self, client):
        """Test users cannot view notes owned by others"""
        # Create two users
        user1 = UserFactory()
        user2 = UserFactory()

        # Create a note owned by user2
        note = NoteFactory(owner=user2)

        # Log in as user1
        client.force_login(user1)

        # Try to view user2's note
        url = reverse("core:note_detail", kwargs={"pk": note.pk})
        response = client.get(url)

        # Should return 404 since user1 doesn't own this note
        assert response.status_code == 404


class TestNoteCreatePageView:
    def test_login_required(self, client):
        """Test that login is required to view the note creation page"""
        url = reverse("core:note_create")
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login page

    def test_note_create_page_view_get(self, client):
        """Test getting the note creation page"""
        user = UserFactory()
        client.force_login(user)

        url = reverse("core:note_create")
        response = client.get(url)

        # Check response
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["is_create"] is True
        assert "bible_books" in response.context
        assert "note_types" in response.context

    # Note: POST tests have been moved to test_note_ajax.py since form submission happens via AJAX


class TestNoteEditPageView:
    def test_login_required(self, client):
        """Test that login is required to view the note edit page"""
        note = NoteFactory()
        url = reverse("core:note_edit", kwargs={"pk": note.pk})
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login page

    def test_note_edit_page_view_get(self, client):
        """Test getting the note edit page"""
        user = UserFactory()
        client.force_login(user)

        # Create a note
        note_type = NoteTypeFactory()
        book = BookFactory()
        note = NoteFactory(title="Original Note", content="Original content", owner=user, note_type=note_type)
        note.referenced_books.add(book)
        note.tags.add("original", "tag")

        # Get the note edit page
        url = reverse("core:note_edit", kwargs={"pk": note.pk})
        response = client.get(url)

        # Check response
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["is_create"] is False

        # Check form initial values
        form = response.context["form"]
        assert form.initial["title"] == "Original Note"
        assert form.initial["content"] == "Original content"
        assert json.loads(form.initial["referenced_books_json"]) == [{"id": book.id, "title": book.title}]
        assert form.initial["tags_input"] == "original,tag"

    def test_cannot_edit_other_users_notes(self, client):
        """Test users cannot view edit page for notes owned by others"""
        # Create two users
        user1 = UserFactory()
        user2 = UserFactory()

        # Create a note owned by user2
        note_type = NoteTypeFactory()
        note = NoteFactory(owner=user2, note_type=note_type)

        # Log in as user1
        client.force_login(user1)

        # Try to view edit page for user2's note
        url = reverse("core:note_edit", kwargs={"pk": note.pk})
        response = client.get(url)

        # Should be forbidden since user1 doesn't own this note
        assert response.status_code == 403

    # Note: POST tests have been moved to test_note_ajax.py since form submission happens via AJAX


class TestNoteDeleteView:
    def test_login_required(self, client):
        """Test that login is required to delete note"""
        note = NoteFactory()
        url = reverse("core:note_delete", kwargs={"pk": note.pk})
        response = client.post(url)
        assert response.status_code == 302  # Redirect to login page

    def test_delete_own_note(self, client):
        """Test deleting own note"""
        user = UserFactory()
        client.force_login(user)

        # Create a note
        note = NoteFactory(owner=user)
        note_pk = note.pk

        # Delete the note
        url = reverse("core:note_delete", kwargs={"pk": note.pk})
        response = client.post(url)

        # Should redirect to notes list
        assert response.status_code == 302
        assert response.url == reverse("core:note_list")

        # Verify note is deleted
        assert not Note.objects.filter(pk=note_pk).exists()

    def test_cannot_delete_other_users_notes(self, client):
        """Test users cannot delete notes owned by others"""
        # Create two users
        user1 = UserFactory()
        user2 = UserFactory()

        # Create a note owned by user2
        note = NoteFactory(owner=user2)
        note_pk = note.pk

        # Log in as user1
        client.force_login(user1)

        # Try to delete user2's note
        url = reverse("core:note_delete", kwargs={"pk": note.pk})
        response = client.post(url)

        # Should return 404 since user1 doesn't own this note
        assert response.status_code == 404

        # Verify note wasn't deleted
        assert Note.objects.filter(pk=note_pk).exists()
