from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from yoga_app.constants import TRAININGS_TYPE, BASE, PERSONAL

from yoga_users.constants import COACH, TRAINEE

User = get_user_model()


def validate_range(value):
    if value < 1 or value > 10:
        raise ValidationError(f'{value} is out of range. Exercise duration must be between 1 and 10.')


class Exercise(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=20, null=True, blank=True)
    duration = models.IntegerField(validators=[validate_range])
    image = models.ImageField(null=True, blank=True, upload_to="images/exercises/")


class Training(models.Model):
    exercises = models.ManyToManyField(Exercise, related_name='trainings', related_query_name='training')
    type = models.CharField(choices=TRAININGS_TYPE, null=True, max_length=8, default=BASE)
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(max_length=255, null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="images/trainings/")
    request = models.OneToOneField('TrainingRequest', null=True, on_delete=models.SET_NULL)

    def clean(self):
        if self.request:
            if self.request.expired:
                raise ValidationError("Can't processed expired trainee request!")

    def save(self, *args, **kwargs):
        if self.request:
            self.type = PERSONAL
            self.request.accepted = True
            self.request.save()
        super().save(*args, **kwargs)


class TrainingRequest(models.Model):
    trainee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_requests',
                                related_query_name='training_request')
    duration = models.IntegerField(default=45)
    description = models.TextField(max_length=255, null=True, blank=True)
    accepted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)

    def clean(self):
        if self.trainee.role == COACH:
            raise ValidationError("Coach can't request training!")


class CoachingRequest(models.Model):
    trainee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coaching_requests_from',
                                related_query_name='coaching_request_from')
    coach = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='coaching_requests_to',
        related_query_name='coaching_request_to'
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
            coaching_requests_from = self.trainee.coaching_requests_from.exclude(id=self.id)
            coaching_requests_from.update(expired=True)
        super().save(*args, **kwargs)
