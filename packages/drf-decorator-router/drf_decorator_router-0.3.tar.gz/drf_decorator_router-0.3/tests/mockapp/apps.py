from django.apps import AppConfig


class MockappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tests.mockapp'

    def ready(self):
        from . import routers
