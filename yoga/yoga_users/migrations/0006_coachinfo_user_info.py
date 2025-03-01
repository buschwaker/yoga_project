# Generated by Django 4.2.17 on 2025-01-08 15:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("yoga_users", "0005_alter_user_first_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="CoachInfo",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "education",
                    models.TextField(
                        blank=True, help_text="Education of coach", null=True
                    ),
                ),
                (
                    "work_experience",
                    models.TextField(
                        blank=True,
                        help_text="Work experience as a coach",
                        null=True,
                    ),
                ),
                (
                    "bio",
                    models.TextField(
                        blank=True, help_text="About coach", null=True
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="user",
            name="info",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="yoga_users.coachinfo",
            ),
        ),
    ]
