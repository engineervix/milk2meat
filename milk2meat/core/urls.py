from django.urls import path

from .views import books as book_views
from .views import notes as note_views
from .views import search as search_views
from .views import tags as tags_views

app_name = "core"

urlpatterns = [
    # Books
    path("books/", book_views.BookListView.as_view(), name="book_list"),
    path("books/<int:pk>/", book_views.BookDetailView.as_view(), name="book_detail"),
    path("books/<int:pk>/edit/", book_views.BookUpdateView.as_view(), name="book_edit"),
    # Notes
    path("notes/", note_views.NoteListView.as_view(), name="note_list"),
    path("notes/create/", note_views.NoteCreateView.as_view(), name="note_create"),
    path("notes/<uuid:pk>/", note_views.NoteDetailView.as_view(), name="note_detail"),
    path("notes/<uuid:pk>/edit/", note_views.NoteUpdateView.as_view(), name="note_edit"),
    path("notes/<uuid:pk>/delete/", note_views.note_delete_view, name="note_delete"),
    # Secure file access
    path("notes/<uuid:note_id>/file/", note_views.serve_protected_file, name="serve_protected_file"),
    # AJAX endpoints
    path("api/notes/create/", note_views.note_save_ajax, name="note_create_ajax"),
    path("api/notes/<uuid:pk>/update/", note_views.note_save_ajax, name="note_update_ajax"),
    path("api/note-types/create/", note_views.create_note_type_ajax, name="create_note_type_ajax"),
    # Tags
    path("tags/", tags_views.TagListView.as_view(), name="tag_list"),
    # Search
    path("search/", search_views.GlobalSearchView.as_view(), name="global_search"),
]
