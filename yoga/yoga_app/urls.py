from django.urls import path
from yoga_app.views import index, signup

urlpatterns = [
    path('', index),
    path('signup/', signup)
]