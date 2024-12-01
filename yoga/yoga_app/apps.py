from django.apps import AppConfig


class YogaAppConfig(AppConfig):
    name = 'yoga_app'

    def ready(self):
        import yoga_app.signals
