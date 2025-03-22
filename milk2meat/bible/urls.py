from django.urls import path

import milk2meat.bible.views as book_views

app_name = "bible"

urlpatterns = [
    # Books
    path("books/", book_views.BookListView.as_view(), name="book_list"),
    path("books/<int:pk>/", book_views.BookDetailView.as_view(), name="book_detail"),
    path("books/<int:pk>/edit/", book_views.BookEditPageView.as_view(), name="book_edit"),
    path("api/books/<int:pk>/update/", book_views.book_save_ajax, name="book_update_ajax"),
]
