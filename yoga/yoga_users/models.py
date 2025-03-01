from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from yoga_users.constants import COACH, GENDER_CHOICES, ROLES_CHOICES


class CoachInfo(models.Model):
    education = models.TextField(
        null=True, blank=True, help_text="Education of coach"
    )
    work_experience = models.TextField(
        null=True, blank=True, help_text="Work experience as a coach"
    )
    bio = models.TextField(null=True, blank=True, help_text="About coach")


class User(AbstractUser):
    role = models.CharField(choices=ROLES_CHOICES, null=True, max_length=7)
    coach = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="trainees",
        related_query_name="trainee",
    )
    avatar = models.ImageField(
        null=True, blank=True, upload_to="images/avatars/"
    )
    height = models.IntegerField(
        null=True, blank=True, help_text="Height in centimeters"
    )
    weight = models.IntegerField(
        null=True, blank=True, help_text="Weight in kilograms"
    )
    gender = models.CharField(
        choices=GENDER_CHOICES, max_length=7, null=True, blank=True
    )
    info = models.OneToOneField(
        CoachInfo, null=True, blank=True, on_delete=models.SET_NULL
    )

    def clean(self):
        if self.role == COACH:
            if self.coach:
                raise ValidationError("Coach can't have a coach!")
