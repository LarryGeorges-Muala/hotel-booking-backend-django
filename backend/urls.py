from django.urls import path

from . import views


app_name = "backend"

urlpatterns = [
    # ex: /backend/
    path("health/", views.Health.as_view(), name="health"),
    path("create/", views.CreateBooking.as_view(), name="create_booking"),
    path("session/", views.CreateUserSession.as_view(), name="create_user_session"),
    path("reload/", views.FetchUserSession.as_view(), name="fetch_user_session"),
    path("reset/", views.ClearUserSession.as_view(), name="clear_user_session"),
    path("dashboard/", views.FetchDashboardData.as_view(), name="fetch_dashboard_data"),
    path("users/register/", views.CreateUser.as_view(), name="create_user"),
    path("users/verify/", views.VerifyUser.as_view(), name="verify_user"),
    path("users/login/", views.FetchUser.as_view(), name="fetch_user"),
    path("users/profile/", views.UpdateUser.as_view(), name="update_user"),
]
