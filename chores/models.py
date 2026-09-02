from django.conf import settings
from django.core.exceptions import ValidationError
import calendar
from datetime import timedelta

from django.db import models, transaction
from django.utils import timezone


class Household(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_households")
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def add_member(self, user):
        if not self.memberships.filter(user=user).exists() and self.memberships.count() >= 10:
            raise ValidationError("A household can have at most 10 members.")
        return HouseholdMembership.objects.get_or_create(household=self, user=user)


class Persona(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="persona")
    display_name = models.CharField(max_length=120)
    theme = models.CharField(max_length=120)
    seeded = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name


class HouseholdMembership(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="household_memberships")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("household", "user"), name="unique_household_member")]


class Chore(models.Model):
    class Recurrence(models.TextChoices):
        NONE = "none", "One-off"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    recurrence = models.CharField(
        max_length=10,
        choices=Recurrence.choices,
        default=Recurrence.NONE,
    )
    due_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_chores",
        null=True,
        blank=True,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_chores",
        null=True,
        blank=True,
    )
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="chores", null=True, blank=True)
    claimed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="claimed_chores", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["is_completed", "due_date", "name"]

    def __str__(self):
        return self.name

    def clean(self):
        if self.is_completed and self.completed_at is None:
            raise ValidationError("Completed chores must have a completion time.")
        if not self.is_completed and self.completed_at is not None:
            raise ValidationError("Incomplete chores cannot have a completion time.")
        if self.claimed_by and self.household and not self.household.memberships.filter(user=self.claimed_by).exists():
            raise ValidationError("Only household members can claim its chores.")

    @property
    def status(self):
        if self.is_completed:
            return "Done"
        return "Claimed" if self.claimed_by_id else "Open"

    @property
    def is_overdue(self):
        return bool(self.due_date and self.due_date < timezone.now() and not self.is_completed)

    def mark_complete(self):
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()

    def complete(self, user=None):
        """Complete this occurrence and create the next recurring occurrence."""
        if self.is_completed:
            return None

        with transaction.atomic():
            self.mark_complete()
            self.save(update_fields=["is_completed", "completed_at", "updated_at"])
            CompletionHistory.objects.create(
                chore=self,
                completed_by=user,
                completed_at=self.completed_at,
            )

            if self.recurrence == self.Recurrence.NONE or self.due_date is None:
                return None

            next_due = self.next_due_date()
            return Chore.objects.create(
                name=self.name,
                description=self.description,
                recurrence=self.recurrence,
                due_date=next_due,
                created_by=self.created_by,
                assigned_to=self.assigned_to,
                household=self.household,
            )

    def next_due_date(self):
        if self.due_date is None:
            return None
        if self.recurrence == self.Recurrence.DAILY:
            return self.due_date + timedelta(days=1)
        if self.recurrence == self.Recurrence.WEEKLY:
            return self.due_date + timedelta(weeks=1)
        if self.recurrence == self.Recurrence.MONTHLY:
            month = self.due_date.month % 12 + 1
            year = self.due_date.year + (self.due_date.month // 12)
            day = min(self.due_date.day, calendar.monthrange(year, month)[1])
            return self.due_date.replace(year=year, month=month, day=day)
        return None


class CompletionHistory(models.Model):
    chore = models.ForeignKey(Chore, on_delete=models.CASCADE, related_name="completion_history")
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chore_completions",
    )
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.chore} completed at {self.completed_at:%Y-%m-%d %H:%M}"

    @property
    def member_name(self):
        return self.completed_by.get_full_name() or self.completed_by.username if self.completed_by else "Unknown"
