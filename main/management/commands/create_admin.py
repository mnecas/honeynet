from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        # The magic line
        if not User.objects.filter(username="mnecas"):
            user = User.objects.create_user(
                username="mnecas",
                email="mnecas@mnecas.cz",
                is_staff=True,
                is_active=True,
                is_superuser=True,
            )
            user.set_password("mnecas")
            user.save()
            # print("Created mnecas|mnecas admin account")
