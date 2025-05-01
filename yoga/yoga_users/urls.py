from django.contrib.auth import views
from django.urls import path

from yoga_users.views import CreateUser, ThankYouView, coach_profile
from .views import CoachesListView

app_name = "yoga_users"

urlpatterns = [
    path("registration/", CreateUser.as_view(), name="signup"),
    path(
        "login/",
        views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "logout/",
        views.LogoutView.as_view(template_name="registration/signup.html"),
        name="logout",
    ),
    path("thankyou/", ThankYouView.as_view(), name="thankyou"),
    path('coaches/', CoachesListView.as_view(), name='coaches_list'),

    path('auth/coaches/<int:coach_id>/', coach_profile, name='coach_profile'),
]
