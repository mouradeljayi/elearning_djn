from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from APIElearning.models import Responsable

def create_responsable_user(**kwargs):
    User = get_user_model()
    email = 'superadmin@example.com'
    password = 'superadmin@1234'
    first_name = 'superadmin'
    last_name = 'superadmin'
    role = 'SUPERADMIN'
    if not User.objects.filter(email=email).exists():
        Responsable.objects.create(email=email, password=password, first_name=first_name, last_name=last_name, role=role)
