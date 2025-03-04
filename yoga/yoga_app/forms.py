from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm

from yoga_app.models import TrainingRequest


User = get_user_model()


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "height",
            "weight",
            "gender",
            "avatar",
        ]
        widgets = {
            "avatar": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
        }


class TrainingRequestForm(forms.ModelForm):
    class Meta:
        model = TrainingRequest
        fields = ["duration", "description"]
