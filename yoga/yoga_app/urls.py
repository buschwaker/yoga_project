from django.urls import path
from yoga_app.views import index

app_name = 'yoga'

urlpatterns = [
    path('', index, name='main')
]