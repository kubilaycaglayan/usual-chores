from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.core import management
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .demo_credentials import (
    DEMO_LOGIN_PASSWORD,
    DEMO_LOGIN_USERNAME,
)
from .management.commands.seed_demo import HOUSEHOLDS
from .models import Chore, CompletionHistory, Household, HouseholdMembership, Persona


class AccountWorkflowTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="alex", password="test-pass-123"
        )
        self.admin = user_model.objects.create_superuser(
            username="staff-admin", password="admin-pass-123", email="staff-admin@example.com"
        )

    def test_new_chore_form_does_not_offer_admin_users_for_assignment(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("chores:create"))

        self.assertNotContains(response, 'value="%s"' % self.admin.pk)
        self.assertNotContains(response, ">staff-admin</option>")

    def test_authenticated_user_can_sign_out_from_the_application(self):
        login_response = self.client.post(
            reverse("login"),
            {"username": "alex", "password": "test-pass-123"},
        )
        self.assertRedirects(login_response, reverse("chores:list"))

        homepage = self.client.get(reverse("chores:list"))
        self.assertContains(
            homepage,
            '<form method="post" action="/accounts/logout/"',
            html=False,
        )

        logout_response = self.client.post(reverse("logout"))

        self.assertEqual(logout_response.status_code, 302)
        self.assertEqual(logout_response["Location"], reverse("chores:list"))
        self.assertFalse(logout_response.wsgi_request.user.is_authenticated)
        homepage_after_logout = self.client.get(logout_response["Location"])
        self.assertContains(homepage_after_logout, "Signed out.")
        self.assertNotContains(homepage_after_logout, "Django administration")


class HouseholdWorkflowTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username="owner", password="pass")
        self.member = user_model.objects.create_user(username="member", password="pass")
        self.outsider = user_model.objects.create_user(username="outsider", password="pass")
        self.household = Household.objects.create(
            name="Home Team", slug="home-team", created_by=self.owner
        )
        self.household.add_member(self.owner)
        self.household.add_member(self.member)

    def test_user_can_create_household_and_is_added_as_member(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("chores:household-create"), {"name": "New Nest"}
        )

        household = Household.objects.get(slug="new-nest")
        self.assertRedirects(response, reverse("chores:households"))
        self.assertTrue(
            household.memberships.filter(user=self.owner).exists()
        )

    def test_public_household_list_and_detail_show_household_data(self):
        Household.objects.create(
            name="Private Home", slug="private-home", created_by=self.owner, is_public=False
        )
        Chore.objects.create(name="Sweep floor", household=self.household)

        listing = self.client.get(reverse("chores:households"))
        detail = self.client.get(
            reverse("chores:household", args=[self.household.slug])
        )

        self.assertContains(listing, "Home Team")
        self.assertNotContains(listing, "Private Home")
        self.assertContains(detail, "Home Team")
        self.assertContains(detail, "Sweep floor")
        self.assertContains(detail, "owner")

    def test_joining_adds_member_and_nonmember_cannot_add_household_chore(self):
        self.client.force_login(self.outsider)
        response = self.client.post(
            reverse("chores:household-join", args=[self.household.slug])
        )
        self.assertRedirects(
            response, reverse("chores:household", args=[self.household.slug])
        )
        self.assertTrue(
            self.household.memberships.filter(user=self.outsider).exists()
        )

        other_household = Household.objects.create(
            name="Other Home", slug="other-home", created_by=self.owner
        )
        response = self.client.post(
            reverse("chores:create"),
            {"name": "Unauthorized chore", "household": other_household.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Chore.objects.filter(name="Unauthorized chore").exists())

    def test_user_is_added_to_household_when_creating_its_chore(self):
        self.client.force_login(self.outsider)

        response = self.client.post(
            reverse("chores:create"),
            {"name": "Sweep porch", "recurrence": "none", "household": self.household.pk},
        )

        self.assertRedirects(response, reverse("chores:list"))
        self.assertTrue(self.household.memberships.filter(user=self.outsider).exists())
        self.assertTrue(
            Chore.objects.filter(name="Sweep porch", household=self.household).exists()
        )

    def test_household_pages_show_new_chore_action(self):
        self.client.force_login(self.member)

        households = self.client.get(reverse("chores:households"))
        detail = self.client.get(
            reverse("chores:household", args=[self.household.slug])
        )

        self.assertContains(households, 'href="/new/"')
        self.assertContains(detail, 'href="/new/"')

    def test_member_can_create_and_edit_household_chore(self):
        self.client.force_login(self.member)
        create_response = self.client.post(
            reverse("chores:create"),
            {"name": "Wash windows", "description": "Both floors", "recurrence": "none", "household": self.household.pk},
        )
        chore = Chore.objects.get(name="Wash windows")

        self.assertRedirects(create_response, reverse("chores:list"))
        self.assertEqual(chore.created_by, self.member)
        edit_response = self.client.post(
            reverse("chores:edit", args=[chore.pk]),
            {"name": "Wash all windows", "description": "Both floors", "recurrence": "none", "household": self.household.pk},
        )
        self.assertRedirects(edit_response, reverse("chores:list"))
        self.assertTrue(Chore.objects.filter(name="Wash all windows").exists())

    def test_household_members_are_limited_to_ten(self):
        user_model = get_user_model()
        for index in range(8):
            self.household.add_member(
                user_model.objects.create_user(username=f"member-{index}")
            )

        with self.assertRaisesMessage(ValidationError, "at most 10 members"):
            self.household.add_member(
                user_model.objects.create_user(username="eleventh")
            )
        self.assertEqual(self.household.memberships.count(), 10)


class ChoreClaimingAndCompletionTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username="owner", password="pass")
        self.member = user_model.objects.create_user(username="member", password="pass")
        self.outsider = user_model.objects.create_user(username="outsider", password="pass")
        self.household = Household.objects.create(
            name="Home Team", slug="home-team", created_by=self.owner
        )
        self.household.add_member(self.owner)
        self.household.add_member(self.member)

    def test_member_can_claim_and_unclaim_open_chore(self):
        chore = Chore.objects.create(name="Open task", household=self.household)
        self.client.force_login(self.member)

        claim = self.client.post(reverse("chores:claim", args=[chore.pk]))
        chore.refresh_from_db()
        self.assertRedirects(claim, reverse("chores:household", args=["home-team"]))
        self.assertEqual(chore.claimed_by, self.member)
        self.assertEqual(chore.status, "Claimed")

        unclaim = self.client.post(reverse("chores:unclaim", args=[chore.pk]))
        chore.refresh_from_db()
        self.assertRedirects(unclaim, reverse("chores:household", args=["home-team"]))
        self.assertIsNone(chore.claimed_by)

    def test_outsider_cannot_claim_and_overdue_chore_cannot_be_unclaimed(self):
        chore = Chore.objects.create(name="Restricted task", household=self.household)
        self.client.force_login(self.outsider)
        response = self.client.post(reverse("chores:claim", args=[chore.pk]))
        self.assertRedirects(response, reverse("chores:list"))
        self.assertIsNone(Chore.objects.get(pk=chore.pk).claimed_by)

        chore.claimed_by = self.member
        chore.due_date = timezone.now() - timedelta(minutes=1)
        chore.save(update_fields=("claimed_by", "due_date", "updated_at"))
        self.client.force_login(self.member)
        self.client.post(reverse("chores:unclaim", args=[chore.pk]))
        self.assertEqual(Chore.objects.get(pk=chore.pk).claimed_by, self.member)

    def test_member_completes_recurring_chore_through_application(self):
        due = timezone.now().replace(microsecond=0)
        chore = Chore.objects.create(
            name="Water plants", recurrence=Chore.Recurrence.WEEKLY,
            due_date=due, household=self.household, claimed_by=self.member,
        )
        self.client.force_login(self.member)

        response = self.client.post(reverse("chores:complete", args=[chore.pk]))

        self.assertRedirects(response, reverse("chores:list"))
        chore.refresh_from_db()
        next_chore = Chore.objects.get(name="Water plants", is_completed=False)
        self.assertTrue(chore.is_completed)
        self.assertEqual(chore.completion_history.get().completed_by, self.member)
        self.assertEqual(next_chore.due_date, due + timedelta(weeks=1))


class HouseholdInsightTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.alex = user_model.objects.create_user(username="alex", password="pass")
        self.sam = user_model.objects.create_user(username="sam", password="pass")
        self.household = Household.objects.create(
            name="Insight Home", slug="insight-home", created_by=self.alex
        )
        self.household.add_member(self.alex)
        self.household.add_member(self.sam)

    def test_detail_shows_deadline_alerts_stats_and_recommendations(self):
        overdue = Chore.objects.create(
            name="Overdue task", household=self.household,
            due_date=timezone.now() - timedelta(hours=1), claimed_by=self.sam,
        )
        soon = Chore.objects.create(
            name="Soon task", household=self.household,
            due_date=timezone.now() + timedelta(hours=1), claimed_by=self.sam,
        )
        Chore.objects.create(
            name="Recommended task", household=self.household,
            due_date=timezone.now() + timedelta(days=4),
        )
        completed = Chore.objects.create(
            name="Completed task", household=self.household,
            is_completed=True, completed_at=timezone.now(),
        )
        CompletionHistory.objects.create(chore=completed, completed_by=self.alex)
        CompletionHistory.objects.create(chore=completed, completed_by=self.alex)
        CompletionHistory.objects.create(chore=completed, completed_by=self.sam)

        response = self.client.get(
            reverse("chores:household", args=[self.household.slug])
        )

        self.assertContains(response, "Overdue task is overdue")
        self.assertContains(response, "Soon task is due soon")
        self.assertContains(response, "alex: 2")
        self.assertContains(response, "sam: 1")
        self.assertContains(response, "Recommended task")
        self.assertContains(response, "Completed task")
        self.assertTrue(overdue.is_overdue)
        self.assertFalse(soon.is_overdue)


class DemoSeedIntegrationTests(TestCase):
    def test_seed_demo_creates_expected_idempotent_dataset(self):
        first_output = StringIO()
        management.call_command("seed_demo", stdout=first_output)
        first_counts = (
            Household.objects.count(),
            Persona.objects.count(),
            Chore.objects.count(),
            CompletionHistory.objects.count(),
            HouseholdMembership.objects.count(),
        )

        second_output = StringIO()
        management.call_command("seed_demo", stdout=second_output)

        self.assertEqual(first_counts, (
            len(HOUSEHOLDS),
            sum(len(people) for _, people, _ in HOUSEHOLDS.values()),
            sum(len(chores) + 1 for _, _, chores in HOUSEHOLDS.values()),
            20,
            sum(len(people) for _, people, _ in HOUSEHOLDS.values()),
        ))
        self.assertEqual(
            first_counts,
            (
                Household.objects.count(), Persona.objects.count(), Chore.objects.count(),
                CompletionHistory.objects.count(), HouseholdMembership.objects.count(),
            ),
        )
        self.assertIn("Seeded 4 households", first_output.getvalue())
        self.assertIn("Seeded 4 households", second_output.getvalue())
        self.assertTrue(Persona.objects.filter(display_name="Einstein").exists())

    def test_seeded_director_account_can_log_in_and_is_shown_on_login_page(self):
        management.call_command("seed_demo", stdout=StringIO())

        self.assertTrue(self.client.login(username=DEMO_LOGIN_USERNAME, password=DEMO_LOGIN_PASSWORD))
        self.assertEqual(self.client.session["_auth_user_id"], str(
            get_user_model().objects.get(username=DEMO_LOGIN_USERNAME).pk
        ))

    def test_login_form_prefills_credentials_and_has_show_password_toggle(self):
        management.call_command("seed_demo", stdout=StringIO())

        response = self.client.get(reverse("login"))

        self.assertContains(response, DEMO_LOGIN_USERNAME)
        self.assertContains(response, DEMO_LOGIN_PASSWORD)
        self.assertContains(response, 'name="username" value="bong-joon-ho"')
        self.assertContains(response, 'type="password" name="password" value="usual-chores-director"')
        self.assertContains(response, '<button type="button" id="password-toggle"')
        self.assertContains(response, 'aria-controls="id_password"')
        self.assertContains(response, "passwordInput.type = showing ? \"password\" : \"text\";")


class AdminIntegrationTests(TestCase):
    def test_development_admin_can_open_registered_chore_models(self):
        response = self.client.post(
            reverse("admin:login"),
            {"username": "admin", "password": "usual-chores-admin"},
        )
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chores")
        self.assertContains(response, "Completion historys")
