from django.core.exceptions import ValidationError
from django.db import models

from yoga_app.constants import TRAININGS_TYPE, BASE

from yoga_users.constants import COACH
from yoga_users.models import User


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
    trainee = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='trainings', related_query_name='training')
    type = models.CharField(choices=TRAININGS_TYPE, null=True, max_length=8, default=BASE)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=20, null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="images/trainings/")

    def clean(self):
        if self.trainee.role == COACH:
            raise ValidationError("Coach can't do training!")
