from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from chores.models import Chore, CompletionHistory, Household, HouseholdMembership, Persona
from chores.demo_credentials import (
    DEMO_LOGIN_EMAIL,
    DEMO_LOGIN_PASSWORD,
    DEMO_LOGIN_USERNAME,
)


HOUSEHOLDS = {
    "scientists-house": ("Scientists House", ["Albert Einstein", "Marie Curie", "Isaac Newton", "Nikola Tesla", "Charles Darwin", "Richard Feynman", "Galileo Galilei", "Johannes Kepler"], [
        "Clean the laboratory", "Organize experiment notes", "Wash the glassware", "Restock chalk", "Take out radioactive waste", "Prepare coffee for the morning discussion", "Calibrate the telescope", "Sort the journals", "Water the greenhouse", "Check the safety equipment",
    ]),
    "movie-directors-house": ("Movie Directors House", ["Bong Joon Ho", "Alberto Rodríguez", "David Fincher", "Tobias Lindholm", "Park Chan-wook", "Denis Villeneuve", "Na Hong-jin", "Grant Singer", "Guillaume Canet"], [
        "Shoot Memories of Murder scene", "Shoot Marshland scene", "Edit the film footage", "Shoot The Game"
    ]),
    "writers-house": ("Writers House", ["Fyodor Dostoevsky", "Virginia Woolf", "Franz Kafka", "George Orwell", "Leo Tolstoy", "Ernest Hemingway"], [
        "Organize the library", "Make coffee", "Clean writing desks", "Water the plants", "Buy printer paper", "Take out recycling", "Sharpen the pencils", "File the manuscripts", "Air the reading room", "Check the dictionaries",
    ]),
    "computer-scientists-house": ("Computer Scientists House", ["Alan Turing", "Ada Lovelace", "Donald Knuth", "Grace Hopper", "Edsger Dijkstra", "Margaret Hamilton"], [
        "Restart the router", "Organize cables", "Clean keyboards", "Back up the household server", "Empty the coffee machine", "Update the shared shopping list", "Patch the home lab", "Label the spare hardware", "Review the backups", "Recycle old batteries",
    ]),
}

LEGACY_DEMO_LOGIN_USERNAME = "demo_movie-directors-house_1"


class Command(BaseCommand):
    help = "Create deterministic, idempotent themed households for development."

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        base_time = timezone.make_aware(datetime(2026, 1, 15, 12, 0))
        created = 0
        legacy_user = User.objects.filter(username=LEGACY_DEMO_LOGIN_USERNAME).first()
        if legacy_user and not User.objects.filter(username=DEMO_LOGIN_USERNAME).exists():
            legacy_user.username = DEMO_LOGIN_USERNAME
            legacy_user.save(update_fields=("username",))
        for slug, (name, people, chore_names) in HOUSEHOLDS.items():
            creator_username = (
                DEMO_LOGIN_USERNAME
                if people[0] == "Bong Joon Ho"
                else slugify(people[0])
            )
            creator, _ = User.objects.get_or_create(username=creator_username, defaults={"email": f"{creator_username}@example.com"})
            creator.set_unusable_password()
            creator.save(update_fields=("password",))
            household, _ = Household.objects.update_or_create(slug=slug, defaults={"name": name, "created_by": creator, "is_public": True})
            for index, display_name in enumerate(people):
                username = (
                    DEMO_LOGIN_USERNAME
                    if display_name == "Bong Joon Ho"
                    else slugify(display_name)
                )
                user, _ = User.objects.get_or_create(username=username, defaults={"email": f"{username}@example.com"})
                if username == DEMO_LOGIN_USERNAME:
                    user.email = DEMO_LOGIN_EMAIL
                    user.set_password(DEMO_LOGIN_PASSWORD)
                    user.save(update_fields=("email", "password"))
                else:
                    user.set_unusable_password()
                    user.save(update_fields=("password",))
                Persona.objects.update_or_create(user=user, defaults={"display_name": display_name, "theme": name, "seeded": True})
                HouseholdMembership.objects.get_or_create(household=household, user=user)
            members = list(household.memberships.order_by("user_id").values_list("user_id", flat=True))
            for index, chore_name in enumerate(chore_names):
                recurrence = Chore.Recurrence.WEEKLY if index == 0 else Chore.Recurrence.DAILY if index == 1 else Chore.Recurrence.NONE
                due_date = base_time + timedelta(days=index - 6)
                if index in (0, 1):
                    due_date = base_time + timedelta(days=730 + index)
                is_completed = index in (2, 3)
                chore, made = Chore.objects.update_or_create(
                    household=household, name=chore_name,
                    defaults={"description": f"A {name} household task.", "recurrence": recurrence, "due_date": due_date, "is_completed": is_completed, "completed_at": base_time - timedelta(days=index + 1) if is_completed else None, "created_by_id": members[0], "claimed_by_id": members[1] if index == 4 else None},
                )
                created += int(made)
                if is_completed:
                    for history_index in range(1 if index == 2 else 3):
                        completed_by = members[(index + history_index) % len(members)]
                        CompletionHistory.objects.get_or_create(chore=chore, completed_by_id=completed_by, completed_at=base_time - timedelta(days=index + history_index + 1))
            # A prior completed occurrence demonstrates recurring history without changing the open seed occurrence.
            prior, _ = Chore.objects.get_or_create(household=household, name=f"Previous {chore_names[0]}", defaults={"recurrence": Chore.Recurrence.WEEKLY, "due_date": base_time - timedelta(days=14), "is_completed": True, "completed_at": base_time - timedelta(days=7), "created_by_id": members[0]})
            CompletionHistory.objects.get_or_create(chore=prior, completed_by_id=members[2], completed_at=base_time - timedelta(days=7))
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(HOUSEHOLDS)} households ({created} new chores)."))
