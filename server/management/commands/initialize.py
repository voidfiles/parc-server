import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        email = os.environ.get('EMAIL', 'voidfiles@example.com')
        password = os.environ.get('PASSWORD', 'testing')
        user, created = User.objects.get_or_create(email=email)

        user.set_password(password)

        user.save()
