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
    #
    # # Смена пароля
    # path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    #
    # # Сообщение об успешном изменении пароля
    # path('password_change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    #
    # # Восстановление пароля
    # path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    #
    # # Сообщение об отправке ссылки для восстановления пароля
    # path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    #
    # # Вход по ссылке для восстановления пароля
    # path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    #
    # # Сообщение об успешном восстановлении пароля
    # path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
