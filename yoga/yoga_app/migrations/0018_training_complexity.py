# Generated by Django 4.2.17 on 2025-04-13 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("yoga_app", "0017_exercise_complexity"),
    ]

    operations = [
        migrations.AddField(
            model_name="training",
            name="complexity",
            field=models.SmallIntegerField(
                blank=True, choices=[("Easy", 1), ("Medium", 2), ("Hard", 3)], null=True
            ),
        ),
    ]
