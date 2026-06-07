from django.urls import path

from . import views


app_name = "backend"

urlpatterns = [
    # ex: /backend/
    path("", views.index, name="index"),
    path("health/", views.health, name="health"),
    path("session/", views.create_user_session, name="create_user_session"),
    path("reload/", views.fetch_user_session, name="fetch_user_session"),
    path("reset/", views.clear_user_session, name="clear_user_session"),
    path("users/register/", views.create_user, name="create_user"),
    path("users/verify/", views.verify_user, name="verify_user"),
]
