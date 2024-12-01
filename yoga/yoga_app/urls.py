from django.urls import path
from yoga_app.views import get_trainings, index

app_name = 'yoga'

urlpatterns = [
    path('', index, name='main'),
    path('trainings/', get_trainings, name='trainings')
]