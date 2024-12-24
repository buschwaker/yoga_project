# Generated by Django 2.2.19 on 2024-12-02 11:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yoga_app', '0006_auto_20241201_1039'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='training',
            name='trainee',
        ),
        migrations.AlterField(
            model_name='training',
            name='description',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='training',
            name='name',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.CreateModel(
            name='TrainingRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.IntegerField(default=45)),
                ('description', models.TextField(blank=True, max_length=255, null=True)),
                ('accepted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('expired', models.BooleanField(default=False)),
                ('trainee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='training_requests', related_query_name='training_request', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CoachingRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, max_length=255, null=True)),
                ('accepted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('expired', models.BooleanField(default=False)),
                ('coach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coaching_requests_to', related_query_name='coaching_request_to', to=settings.AUTH_USER_MODEL)),
                ('trainee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coaching_requests_from', related_query_name='coaching_request_from', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='training',
            name='request',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='yoga_app.TrainingRequest'),
        ),
    ]