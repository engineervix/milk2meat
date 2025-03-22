from django.urls import path

from .views import notes as note_views
from .views import tags as tags_views

app_name = "notes"

urlpatterns = [
    # Notes
    path("notes/", note_views.NoteListView.as_view(), name="note_list"),
    path("notes/create/", note_views.NoteCreatePageView.as_view(), name="note_create"),
    path("notes/<uuid:pk>/", note_views.NoteDetailView.as_view(), name="note_detail"),
    path("notes/<uuid:pk>/edit/", note_views.NoteEditPageView.as_view(), name="note_edit"),
    path("notes/<uuid:pk>/delete/", note_views.note_delete_view, name="note_delete"),
    # Secure file access
    path("notes/<uuid:note_id>/file/", note_views.serve_protected_file, name="serve_protected_file"),
    # AJAX endpoints
    path("api/notes/create/", note_views.note_save_ajax, name="note_create_ajax"),
    path("api/notes/<uuid:pk>/update/", note_views.note_save_ajax, name="note_update_ajax"),
    path("api/note-types/create/", note_views.create_note_type_ajax, name="create_note_type_ajax"),
    # Tags
    path("tags/", tags_views.TagListView.as_view(), name="tag_list"),
]
