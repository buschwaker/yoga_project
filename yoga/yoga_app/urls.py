from django.urls import path
from yoga_app.views import hello

urlpatterns = [
    path('test/', hello)
]