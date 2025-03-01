# Generated by Django 2.2.19 on 2024-12-26 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("yoga_users", "0002_alter_user_first_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[("male", "Male"), ("female", "Female")],
                max_length=6,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="height",
            field=models.IntegerField(
                blank=True, help_text="Height in centimeters", null=True
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="weight",
            field=models.IntegerField(
                blank=True, help_text="Weight in kilograms", null=True
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(
                blank=True, max_length=30, verbose_name="first name"
            ),
        ),
    ]
