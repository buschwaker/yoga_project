from django.urls import path
from yoga_app.views import index

urlpatterns = [
    path('', index)
]