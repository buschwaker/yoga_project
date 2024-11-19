from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser

from yoga_users.constants import ROLES_CHOICES, COACH


class User(AbstractUser):
    role = models.CharField(choices=ROLES_CHOICES, null=True, max_length=7)
    coach = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name='trainees', related_query_name='trainee')
    avatar = models.ImageField(null=True, blank=True, upload_to="images/avatars/")

    def clean(self):
        if self.role == COACH:
            if self.coach:
                raise ValidationError("Coach can't have a coach!")
