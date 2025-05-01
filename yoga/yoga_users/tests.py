from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from yoga_users.models import User

User = get_user_model()


class UserViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.coach = User.objects.create_user(
            username='coach1',
            email='coach1@example.com',
            password='testpass123',
            role='coach'
        )
        cls.trainee = User.objects.create_user(
            username='trainee1',
            email='trainee1@example.com',
            coach=cls.coach,
            password='testpass123',
            role='trainee'
        )
        for i in range(2, 8):
            User.objects.create_user(
                username=f'coach{i}',
                email=f'coach{i}@example.com',
                password='testpass123',
                role='coach'
            )

    def setUp(self):
        self.guest_client = Client()
        self.coach_client = Client()
        self.trainee_client = Client()
        self.coach_client.login(username='coach1', password='testpass123')
        self.trainee_client.login(username='trainee1', password='testpass123')
        self.ok = HTTPStatus.OK.value
        self.found = HTTPStatus.FOUND.value

    def test_create_user_view(self):
        """Проверка регистрации нового пользователя"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'role': 'trainee'
        }
        response = self.guest_client.post(
            reverse('yoga_users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, self.ok)
        self.assertTrue(
            User.objects.filter(username='newuser').exists()
        )
        self.assertRedirects(
            response,
            reverse('yoga_users:thankyou')
        )

    def test_thankyou_view(self):
        """Проверка страницы благодарности"""
        response = self.guest_client.get(
            reverse('yoga_users:thankyou')
        )
        self.assertEqual(response.status_code, self.ok)

    def test_coaches_list_view_guest(self):
        """Проверка списка тренеров для гостя"""
        response = self.guest_client.get(
            reverse('yoga_users:coaches_list')
        )
        self.assertEqual(response.status_code, self.ok)
        self.assertEqual(len(response.context['coaches']), 6)
        self.assertFalse(response.context.get('coach', False))
        self.assertFalse(response.context.get('trainee', False))

    def test_coaches_list_view_trainee(self):
        """Проверка списка тренеров для трейни"""
        response = self.trainee_client.get(
            reverse('yoga_users:coaches_list')
        )
        self.assertEqual(response.status_code, self.ok)
        self.assertTrue(response.context['trainee'])
        self.assertFalse(response.context.get('coach', False))

    def test_coaches_list_view_coach(self):
        """Проверка списка тренеров для тренера"""
        response = self.coach_client.get(
            reverse('yoga_users:coaches_list')
        )
        self.assertEqual(response.status_code, self.ok)
        self.assertTrue(response.context['coach'])
        self.assertFalse(response.context.get('trainee', False))

    def test_coaches_list_pagination(self):
        """Проверка пагинации списка тренеров"""
        response = self.guest_client.get(
            reverse('yoga_users:coaches_list') + '?page=2'
        )
        self.assertEqual(response.status_code, self.ok)
        self.assertEqual(len(response.context['coaches']), 1)  # 7 тренеров всего

    def test_coach_profile_view(self):
        """Проверка профиля тренера"""
        response = self.guest_client.get(
            reverse('yoga_users:coach_profile', kwargs={'coach_id': self.coach.id})
        )
        self.assertEqual(response.status_code, self.ok)
        self.assertEqual(response.context['coach'], self.coach)

    def test_coach_profile_view_wrong_id(self):
        """Проверка профиля тренера с несуществующим ID"""
        response = self.guest_client.get(
            reverse('yoga_users:coach_profile', kwargs={'coach_id': 999})
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_coach_profile_view_not_coach(self):
        """Проверка профиля для пользователя не-тренера"""
        response = self.guest_client.get(
            reverse('yoga_users:coach_profile', kwargs={'coach_id': self.trainee.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_login_view(self):
        """Проверка входа в систему"""
        response = self.guest_client.post(
            reverse('yoga_users:login'),
            {'username': 'trainee1', 'password': 'testpass123'},
            follow=True
        )
        self.assertEqual(response.status_code, self.ok)

    def test_logout_view(self):
        """Проверка выхода из системы"""
        response = self.trainee_client.get(
            reverse('yoga_users:logout'),
            follow=True
        )
        self.assertEqual(response.status_code, self.ok)
