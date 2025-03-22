from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    # Search
    path("search/", views.GlobalSearchView.as_view(), name="global_search"),
]
