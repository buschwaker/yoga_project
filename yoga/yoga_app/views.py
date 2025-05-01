import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import IntegrityError
from django.db.models import DateField, Q
from django.db.models.functions import Cast
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from yoga_app.constants import BASE
from yoga_app.models import (CoachingRequest, Exercise, Training,
                             TrainingRequest, WorkoutStatistic, Style, ExerciseType, )
from yoga_users.constants import COACH, TRAINEE

from .forms import CustomUserChangeForm, TrainingRequestForm


User = get_user_model()


def role_required(role: str):
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role != role:
                return HttpResponseForbidden(
                    "You do not have permission to view this page"
                )
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
        personal_trainings = Training.objects.filter(
            request__trainee_id=request.user.id
        )
        context.update(
            {"personal_trainings": personal_trainings, TRAINEE: True}
        )
    return render(request, "yoga/main.html", context=context)


@role_required(TRAINEE)
def get_user_info(request):
    return render(
        request,
        "yoga/lk_trainee.html",
        context={"active_tab": "show_lk", TRAINEE: True},
    )


@role_required(COACH)
def get_coach_request_trainee_info(request, trainee_id):
    trainee = get_object_or_404(
        User,
        id=trainee_id
    )
    return render(
        request,
        "yoga/coach/coach_request_from_trainee.html",
        context={COACH: True, 'trainee': trainee},
    )


@role_required(TRAINEE)
def delete_coaching_request(request, request_id):
    request_obj = get_object_or_404(CoachingRequest, id=request_id)
    if request.method == "POST":
        if request_obj.trainee == request.user:
            request_obj.delete()
            messages.success(request, "Запрос успешно удален.")
        else:
            messages.error(
                request, "Ошибка: Вы не можете удалить этот запрос."
            )
        return redirect("yoga:trainee_trainer_choice")
    else:
        return redirect("yoga:trainee_trainer_choice")


@role_required(TRAINEE)
def trainee_choose_coach(request):
    message = ""
    if request.method == "POST":
        coach_id = request.POST.get("coach_id")
        coach = get_object_or_404(User, id=coach_id)
        trainee = request.user
        # Проверяем, существует ли уже запрос с этими trainee и coach
        if CoachingRequest.objects.filter(
            trainee=trainee, coach=coach, expired=False
        ).exists():
            message = "Вы уже отправили запрос тренеру, дождитесь ответа"
        else:
            CoachingRequest.objects.create(trainee=trainee, coach=coach)
            message = "Запрос тренеру отправлен"
    coaches = User.objects.filter(role=COACH)
    paginator = Paginator(coaches, 4)
    page_number = request.GET.get("page")
    coaches_page = paginator.get_page(page_number)

    # Получаем список запросов CoachingRequest текущего trainee
    coaching_requests = CoachingRequest.objects.filter(trainee=request.user)

    return render(
        request,
        "yoga/lk_trainee_choose_coach.html",
        {
            "active_tab": "trainee_trainer_choice",
            "coaches": coaches,
            "coaches_page": coaches_page,
            "coaching_requests": coaching_requests,
            TRAINEE: True,
            "hello": "Hello world",
            "message": message,
        },
    )


@login_required()
def trainee_stats(request, trainee_id):
    trainee = get_object_or_404(User, pk=trainee_id)
    if request.user.role == TRAINEE:
        context = {TRAINEE: True}
    else:
        context = {COACH: True}

    workout_statistics = WorkoutStatistic.objects.filter(
        user=trainee
    ).order_by("-start_time")
    workout_dates = (
        workout_statistics.annotate(date=Cast("start_time", DateField()))
        .values("date")
        .distinct()
    )
    workout_days = [
        workout["date"].strftime("%Y-%m-%d") for workout in workout_dates
    ]

    paginator = Paginator(workout_statistics, 5)
    page_number = request.GET.get("page")
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(
            1
        )  # If page_number is not an integer, deliver first page.
    except EmptyPage:
        page_obj = paginator.page(
            paginator.num_pages
        )  # If page_number is out of range, deliver last page.

    context.update({
        "page_obj": page_obj,
        "workout_statistics": workout_statistics,
        "workout_days": workout_days,
        "trainee": trainee,
    })
    if trainee_id:
        return render(request, "yoga/coach/trainee_statistics.html", context)
    else:
        return render(request, "yoga/lk_trainee_statistics.html", context)


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = CustomUserChangeForm(
            request.POST, request.FILES, instance=request.user
        )
        if form.is_valid():
            form.save()
            if request.user.role == TRAINEE:
                return redirect(reverse("yoga:show_lk"))
            else:
                return redirect(reverse("yoga:coach_lk"))
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, "yoga/edit_profile.html", {"form": form})


@role_required(TRAINEE)
def show_workout(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    total_duration_seconds = sum(
        exercise.duration for exercise in training.exercises.all()
    )
    total_duration_minutes = total_duration_seconds // 60
    remaining_seconds = total_duration_seconds % 60

    context = {
        "training": training,
        "total_duration_minutes": total_duration_minutes,
        "remaining_seconds": remaining_seconds,
        TRAINEE: True,
    }

    return render(request, "yoga/workouts/training.html", context)


@role_required(TRAINEE)
def start_workout(request, training_id):
    training = get_object_or_404(Training, id=training_id)
    request.session["training_name"] = training.name

    # Сохраняем в сессии идентификатор тренировки и список упражнений
    request.session["current_training"] = training.id
    request.session["exercises"] = list(
        training.exercises.values()
    )  # Сохраняем все упражнения
    request.session["current_exercise_index"] = (
        0  # Начинаем с первого упражнения
    )

    user = request.user

    workout_statistic = WorkoutStatistic.objects.create(
        user=user,
        training=training,
    )
    request.session["workout_statistic_id"] = workout_statistic.id
    # Перенаправляем на первое упражнение
    return redirect(
        "yoga:exercise_detail",
        exercise_id=request.session["exercises"][0]["id"],
    )


@role_required(TRAINEE)
def exercise_detail(request, exercise_id):
    # Проверяем наличие текущей тренировки в сессии
    if "current_training" not in request.session:
        return redirect("yoga:show_lk")

    exercises = request.session.get("exercises", [])
    current_index = request.session.get("current_exercise_index", 0)

    # Проверяем, что индекс в пределах допустимого диапазона
    if current_index >= len(exercises):
        return redirect("yoga:show_lk")

    current_exercise_id = exercises[current_index]["id"]

    # Проверяем соответствие exercise_id
    if current_exercise_id != exercise_id:
        return redirect("yoga:show_lk")

    # Определяем следующее упражнение, если оно есть
    next_exercise_id = (
        exercises[current_index + 1]["id"]
        if current_index + 1 < len(exercises)
        else None
    )
    current_exercise = get_object_or_404(Exercise, pk=current_exercise_id)
    next_exercise = None
    if next_exercise_id:
        next_exercise = get_object_or_404(Exercise, pk=next_exercise_id)

    context = {
        "exercise": current_exercise,
        "next_exercise": next_exercise,
    }

    return render(request, "yoga/workouts/exercise_detail.html", context)


@role_required(TRAINEE)
def next_exercise_view(request, next_exercise_id):
    exercises = request.session.get("exercises", [])
    current_index = request.session.get("current_exercise_index", 0)
    # Найдем текущий индекс по переданному идентификатору
    current_exercise = next(
        (ex for ex in exercises if ex["id"] == next_exercise_id), None
    )
    if current_exercise is None:
        return redirect(
            "yoga:show_lk"
        )  # Если упражнение не найдено, перенаправляем

    # Проверяем, есть ли следующее упражнение
    if current_index < len(exercises) - 1:
        current_index += 1
        request.session["current_exercise_index"] = current_index
        # Перенаправляем на следующее упражнение
        return redirect(
            "yoga:exercise_detail", exercise_id=exercises[current_index]["id"]
        )
    else:
        # Если это последнее упражнение, очищаем сессию и перенаправляем на личный кабинет
        del request.session["current_training"]
        del request.session["current_exercise_index"]
        return redirect("yoga:workout_end")


@role_required(TRAINEE)
def workout_end(request):
    workout_statistic_id = request.session.get("workout_statistic_id")
    exercises = request.session.get("exercises", [])
    if workout_statistic_id:
        workout_statistic = WorkoutStatistic.objects.get(
            id=workout_statistic_id
        )

        workout_statistic.end_time = timezone.now()
        workout_statistic.count_exercises = len(exercises)
        workout_statistic.save()

        duration = workout_statistic.end_time - workout_statistic.start_time
        duration_seconds = int(duration.total_seconds())
        duration_minutes = duration_seconds // 60
        remaining_seconds = duration_seconds % 60
        exercise_count = len(exercises)

    training = get_object_or_404(
        Training, id=request.session["current_training"]
    )
    context = {
        "training": training,
        "workout_statistic": workout_statistic,
        "duration_minutes": duration_minutes,
        "remaining_seconds": remaining_seconds,
        "exercise_count": exercise_count,
        TRAINEE: True,
    }
    del request.session["workout_statistic_id"]
    del request.session["exercises"]
    return render(request, "yoga/workouts/workout_stats.html", context)


@role_required(TRAINEE)
def create_training_request(request):
    if not request.user.coach:
        return redirect("yoga:trainee_trainer_choice")

    if request.method == "POST":
        form = TrainingRequestForm(request.POST)
        if form.is_valid():
            training_request = form.save(commit=False)
            training_request.trainee = request.user
            training_request.save()

            messages.success(request, "Ваш запрос успешно отправлен!")
            return redirect("yoga:show_training_requests")
        else:
            print("Ошибки формы:", form.errors)
            messages.error(request, "Пожалуйста, исправьте ошибки в форме")
    else:
        # Инициализация формы с начальными значениями
        initial_data = {
            'duration': 60,  # Значение по умолчанию
            'complexity': 2,  # Средний уровень
        }
        form = TrainingRequestForm(initial=initial_data)

    return render(
        request,
        "trainings/create_training_request.html",
        {
            "form": form,
            "styles": Style.objects.all()
        }
    )


@role_required(TRAINEE)
def show_training_requests(request):
    t_requests = TrainingRequest.objects.filter(trainee=request.user)
    return render(
        request,
        "yoga/lk_trainee_training_request.html",
        context={
            "active_tab": "show_training_requests",
            "training_requests": t_requests,
            TRAINEE: True,
        },
    )


@role_required(COACH)
def get_coach_info(request):
    return render(
        request,
        "yoga/coach/lk_coach.html",
        context={"active_tab": "coach_lk", COACH: True},
    )


@role_required(COACH)
def coach_requests(request):
    coach = request.user
    coaching_requests = CoachingRequest.objects.filter(
        coach=coach
    ).select_related("trainee")
    return render(
        request,
        "yoga/coach/coach_requests.html",
        context={
            "active_tab": "coach_requests",
            "coaching_requests": coaching_requests,
            COACH: True,
        },
    )


@role_required(COACH)
def accept_coaching_request(request, request_id):
    coach = request.user
    coaching_request = get_object_or_404(
        CoachingRequest, id=request_id, coach=coach
    )
    if request.method == "POST":
        coaching_request.accepted = True
        coaching_request.save()
        return redirect("yoga:coach_requests")
    return HttpResponseForbidden()


@role_required(COACH)
def decline_coaching_request(request, request_id):
    coach = request.user
    coaching_request = get_object_or_404(
        CoachingRequest, id=request_id, coach=coach
    )

    if request.method == "POST":
        coaching_request.expired = True
        coaching_request.save()
        return redirect("yoga:coach_requests")
    return HttpResponseForbidden()


@role_required(COACH)
def coach_show_training_requests(request):
    t_requests = TrainingRequest.objects.select_related("trainee").filter(
        trainee__coach=request.user
    )
    return render(
        request,
        "yoga/coach/training_requests.html",
        context={
            "active_tab": "coach_show_training_requests",
            "training_requests": t_requests,
            COACH: True,
        },
    )


@role_required(COACH)
def create_training_by_request(request, request_id):
    exercises = Exercise.objects.all()
    request_obj = get_object_or_404(TrainingRequest, pk=request_id)

    if request.method == "POST":
        selected_exercises = request.POST.getlist("exercises")
        description = request.POST.get("description", "")
        image = request.FILES.get("image")
        try:
            training = Training.objects.create(
                name=f"Тренировка № {request_id}",
                type="PERSONAL",
                request=request_obj,
                description=description,
                image=image,
            )
            selected_exercises_qs = Exercise.objects.filter(
                pk__in=selected_exercises
            )
            training.exercises.add(*selected_exercises_qs)
            return redirect("yoga:coach_lk")
        except IntegrityError:
            return render(
                request,
                "yoga/coach/create_training.html",
                {
                    "exercises": exercises,
                    "request": request_obj,
                    "error": "Training name is not unique!",
                },
            )
        except Exception as e:
            return render(
                request,
                "yoga/coach/create_training.html",
                {
                    "exercises": exercises,
                    "request": request_obj,
                    "error": f"Error: {e}",
                },
            )
    return render(
        request,
        "yoga/coach/create_training.html",
        {"exercises": exercises, "request": request_obj},
    )


def show_articles(request):
    is_coach = request.user.is_authenticated and request.user.role == COACH
    is_trainee = request.user.is_authenticated and request.user.role == TRAINEE

    query = request.GET.get("q")
    complexity = request.GET.get("complexity")
    selected_types = request.GET.getlist("type")  # Получаем список выбранных типов

    exercises = Exercise.objects.all()
    all_types = ExerciseType.objects.all()  # Получаем все возможные типы

    if query:
        exercises = exercises.filter(Q(name__icontains=query))

    if complexity:
        exercises = exercises.filter(complexity=complexity)

    if selected_types:
        # Фильтруем упражнения по выбранным типам
        exercises = exercises.filter(types__id__in=selected_types).distinct()

    context = {
        COACH: is_coach,
        TRAINEE: is_trainee,
        "exercises": exercises,
        "query": query,
        "selected_complexity": complexity,
        "all_types": all_types,
        "selected_types": selected_types,
    }
    return render(request, "articles/all_exercises.html", context)


def articles_exercise_detail(request, exercise_id):
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    return render(request, 'articles/exercise_detail.html', {'exercise': exercise})