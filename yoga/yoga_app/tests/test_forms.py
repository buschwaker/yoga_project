from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django import forms

from yoga_app.forms import CustomUserChangeForm, TrainingRequestForm
from yoga_app.models import Style
from yoga_users.constants import COACH, TRAINEE

User = get_user_model()


class CustomUserChangeFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=TRAINEE
        )

    def setUp(self):
        self.form_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@example.com',
            'height': 180,
            'weight': 75,
            'gender': 'M',
        }
        self.image = SimpleUploadedFile(
            name='test_avatar.jpg',
            content=b'simple image content',
            content_type='image/jpeg'
        )

    def test_custom_user_change_form_fields(self):
        """Проверка полей формы изменения профиля"""
        form = CustomUserChangeForm(instance=self.user)
        self.assertIsInstance(
            form.fields['first_name'], forms.fields.CharField
        )
        self.assertIsInstance(
            form.fields['last_name'], forms.fields.CharField
        )
        self.assertIsInstance(
            form.fields['email'], forms.fields.EmailField
        )
        self.assertIsInstance(
            form.fields['height'], forms.fields.IntegerField
        )
        self.assertIsInstance(
            form.fields['weight'], forms.fields.IntegerField
        )
        self.assertIsInstance(
            form.fields['gender'], forms.fields.ChoiceField
        )
        self.assertIsInstance(
            form.fields['avatar'], forms.fields.ImageField
        )


class TrainingRequestFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.style = Style.objects.create(
            name='Хатха-йога',
            description='Традиционный стиль йоги'
        )
        cls.user = User.objects.create_user(
            username='trainee',
            role=TRAINEE,
            password='testpass123'
        )

    def setUp(self):
        self.form_data = {
            'duration': 60,
            'complexity': 2,
            'style': self.style.id,
            'description': 'Хочу научиться основам йоги'
        }


    def test_training_request_form_valid(self):
        """Проверка валидности формы с корректными данными"""
        form = TrainingRequestForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_training_request_form_save(self):
        """Проверка сохранения формы запроса на тренировку"""
        form = TrainingRequestForm(data=self.form_data)
        if form.is_valid():
            training_request = form.save(commit=False)
            training_request.trainee = self.user
            training_request.save()

        self.assertEqual(self.user.training_requests.count(), 1)
        request = self.user.training_requests.first()
        self.assertEqual(request.duration, 60)
        self.assertEqual(request.complexity, 2)
        self.assertEqual(request.style, self.style)
        self.assertEqual(request.description, 'Хочу научиться основам йоги')

    def test_training_request_form_widget_attrs(self):
        """Проверка атрибутов виджетов формы"""
        form = TrainingRequestForm()
        self.assertEqual(
            form.fields['duration'].widget.attrs['class'], 'form-control'
        )
        self.assertEqual(
            form.fields['duration'].widget.attrs['min'], 30
        )
        self.assertEqual(
            form.fields['duration'].widget.attrs['max'], 240
        )
        self.assertEqual(
            form.fields['complexity'].widget.attrs['class'], 'form-select'
        )
        self.assertEqual(
            form.fields['description'].widget.attrs['class'], 'form-control'
        )
        self.assertEqual(
            form.fields['description'].widget.attrs['rows'], 4
        )