from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

from yoga_app.views import index, get_user_info, trainee_statistics, \
    edit_profile, show_articles, get_coach_info, show_coach_workouts, coach_requests, trainee_choose_coach, \
    show_workout, start_workout, exercise_detail, next_exercise_view, workout_end

app_name = 'yoga'

urlpatterns = [
    path('', index, name='main'),
    path('lk_trainee/', get_user_info, name='show_lk'),
    path('lk_trainee/choose_coach', trainee_choose_coach, name='trainee_trainer_choice'),
    path('lk_trainee/stats/', trainee_statistics, name='trainee_statistics'),
    path('edit_profile/', edit_profile, name='edit_profile'),

    path('coach_lk/', get_coach_info, name='coach_lk'),
    path('coach_lk/workouts/', show_coach_workouts, name='coach_workouts'),
    path('coach_lk/requests/', coach_requests, name='coach_requests'),

    path('training/<int:training_id>/', show_workout, name='show_workout'),
    path('training/<int:training_id>/start/', start_workout, name='start_workout'),
    path('exercise/<int:exercise_id>/', exercise_detail, name='exercise_detail'),
    path('exercise/next/<int:next_exercise_id>/', next_exercise_view, name='next_exercise'),
    path('training/workout_stats/', workout_end, name='workout_end'),

    path('articles/', show_articles, name='articles'),
]

if settings.DEBUG:
       urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)