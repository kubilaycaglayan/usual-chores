from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


USERNAME = "admin"
EMAIL = "admin@example.com"
PASSWORD = "usual-chores-admin"


class Command(BaseCommand):
    help = "Create or update the local development administrator account."

    def handle(self, *args, **options):
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=USERNAME,
            defaults={"email": EMAIL},
        )
        user.email = EMAIL
        user.is_staff = True
        user.is_superuser = True
        user.set_password(PASSWORD)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} development admin user '{USERNAME}'."))
