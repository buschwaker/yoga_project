# Generated by Django 2.2.19 on 2024-12-26 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yoga_users', '0003_auto_20241226_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Мужской'), ('female', 'Женский')], max_length=7, null=True),
        ),
    ]
