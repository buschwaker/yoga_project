from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from yoga_app.constants import BASE, DAYS_OF_WEEK, PERSONAL, TRAININGS_TYPE
from yoga_users.constants import COACH, TRAINEE


User = get_user_model()


def validate_range(value):
    if value < 30 or value > 120:
        raise ValidationError(
            f"{value} is out of range. Exercise duration must be between 30 and 120."
        )


class Exercise(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    duration = models.IntegerField(validators=[validate_range])
    image = models.ImageField(
        null=True, blank=True, upload_to="images/exercises/"
    )


# class ExercisesDuration(models.Model):
#     exercise = models.ForeignKey(
#         Exercise, on_delete=models.CASCADE
#     )
#     duration = models.IntegerField(validators=[validate_range])


class Training(models.Model):
    exercises = models.ManyToManyField(
        Exercise, related_name="trainings", related_query_name="training"
    )
    type = models.CharField(
        choices=TRAININGS_TYPE, null=True, max_length=8, default=BASE
    )
    name = models.CharField(max_length=45, unique=True)
    description = models.TextField(max_length=255, null=True, blank=True)
    image = models.ImageField(
        null=True, blank=True, upload_to="images/trainings/"
    )
    request = models.OneToOneField(
        "TrainingRequest", null=True, on_delete=models.SET_NULL
    )

    def clean(self):
        if self.request:
            if self.request.expired:
                raise ValidationError(
                    "Can't processed expired trainee request!"
                )

    def save(self, *args, **kwargs):
        if self.request:
            self.type = PERSONAL
            self.request.accepted = True
            self.request.save()
        super().save(*args, **kwargs)


class TrainingRequest(models.Model):
    trainee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="training_requests",
        related_query_name="training_request",
    )
    duration = models.IntegerField(default=60)
    description = models.TextField(max_length=255, null=True, blank=True)
    accepted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)

    def clean(self):
        if self.trainee.role == COACH:
            raise ValidationError("Coach can't request training!")


class CoachingRequest(models.Model):
    trainee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="coaching_requests_from",
        related_query_name="coaching_request_from",
    )
    coach = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="coaching_requests_to",
        related_query_name="coaching_request_to",
    )
    description = models.TextField(max_length=255, null=True, blank=True)
    accepted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)

    def clean(self):
        if self.coach.role != COACH:
            raise ValidationError("Coach hasn't correct permissions!")

    def save(self, *args, **kwargs):
        if self.accepted:
            self.trainee.role = TRAINEE
            self.trainee.coach = self.coach
            self.trainee.save()
            coaching_requests_from = (
                self.trainee.coaching_requests_from.exclude(id=self.id)
            )
            coaching_requests_from.update(expired=True)
        super().save(*args, **kwargs)


class WorkoutStatistic(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workout_completed_by",
        related_query_name="workout_completed_by",
    )
    training = models.ForeignKey(
        Training,
        on_delete=models.CASCADE,
        related_name="workout_statistic",
        related_query_name="workout_statistic",
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(
        null=True, blank=True
    )  # заполняется в момент окончания трени
    count_exercises = models.IntegerField(default=0)


class ProgramRequest(models.Model):
    trainee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="program_requests_from",
        related_query_name="program_request_from",
    )
    description = models.TextField(max_length=255, null=True, blank=True)
    accepted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.accepted:
            program_requests_from = self.trainee.program_requests_from.exclude(
                id=self.id
            )
            program_requests_from.update(expired=True)
        super().save(*args, **kwargs)


class ProgramItem(models.Model):
    weekday = models.CharField(max_length=9, choices=DAYS_OF_WEEK)
    training = models.ForeignKey(
        Training,
        on_delete=models.CASCADE,
        related_name="consists_of",
        related_query_name="consists_of",
    )
    program_request = models.ForeignKey(
        ProgramRequest,
        on_delete=models.CASCADE,
        related_name="related_to",
        related_query_name="related_to",
    )


class Program(models.Model):
    name = models.CharField(max_length=45)
    program_request = models.OneToOneField(
        ProgramRequest,
        on_delete=models.CASCADE,
    )


# class Article(models.Model):
#     title = models.CharField(max_length=255, unique=True)
#     content = models.TextField()
#     published_date = models.DateField(auto_now_add=True)  # Дата публикации
#     author = models.CharField(max_length=255, blank=True)  # Автор (необязательно)
#     related_exercises = models.ManyToManyField(Exercise, blank=True) # Связь со статьями
#
#     def __str__(self):
#         return self.title
