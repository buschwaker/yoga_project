from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from yoga_users.constants import COACH

User = get_user_model()


def validate_range(value):
    if value < 1 or value > 10:
        raise ValidationError(f'{value} is out of range. Exercise duration must be between 1 and 10.')


class Exercise(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=20, null=True, blank=True)
    duration = models.IntegerField(validators=[validate_range])
    image = models.ImageField(null=True, blank=True, upload_to="images/exercises/")


class DailyTraining(models.Model):
    day = models.DateField()
    exercises = models.ManyToManyField(Exercise, related_name='trainings', related_query_name='training')
    trainee = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='trainings', related_query_name='training')

    def clean(self):
        if self.trainee.role == COACH:
            raise ValidationError("Coach can't do daily training!")
