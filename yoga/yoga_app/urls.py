from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from yoga_app.views import (accept_coaching_request, coach_requests,
                            coach_show_training_requests,
                            create_training_by_request,
                            create_training_request, decline_coaching_request,
                            edit_profile, exercise_detail, get_coach_info,
                            get_user_info, index, next_exercise_view,
                            show_articles, show_training_requests,
                            show_workout, start_workout, trainee_choose_coach,
                            trainee_stats, workout_end, articles_exercise_detail,
                            get_coach_request_trainee_info, )

from . import views


app_name = "yoga"

urlpatterns = [
    path("", index, name="main"),
    path("lk_trainee/", get_user_info, name="show_lk"),
    path(
        "lk_trainee/choose_coach",
        trainee_choose_coach,
        name="trainee_trainer_choice",
    ),
    path(
        "lk_trainee/delete_request/<int:request_id>/",
        views.delete_coaching_request,
        name="delete_coaching_request",
    ),
    path("lk_trainee/stats/<int:trainee_id>/", trainee_stats, name="trainee_statistics"),
    path("edit_profile/", edit_profile, name="edit_profile"),
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="yoga/password_change_form.html"
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="yoga/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path("coach_lk/", get_coach_info, name="coach_lk"),
    path(
        "coach_lk/workouts/",
        coach_show_training_requests,
        name="coach_show_training_requests",
    ),
    path("coach_lk/requests/", coach_requests, name="coach_requests"),
    path('coach_lk/requests/trainee/<int:trainee_id>/', get_coach_request_trainee_info, name='get_coach_request_trainee_info'),
    path(
        "coach_requests/accept/<int:request_id>/",
        accept_coaching_request,
        name="accept_coaching_request",
    ),
    path(
        "coach_requests/decline/<int:request_id>/",
        decline_coaching_request,
        name="decline_coaching_request",
    ),
    path(
        "coach/create_training/<int:request_id>/",
        create_training_by_request,
        name="create_training_by_request",
    ),
    path(
        "coach/trainee_stats/<int:trainee_id>/",
        trainee_stats,
        name="trainee_stats",
    ),
    path("training/<int:training_id>/", show_workout, name="show_workout"),
    path(
        "training/<int:training_id>/start/",
        start_workout,
        name="start_workout",
    ),
    path(
        "exercise/<int:exercise_id>/", exercise_detail, name="exercise_detail"
    ),
    path(
        "exercise/next/<int:next_exercise_id>/",
        next_exercise_view,
        name="next_exercise",
    ),
    path("training/workout_stats/", workout_end, name="workout_end"),
    path(
        "trainee/training_request/",
        create_training_request,
        name="training_request",
    ),
    path(
        "trainee/show_training_request/",
        show_training_requests,
        name="show_training_requests",
    ),
    path("articles/", show_articles, name="articles"),

    path('articles/<int:exercise_id>/', articles_exercise_detail, name='articles_exercise_detail'),

    path('training-request/create/', views.create_training_request, name='training_request'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
