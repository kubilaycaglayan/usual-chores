from django.contrib.auth import get_user_model
from django.db import migrations


USERNAME = "admin"
EMAIL = "admin@example.com"
PASSWORD = "usual-chores-admin"


def create_development_admin(apps, schema_editor):
    user_model = get_user_model()
    user, _ = user_model.objects.get_or_create(
        username=USERNAME,
        defaults={"email": EMAIL},
    )
    user.email = EMAIL
    user.is_staff = True
    user.is_superuser = True
    user.set_password(PASSWORD)
    user.save()


def remove_development_admin(apps, schema_editor):
    get_user_model().objects.filter(username=USERNAME, email=EMAIL).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("chores", "0002_completionhistory"),
    ]

    operations = [
        migrations.RunPython(create_development_admin, remove_development_admin),
    ]
