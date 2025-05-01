from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse

from yoga_app.models import CoachingRequest, TrainingRequest, Training, Exercise, WorkoutStatistic

User = get_user_model()


class TestUrls(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.trainee = User.objects.create_user(username='trainee', role="trainee")
        cls.coach = User.objects.create_user(username='coach', role="coach")

        cls.coaching_request = CoachingRequest.objects.create(
            trainee=cls.trainee,
            coach=cls.coach
        )
        cls.training_request = TrainingRequest.objects.create(
            trainee=cls.trainee
        )
        cls.training = Training.objects.create(
            name="Test Training",
            type="PERSONAL",
            request=cls.training_request
        )
        cls.exercise = Exercise.objects.create(
            name="Test Exercise",
            description="Test Description",
            duration=35,
            complexity=1
        )
        cls.workout_stat = WorkoutStatistic.objects.create(
            user=cls.trainee,
            training=cls.training
        )

        cls.ok = HTTPStatus.OK.value
        cls.nf = HTTPStatus.NOT_FOUND.value
        cls.found = HTTPStatus.FOUND.value
        cls.forbidden = HTTPStatus.FORBIDDEN.value

    def setUp(self):
        self.guest_client = Client()
        self.trainee_client = Client()
        self.coach_client = Client()
        self.trainee_client.force_login(self.trainee)
        self.coach_client.force_login(self.coach)
        self.clients = [self.guest_client, self.trainee_client, self.coach_client]

    def test_main_page(self):
        url = reverse("yoga:main")
        for client in self.clients:
            with self.subTest(client=client):
                response = self.guest_client.get(url, follow=True)
                self.assertEqual(response.status_code, self.ok)
                self.assertTemplateUsed(
                    response, "yoga/main.html",
                    "wrong template used"
                )

    def test_lk_trainee(self):
        url = reverse("yoga:show_lk")
        expected_statuses = [self.ok, self.ok, self.forbidden]
        expected_templates = [
            "registration/login.html",
            "yoga/lk_trainee.html",
            None,
        ]

        for client, status, template in zip(self.clients, expected_statuses, expected_templates):
            with self.subTest(client=client):
                response = client.get(url, follow=True)
                self.assertEqual(response.status_code, status)
                if template:
                    self.assertTemplateUsed(response, template, "wrong template used")

    def test_trainee_choose_coach_access(self):
        url = reverse("yoga:trainee_trainer_choice")
        responses = [
            (self.guest_client.get(url, follow=True), self.ok, "registration/login.html"),
            (self.trainee_client.get(url), self.ok, "yoga/lk_trainee_choose_coach.html"),
            (self.coach_client.get(url), self.forbidden, None)
        ]

        for response, status, template in responses:
            with self.subTest(response=response):
                self.assertEqual(response.status_code, status)
                if template:
                    self.assertTemplateUsed(response, template)

    def test_trainee_statistics_access(self):
        url = reverse("yoga:trainee_statistics")
        responses = [
            (self.guest_client.get(url, follow=True), self.ok, "registration/login.html"),
            (self.trainee_client.get(url), self.ok, "yoga/lk_trainee_statistics.html"),
            (self.coach_client.get(url), self.forbidden, None)
        ]

        for response, status, template in responses:
            with self.subTest(response=response):
                self.assertEqual(response.status_code, status)
                if template:
                    self.assertTemplateUsed(response, template)

    def test_coach_lk_access(self):
        url = reverse("yoga:coach_lk")
        responses = [
            (self.guest_client.get(url, follow=True), self.ok, "registration/login.html"),
            (self.trainee_client.get(url), self.forbidden, None),
            (self.coach_client.get(url), self.ok, "yoga/coach/lk_coach.html")
        ]

        for response, status, template in responses:
            with self.subTest(response=response):
                self.assertEqual(response.status_code, status)
                if template:
                    self.assertTemplateUsed(response, template)

    def test_coach_requests_access(self):
        url = reverse("yoga:coach_requests")
        responses = [
            (self.guest_client.get(url, follow=True), self.ok, "registration/login.html"),
            (self.trainee_client.get(url), self.forbidden, None),
            (self.coach_client.get(url), self.ok, "yoga/coach/coach_requests.html")
        ]

        for response, status, template in responses:
            with self.subTest(response=response):
                self.assertEqual(response.status_code, status)
                if template:
                    self.assertTemplateUsed(response, template)

    # Тесты для тренировок
    def test_show_workout_access(self):
        url = reverse("yoga:show_workout", kwargs={"training_id": self.training.id})
        responses = [
            (self.guest_client.get(url, follow=True), self.ok, "registration/login.html"),
            (self.trainee_client.get(url), self.ok, "yoga/workouts/training.html"),
            (self.coach_client.get(url), self.forbidden, None)
        ]

        for response, status, template in responses:
            with self.subTest(response=response):
                self.assertEqual(response.status_code, status)
                if template:
                    self.assertTemplateUsed(response, template)

    def test_show_articles_access(self):
        url = reverse("yoga:articles")
        for client in [self.guest_client, self.trainee_client, self.coach_client]:
            with self.subTest(client=client):
                response = client.get(url)
                self.assertEqual(response.status_code, self.ok)
                self.assertTemplateUsed(response, "articles/all_exercises.html")

    def test_articles_exercise_detail_access(self):
        url = reverse("yoga:articles_exercise_detail", kwargs={"exercise_id": self.exercise.id})
        for client in [self.guest_client, self.trainee_client, self.coach_client]:
            with self.subTest(client=client):
                response = client.get(url)
                self.assertEqual(response.status_code, self.ok)
                self.assertTemplateUsed(response, "articles/exercise_detail.html")

    def test_edit_profile_access(self):
        url = reverse("yoga:edit_profile")
        responses = [
            (self.guest_client.get(url, follow=True), self.ok, "registration/login.html"),
            (self.trainee_client.get(url), self.ok, "yoga/edit_profile.html"),
            (self.coach_client.get(url), self.ok, "yoga/edit_profile.html")
        ]

        for response, status, template in responses:
            with self.subTest(response=response):
                self.assertEqual(response.status_code, status)
                if template:
                    self.assertTemplateUsed(response, template)

    def test_accept_coaching_request_access(self):
        url = reverse("yoga:accept_coaching_request", kwargs={"request_id": self.coaching_request.id})
        responses = [
            (self.guest_client.post(url, follow=True), self.ok, "registration/login.html"),
            (self.trainee_client.post(url), self.forbidden, None),
            (self.coach_client.post(url), self.found, None)
        ]

        for response, status, template in responses:
            with self.subTest(response=response):
                self.assertEqual(response.status_code, status)
                if template:
                    self.assertTemplateUsed(response, template)

    def test_delete_coaching_request_access(self):
        url = reverse("yoga:delete_coaching_request", kwargs={"request_id": self.coaching_request.id})
        responses = [
            (self.guest_client.post(url, follow=True), self.ok, "registration/login.html"),
            (self.trainee_client.post(url), self.found, None),
            (self.coach_client.post(url), self.forbidden, None)
        ]

        for response, status, template in responses:
            with self.subTest(response=response):
                self.assertEqual(response.status_code, status)
                if template:
                    self.assertTemplateUsed(response, template)