from django.apps import AppConfig
from django.db.models.signals import post_migrate

class ApielearningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'APIElearning'

    def ready(self):
        from .create_responsable import create_responsable_user
        post_migrate.connect(create_responsable_user, sender=self)
