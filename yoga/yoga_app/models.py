from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser


coach = 'coach'
trainee = 'trainee'

ROLES_CHOICES = [
    (coach, 'Coach'),
    (trainee, 'Trainee'),
]


def validate_range(value):
    if value < 1 or value > 10:
        raise ValidationError(f'{value} is out of range. Exercise duration must be between 1 and 10.')


class User(AbstractUser):
    role = models.CharField(choices=ROLES_CHOICES, null=True, max_length=7)
    coach = models.ForeignKey("self", null=True, on_delete=models.SET_NULL, related_name='trainees', related_query_name='trainee')

    def clean(self):
        if self.role == coach:
            if self.coach:
                raise ValidationError("Coach can't have a coach!")


class Exercise(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=20, null=True)
    duration = models.IntegerField(validators=[validate_range])


class DailyTraining(models.Model):
    day = models.DateField()
    exercises = models.ManyToManyField(Exercise, related_name='trainings', related_query_name='training')
    trainee = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='trainings', related_query_name='training')

    def clean(self):
        if self.trainee.role == coach:
            raise ValidationError("Coach can't do daily training!")
