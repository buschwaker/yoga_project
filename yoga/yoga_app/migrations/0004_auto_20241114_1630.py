# Generated by Django 2.2.19 on 2024-11-14 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("yoga_app", "0003_exercise_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                blank=True, null=True, upload_to="images/avatars/"
            ),
        ),
        migrations.AlterField(
            model_name="exercise",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to="images/exercises/"
            ),
        ),
    ]
