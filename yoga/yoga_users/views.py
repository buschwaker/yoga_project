from django.shortcuts import render
from django.views.generic import CreateView

from yoga_users.forms import CreationForm


class CreateUser(CreateView):
    form_class = CreationForm
    template_name = 'yoga/signup.html'
    success_url = '/thankyou/'
