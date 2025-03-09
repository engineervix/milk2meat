from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    # Books
    path("books/", views.BookListView.as_view(), name="book_list"),
    path("books/<int:pk>/", views.BookDetailView.as_view(), name="book_detail"),
    path("books/<int:pk>/edit/", views.BookUpdateView.as_view(), name="book_edit"),
    # Notes
    path("notes/", views.NoteListView.as_view(), name="note_list"),
    path("notes/create/", views.NoteCreateView.as_view(), name="note_create"),
    path("notes/<uuid:pk>/", views.NoteDetailView.as_view(), name="note_detail"),
    path("notes/<uuid:pk>/edit/", views.NoteUpdateView.as_view(), name="note_edit"),
    path("notes/<uuid:pk>/delete/", views.note_delete_view, name="note_delete"),
    path("tags/", views.TagListView.as_view(), name="tag_list"),
    path("api/note-types/create/", views.create_note_type_ajax, name="create_note_type_ajax"),
    # Search
    path("search/", views.GlobalSearchView.as_view(), name="global_search"),
]
