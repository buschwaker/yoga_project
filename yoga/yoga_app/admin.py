from django.contrib import admin
from yoga_app import models

admin.site.register(models.Exercise)

admin.site.register(models.User)

admin.site.register(models.Training)
