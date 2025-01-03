import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .forms import CustomUserChangeForm

from yoga_app.constants import BASE
from yoga_users.constants import TRAINEE, COACH
from yoga_app.models import Training, CoachingRequest, Exercise, WorkoutStatistic

User = get_user_model()


def role_required(role: str):
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role != role:
                return HttpResponseForbidden("You do not have permission to view this page")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def index(request):
    base_trainings = Training.objects.filter(type=BASE)
    context = {"base_trainings": base_trainings}
    if not request.user.is_authenticated:
        context = context
    elif request.user.role == COACH:
        trainees = request.user.trainees.all()
        context = {"trainees": trainees, COACH: True}
    elif request.user.role == TRAINEE:
        personal_trainings = Training.objects.filter(request__trainee_id=request.user.id)
        context.update({"personal_trainings": personal_trainings, TRAINEE: True})
    return render(request, 'yoga/main.html', context=context)


@role_required(TRAINEE)
def get_user_info(request):
    return render(request, 'yoga/lk_trainee.html', context={'active_tab': 'show_lk', TRAINEE: True})


@role_required(TRAINEE)
def trainee_choose_coach(request):

    if request.method == "POST":
        coach_id = request.POST.get('coach_id')
        coach = get_object_or_404(User, id=coach_id)
        trainee = request.user
        # Проверяем, существует ли уже запрос с этими trainee и coach
        if CoachingRequest.objects.filter(trainee=trainee, coach=coach, expired=False).exists():
            messages.error = f"Вы уже отправили запрос тренеру {coach.first_name} {coach.last_name}, дождитесь ответа"
        else:
            CoachingRequest.objects.create(trainee=trainee, coach=coach)
            # messages.success(request, f"Запрос тренеру {coach.first_name} {coach.last_name} отправлен")
    coaches = User.objects.filter(role=COACH)
    paginator = Paginator(coaches, 4)
    page_number = request.GET.get('page')
    coaches_page = paginator.get_page(page_number)

    # Получаем список запросов CoachingRequest текущего trainee
    coaching_requests = CoachingRequest.objects.filter(trainee=request.user)

    return render(
        request,
        "yoga/lk_trainee_choose_coach.html",
        {
            'active_tab': 'trainee_trainer_choice',
            'coaches': coaches,
            'coaches_page': coaches_page,
            'coaching_requests': coaching_requests,
            TRAINEE: True,
            'hello': "Hello world"
        }
    )


@role_required(TRAINEE)
def trainee_statistics(request):
    return render(request, 'yoga/lk_trainee_statistics.html', {'active_tab': 'trainee_statistics', TRAINEE: True})


@role_required(TRAINEE)
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('yoga:show_lk'))
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'yoga/edit_profile.html', {'form': form, TRAINEE: True})


@role_required(TRAINEE)
def show_workout(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    total_duration_seconds = sum(exercise.duration for exercise in training.exercises.all())
    total_duration_minutes = total_duration_seconds // 60
    remaining_seconds = total_duration_seconds % 60

    context = {
        'training': training,
        'total_duration_minutes': total_duration_minutes,
        'remaining_seconds': remaining_seconds,
        TRAINEE: True
    }

    return render(request, 'yoga/workouts/training.html', context)


@role_required(TRAINEE)
def start_workout(request, training_id):
    training = get_object_or_404(Training, id=training_id)
    request.session['training_name'] = training.name
    # request.session['start_time'] = timezone.now().isoformat()
    # Сохраняем в сессии идентификатор тренировки и список упражнений
    request.session['current_training'] = training.id
    request.session['exercises'] = list(training.exercises.values())  # Сохраняем все упражнения
    request.session['current_exercise_index'] = 0  # Начинаем с первого упражнения

    # Перенаправляем на первое упражнение
    return redirect('yoga:exercise_detail', exercise_id=request.session['exercises'][0]['id'])


@role_required(TRAINEE)
def exercise_detail(request, exercise_id):
    # Проверяем наличие текущей тренировки в сессии
    if 'current_training' not in request.session:
        return redirect('yoga:show_lk')

    exercises = request.session.get('exercises', [])
    current_index = request.session.get('current_exercise_index', 0)

    # Проверяем, что индекс в пределах допустимого диапазона
    if current_index >= len(exercises):
        return redirect('yoga:show_lk')

    current_exercise = exercises[current_index]

    # Проверяем соответствие exercise_id
    if current_exercise['id'] != exercise_id:
        return redirect('yoga:show_lk')

    # Определяем следующее упражнение, если оно есть
    next_exercise = exercises[current_index + 1] if current_index + 1 < len(exercises) else None

    context = {
        'exercise': current_exercise,
        'next_exercise': next_exercise,
    }

    return render(request, 'yoga/workouts/exercise_detail.html', context)


@role_required(TRAINEE)
def next_exercise_view(request, next_exercise_id):
    exercises = request.session.get('exercises', [])
    current_index = request.session.get('current_exercise_index', 0)
    # Найдем текущий индекс по переданному идентификатору
    current_exercise = next((ex for ex in exercises if ex['id'] == next_exercise_id), None)
    if current_exercise is None:
        return redirect('yoga:show_lk')  # Если упражнение не найдено, перенаправляем

    # Проверяем, есть ли следующее упражнение
    if current_index < len(exercises) - 1:
        current_index += 1
        request.session['current_exercise_index'] = current_index
        # Перенаправляем на следующее упражнение
        return redirect('yoga:exercise_detail', exercise_id=exercises[current_index]['id'])
    else:
        # Если это последнее упражнение, очищаем сессию и перенаправляем на личный кабинет
        del request.session['current_training']
        del request.session['exercises']
        del request.session['current_exercise_index']
        return redirect('yoga:show_lk')


def workout_end(request):
    start_time_str = request.session.get('start_time')
    exercises = request.session.get('exercises', [])
    training_id = request.session.get('current_training')
    user = request.user
    training = get_object_or_404(Training, pk=training_id)

    if not start_time_str or not training_id:
        return redirect('yoga:show_lk')
    start_time = timezone.datetime.fromisoformat(start_time_str)
    end_time = timezone.now()
    duration = end_time - start_time
    duration_seconds = int(duration.total_seconds())
    duration_minutes = duration_seconds // 60
    remaining_seconds = duration_seconds % 60

    WorkoutStatistic.objects.create(
        user=user,
        training=training,
        start_time=start_time,
        end_time=end_time,
        duration_seconds=duration_seconds,
        exercise_count=len(exercises),
    )

    request.session.pop('start_time', None)
    request.session.pop('exercises', None)
    request.session.pop('current_training', None)
    request.session.pop('current_exercise_index', None)

    context = {
        'start_time': start_time,
        'end_time': end_time,
        'duration_minutes': duration_minutes,
        'remaining_seconds': remaining_seconds,
        'exercise_count': len(exercises),
        'training_name': request.session.get('training_name', "Unknown training"),
        TRAINEE: True
    }
    return render(request, 'yoga/workouts/workout_stats.html', context)



def get_coach_info(request):
    return render(request, 'yoga/articles.html')


def show_coach_workouts(request):
    return render(request, 'yoga/coach_workouts.html')


def coach_requests(request):
    return render(request, 'yoga/coach_requests.html')


def show_articles(request):
    return render(request, 'yoga/articles.html')