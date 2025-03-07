from django.urls import path

from . import views

app_name = "auth"

urlpatterns = [
    path("login/", views.TurnstileLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
]
