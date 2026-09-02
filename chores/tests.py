from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import ChoreForm
from .models import Chore, CompletionHistory


class ChoreModelTests(TestCase):
    def test_string_representation(self):
        self.assertEqual(str(Chore(name="Wash dishes")), "Wash dishes")

    def test_completed_chore_requires_completion_time(self):
        with self.assertRaises(ValidationError):
            Chore(name="Wash dishes", is_completed=True).full_clean()

    def test_recurring_completion_creates_next_occurrence_and_history(self):
        due = timezone.now().replace(microsecond=0)
        chore = Chore.objects.create(name="Water plants", recurrence=Chore.Recurrence.WEEKLY, due_date=due)

        next_chore = chore.complete()

        chore.refresh_from_db()
        self.assertTrue(chore.is_completed)
        self.assertIsNotNone(chore.completed_at)
        self.assertEqual(CompletionHistory.objects.count(), 1)
        self.assertEqual(next_chore.due_date, due + timedelta(weeks=1))
        self.assertFalse(next_chore.is_completed)


class ChoreFormTests(TestCase):
    def test_recurring_chore_requires_due_date(self):
        form = ChoreForm(data={"name": "Water plants", "recurrence": Chore.Recurrence.DAILY})

        self.assertFalse(form.is_valid())
        self.assertIn("due_date", form.errors)


class ChoreViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="alex", password="test-pass-123")
        self.other_user = get_user_model().objects.create_user(username="sam", password="test-pass-123")

    def test_list_shows_only_incomplete_chores(self):
        Chore.objects.create(name="Open chore")
        Chore.objects.create(name="Done chore", is_completed=True, completed_at=timezone.now())

        response = self.client.get(reverse("chores:list"))

        self.assertContains(response, "Open chore")
        self.assertNotContains(response, "Done chore")

    def test_authenticated_user_can_create_chore(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("chores:create"), {"name": "Take out bins", "recurrence": "none"})

        self.assertRedirects(response, reverse("chores:list"))
        self.assertEqual(Chore.objects.get().created_by, self.user)

    def test_user_can_sign_in_through_application_login(self):
        response = self.client.post(
            reverse("login"),
            {"username": "alex", "password": "test-pass-123"},
        )

        self.assertRedirects(response, reverse("chores:list"))

    def test_user_can_sign_up_and_is_signed_in(self):
        response = self.client.post(
            reverse("chores:signup"),
            {"username": "new-user", "password1": "a-strong-password-123", "password2": "a-strong-password-123"},
        )

        self.assertRedirects(response, reverse("chores:list"))
        self.assertTrue(get_user_model().objects.filter(username="new-user").exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_authenticated_user_can_sign_out(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("logout"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_requires_post(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("logout"))

        self.assertEqual(response.status_code, 405)

    def test_login_page_links_to_sign_up(self):
        response = self.client.get(reverse("login"))

        self.assertContains(response, 'href="/accounts/signup/"')

    def test_only_owner_or_assignee_can_edit_or_complete(self):
        chore = Chore.objects.create(name="Private edit", created_by=self.user)
        self.client.force_login(self.other_user)

        self.assertEqual(self.client.get(reverse("chores:edit", args=[chore.pk])).status_code, 403)
        response = self.client.post(reverse("chores:complete", args=[chore.pk]))

        self.assertRedirects(response, reverse("chores:list"))
        self.assertFalse(Chore.objects.get(pk=chore.pk).is_completed)

    def test_owner_can_complete_chore(self):
        chore = Chore.objects.create(name="Finish report", created_by=self.user)
        self.client.force_login(self.user)

        response = self.client.post(reverse("chores:complete", args=[chore.pk]))

        self.assertRedirects(response, reverse("chores:list"))
        self.assertTrue(Chore.objects.get(pk=chore.pk).is_completed)
