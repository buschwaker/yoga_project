import os
import shutil

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from yoga_app.constants import BASE, PERSONAL
from yoga_app.models import CoachingRequest, Training
from yoga_users.constants import TRAINEE


def attach_photo(training, image_path):
    if not os.path.exists(image_path):
        print(f"No file: {image_path}")
        return
    upload_to_dir = Training._meta.get_field("image").upload_to
    image_name = os.path.basename(image_path)
    media_image_dir = os.path.join(settings.MEDIA_ROOT, upload_to_dir)
    os.makedirs(media_image_dir, exist_ok=True)
    media_image_path = os.path.join(media_image_dir, image_name)
    if not os.path.exists(media_image_path):
        shutil.copy(image_path, os.path.join(media_image_dir, image_name))

    training_image = os.path.join(upload_to_dir, image_name)
    training.image = training_image
    training.save()


def create_base_trainings(training_info):
    training = Training.objects.create(
        name=training_info["name"],
        description=training_info["description"],
        type=training_info["type"],
    )
    attach_photo(training, training_info["image"])


@receiver(post_migrate)
def base_trainings_handler(sender, **kwargs):
    if Training.objects.exists():
        return
    #  TO-DO
    # exercises =
    images_path = os.path.join(settings.BASE_DIR, "static/img")
    trainings_info = [
        {
            "name": "Йога для начинающих",
            "description": "Занятия для тех, кто только начинает путь в йогу",
            "type": BASE,
            "image": os.path.join(images_path, "newby.jpeg"),
        },
        {
            "name": "Йога для продвинутых",
            "description": "Интенсивные занятия для опытных практиков",
            "type": BASE,
            "image": os.path.join(images_path, "advanced.jpg"),
        },
        {
            "name": "Йога для беременных",
            "description": "Специальные занятия для будущих мам",
            "type": BASE,
            "image": os.path.join(images_path, "pregnancy.jpg"),
        },
    ]
    for info in trainings_info:
        create_base_trainings(info)
