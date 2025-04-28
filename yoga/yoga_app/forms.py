from colorama import Style
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm

from yoga_app.constants import EXERCISE_COMPLEXITY
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
    complexity = forms.ChoiceField(
        choices=EXERCISE_COMPLEXITY,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Уровень сложности"
    )

    class Meta:
        model = TrainingRequest
        fields = ['duration', 'complexity', 'style', 'description']
        widgets = {
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 30,
                'max': 240
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
        }

#
# class TrainingRequestForm(forms.ModelForm):
#     class Meta:
#         model = TrainingRequest
#         fields = ['duration', 'description']
#         widgets = {
#             'duration': forms.NumberInput(attrs={
#                 'min': 30,
#                 'max': 240,
#                 'step': 15,
#                 'class': 'form-control'
#             }),
#             'description': forms.Textarea(attrs={
#                 'rows': 5,
#                 'class': 'form-control',
#                 'placeholder': 'Опишите ваши цели и пожелания...'
#             }),
#             'complexity': forms.Select(attrs={'class': 'form-select'}),
#             'style': forms.Select(attrs={'class': 'form-select'}),
#         }

