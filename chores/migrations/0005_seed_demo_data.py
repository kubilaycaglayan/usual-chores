import sys

from django.core.management import call_command
from django.db import migrations


def seed_demo_data(apps, schema_editor):
    if "test" in sys.argv:
        return
    call_command("seed_demo", verbosity=0)


def remove_demo_data(apps, schema_editor):
    User = apps.get_model("auth", "User")
    User.objects.filter(username__startswith="demo_").delete()


class Migration(migrations.Migration):
    dependencies = [("chores", "0004_chore_claimed_by_household_chore_household_persona_and_more")]

    operations = [migrations.RunPython(seed_demo_data, remove_demo_data)]
