from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from yoga_app.models import (
    ExerciseType, Exercise, Style, Training,
    TrainingRequest, CoachingRequest, WorkoutStatistic,
    ProgramRequest, ProgramItem, Program
)
from yoga_users.models import User
from yoga_app.constants import PERSONAL
from yoga_users.constants import COACH, TRAINEE


class ModelTests(TestCase):
    def setUp(self):
        # Создаем тестовых пользователей
        self.coach = User.objects.create_user(
            username='coach',
            email='coach@example.com',
            password='testpass123',
            role=COACH
        )
        self.trainee = User.objects.create_user(
            username='trainee',
            email='trainee@example.com',
            password='testpass123',
            coach=self.coach,
            role=TRAINEE
        )

        # Создаем тестовые данные
        self.exercise_type = ExerciseType.objects.create(
            name='Асаны',
            description='Описание типа упражнений'
        )

        self.style = Style.objects.create(
            name='Хатха-йога',
            description='Традиционный стиль йоги'
        )

        self.exercise = Exercise.objects.create(
            name='Поза дерева',
            description='Балансирующая асана',
            duration=60,
            complexity=2
        )
        self.exercise.types.add(self.exercise_type)

        self.training_request = TrainingRequest.objects.create(
            trainee=self.trainee,
            style=self.style,
            complexity=2
        )

        self.training = Training.objects.create(
            name='Утренний комплекс',
            type=PERSONAL,
            request=self.training_request,
            style=self.style
        )
        self.training.exercises.add(self.exercise)

        self.coaching_request = CoachingRequest.objects.create(
            trainee=self.trainee,
            coach=self.coach
        )

        self.workout_stat = WorkoutStatistic.objects.create(
            user=self.trainee,
            training=self.training
        )

        self.program_request = ProgramRequest.objects.create(
            trainee=self.trainee
        )

        self.program = Program.objects.create(
            name='Программа для начинающих',
            program_request=self.program_request
        )

        self.program_item = ProgramItem.objects.create(
            weekday='monday',
            training=self.training,
            program_request=self.program_request
        )

    # ExerciseType Model Tests
    def test_exercise_type_creation(self):
        self.assertEqual(self.exercise_type.name, 'Асаны')

    def test_exercise_type_unique_name(self):
        with self.assertRaises(Exception):
            ExerciseType.objects.create(name='Асаны')

    # Exercise Model Tests
    def test_exercise_creation(self):
        self.assertEqual(self.exercise.name, 'Поза дерева')
        self.assertEqual(self.exercise.duration, 60)
        self.assertEqual(self.exercise.complexity, 2)

    def test_exercise_duration_validation(self):
        exercise = Exercise(
            name='Неправильная длительность',
            duration=20  # Меньше минимального
        )
        with self.assertRaises(ValidationError):
            exercise.full_clean()

    def test_exercise_image_upload(self):
        image = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        exercise = Exercise.objects.create(
            name='С изображением',
            duration=30,
            complexity=1,
            image=image
        )
        self.assertTrue(exercise.image.name.startswith('images/exercises/'))

    # Style Model Tests
    def test_style_creation(self):
        self.assertEqual(self.style.name, 'Хатха-йога')

    def test_style_unique_name(self):
        with self.assertRaises(Exception):
            Style.objects.create(name='Хатха-йога')

    # Training Model Tests
    def test_training_creation(self):
        self.assertEqual(self.training.name, 'Утренний комплекс')
        self.assertEqual(self.training.type, PERSONAL)
        self.assertEqual(self.training.request, self.training_request)

    def test_training_total_duration(self):
        self.assertEqual(self.training.get_total_duration(), '1 мин')

    def test_training_complexity_display(self):
        self.assertEqual(self.training.get_complexity_display(), 'Средний уровень')

    def test_training_unique_name(self):
        with self.assertRaises(Exception):
            Training.objects.create(name='Утренний комплекс')

    def test_training_with_expired_request(self):
        expired_request = TrainingRequest.objects.create(
            trainee=self.trainee,
            expired=True
        )
        training = Training(request=expired_request)
        with self.assertRaises(ValidationError):
            training.clean()

    # TrainingRequest Model Tests
    def test_training_request_creation(self):
        self.assertEqual(self.training_request.trainee, self.trainee)
        self.assertEqual(self.training_request.style, self.style)

    def test_training_request_default_values(self):
        request = TrainingRequest.objects.create(trainee=self.trainee)
        self.assertEqual(request.duration, 30)
        self.assertEqual(request.complexity, 1)
        self.assertFalse(request.accepted)
        self.assertFalse(request.expired)

    # CoachingRequest Model Tests
    def test_coaching_request_creation(self):
        self.assertEqual(self.coaching_request.trainee, self.trainee)
        self.assertEqual(self.coaching_request.coach, self.coach)

    def test_coaching_request_coach_validation(self):
        with self.assertRaises(ValidationError):
            CoachingRequest(trainee=self.trainee, coach=self.trainee).clean()

    # WorkoutStatistic Model Tests
    def test_workout_statistic_creation(self):
        self.assertEqual(self.workout_stat.user, self.trainee)
        self.assertEqual(self.workout_stat.training, self.training)
        self.assertEqual(self.workout_stat.count_exercises, 0)
        self.assertIsNone(self.workout_stat.end_time)

    # ProgramRequest Model Tests
    def test_program_request_creation(self):
        self.assertEqual(self.program_request.trainee, self.trainee)


    def test_program_item_creation(self):
        self.assertEqual(self.program_item.weekday, 'monday')
        self.assertEqual(self.program_item.training, self.training)
        self.assertEqual(self.program_item.program_request, self.program_request)

    # Program Model Tests
    def test_program_creation(self):
        self.assertEqual(self.program.name, 'Программа для начинающих')
        self.assertEqual(self.program.program_request, self.program_request)