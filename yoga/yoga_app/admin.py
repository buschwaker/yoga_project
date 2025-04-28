from django.contrib import admin

from yoga_app import models


admin.site.register(models.Exercise)

admin.site.register(models.User)

admin.site.register(models.Training)

admin.site.register(models.TrainingRequest)

admin.site.register(models.CoachingRequest)

admin.site.register(models.WorkoutStatistic)

admin.site.register(models.ProgramRequest)

admin.site.register(models.ProgramItem)

admin.site.register(models.Program)

admin.site.register(models.Style)

admin.site.register(models.ExerciseType)
