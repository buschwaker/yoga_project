# Generated by Django 4.2.17 on 2025-01-05 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("yoga_app", "0009_alter_exercise_description_alter_exercise_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="workoutstatistic",
            name="end_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
