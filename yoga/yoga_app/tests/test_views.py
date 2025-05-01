from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages

from yoga_app.models import (
    CoachingRequest, TrainingRequest, Training,
    Exercise, WorkoutStatistic, Style, ExerciseType
)
from yoga_users.constants import COACH, TRAINEE

User = get_user_model()


class YogaViewsContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.coach = User.objects.create_user(
            username='coach', role=COACH, password='testpass123'
        )
        cls.trainee = User.objects.create_user(
            username='trainee', coach=cls.coach, role=TRAINEE, password='testpass123'
        )

        cls.style = Style.objects.create(name="Test Style")
        cls.exercise_type = ExerciseType.objects.create(name="Test Type")
        cls.exercise = Exercise.objects.create(
            name="Test Exercise", duration=60, complexity=1
        )
        cls.exercise.types.add(cls.exercise_type)

        cls.training_request = TrainingRequest.objects.create(
            trainee=cls.trainee, style=cls.style
        )

        cls.training = Training.objects.create(
            name="Test Training", type="PERSONAL", request=cls.training_request
        )
        cls.training.exercises.add(cls.exercise)

        cls.coaching_request = CoachingRequest.objects.create(
            trainee=cls.trainee, coach=cls.coach
        )

        cls.workout_stat = WorkoutStatistic.objects.create(
            user=cls.trainee, training=cls.training
        )

    def setUp(self):
        self.guest_client = Client()
        self.trainee_client = Client()
        self.coach_client = Client()
        self.trainee_client.login(username='trainee', password='testpass123')
        self.coach_client.login(username='coach', password='testpass123')

    def test_main_page_context(self):
        response = self.guest_client.get(reverse('yoga:main'))
        self.assertIn('base_trainings', response.context)

        # Для трейни
        response = self.trainee_client.get(reverse('yoga:main'))
        self.assertIn('personal_trainings', response.context)
        self.assertTrue(response.context[TRAINEE])

        # Для коуча
        response = self.coach_client.get(reverse('yoga:main'))
        self.assertIn('trainees', response.context)
        self.assertTrue(response.context[COACH])

    def test_trainee_lk_context(self):
        """Проверка контекста ЛК трейни"""
        response = self.trainee_client.get(reverse('yoga:show_lk'))
        self.assertEqual(response.context['active_tab'], 'show_lk')
        self.assertTrue(response.context[TRAINEE])

    def test_trainee_choose_coach_context(self):
        """Проверка контекста страницы выбора тренера"""
        response = self.trainee_client.get(reverse('yoga:trainee_trainer_choice'))
        self.assertEqual(len(response.context['coaches']), 1)
        self.assertEqual(response.context['coaches'][0], self.coach)
        self.assertEqual(len(response.context['coaching_requests']), 1)

    def test_trainee_statistics_context(self):
        """Проверка контекста статистики трейни"""
        response = self.trainee_client.get(reverse('yoga:trainee_statistics'))
        self.assertEqual(len(response.context['workout_statistics']), 1)
        self.assertEqual(response.context['workout_days'][0],
                         self.workout_stat.start_time.strftime('%Y-%m-%d'))

    def test_coach_requests_context(self):
        """Проверка контекста запросов коуча"""
        response = self.coach_client.get(reverse('yoga:coach_requests'))
        self.assertEqual(len(response.context['coaching_requests']), 1)
        self.assertEqual(response.context['coaching_requests'][0], self.coaching_request)

    def test_articles_context(self):
        """Проверка контекста страницы статей"""
        response = self.guest_client.get(reverse('yoga:articles'))
        self.assertEqual(len(response.context['exercises']), 1)
        self.assertEqual(len(response.context['all_types']), 1)

    def test_create_training_request_form(self):
        """Проверка формы создания запроса на тренировку"""
        response = self.trainee_client.get(reverse('yoga:training_request'))
        form_fields = {
            'description': forms.fields.CharField,
            'duration': forms.fields.IntegerField,
            'complexity': forms.fields.ChoiceField,
            'style': forms.models.ModelChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                self.assertIsInstance(
                    response.context['form'].fields[field], expected
                )

    def test_accept_coaching_request_redirect(self):
        """Проверка редиректа после принятия запроса"""
        response = self.coach_client.post(
            reverse('yoga:accept_coaching_request',
                    kwargs={'request_id': self.coaching_request.id})
        )
        self.assertRedirects(response, reverse('yoga:coach_requests'))
        self.coaching_request.refresh_from_db()
        self.assertTrue(self.coaching_request.accepted)

    def test_delete_coaching_request_redirect(self):
        """Проверка редиректа и сообщения после удаления запроса"""
        response = self.trainee_client.post(
            reverse('yoga:delete_coaching_request',
                    kwargs={'request_id': self.coaching_request.id})
        )
        self.assertRedirects(response, reverse('yoga:trainee_trainer_choice'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Запрос успешно удален.")

    def test_trainee_stats_context_for_coach(self):
        """Проверка контекста статистики трейни для коуча"""
        response = self.coach_client.get(
            reverse('yoga:trainee_stats', kwargs={'trainee_id': self.trainee.id})
        )
        self.assertEqual(response.context['trainee'], self.trainee)
        self.assertTrue(response.context[COACH])

    def test_create_training_by_request_post(self):
        """Проверка создания тренировки по запросу"""
        new_request = TrainingRequest.objects.create(
            trainee=self.trainee,
            style=self.style,
            description="New request for test"
        )
        data = {
            'exercises': [self.exercise.id],
            'description': 'New training'
        }
        response = self.coach_client.post(
            reverse('yoga:create_training_by_request',
                    kwargs={'request_id': new_request.id}),
            data
        )
        self.assertRedirects(response, reverse('yoga:coach_lk'))
        self.assertTrue(Training.objects.filter(description='New training').exists())

    def test_articles_filter_context(self):
        """Проверка фильтрации на странице статей"""
        response = self.guest_client.get(
            reverse('yoga:articles') + '?q=Test&complexity=1&type=' + str(self.exercise_type.id)
        )
        self.assertEqual(len(response.context['exercises']), 1)
        self.assertEqual(response.context['query'], 'Test')
        self.assertEqual(response.context['selected_complexity'], '1')