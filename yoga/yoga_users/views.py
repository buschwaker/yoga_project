from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from yoga_users.forms import CreationForm


class CreateUser(CreateView):
    form_class = CreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("yoga_users:thankyou")


class ThankYouView(TemplateView):
    template_name = "registration/thankyou.html"
