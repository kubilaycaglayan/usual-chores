from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, UpdateView

from .forms import ChoreForm, HouseholdForm
from .models import Chore, CompletionHistory, Household


def sign_up(request):
    if request.user.is_authenticated:
        return redirect("chores:list")

    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        next_url = request.POST.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            return redirect(next_url)
        return redirect("chores:list")
    return render(
        request,
        "registration/signup.html",
        {"form": form, "next": request.POST.get("next") or request.GET.get("next", "")},
    )


@require_POST
def sign_out(request):
    logout(request)
    messages.success(request, "Signed out.")
    return redirect("chores:list")


class ChoreListView(ListView):
    model = Chore
    context_object_name = "chores"
    template_name = "chores/chore_list.html"

    def get_queryset(self):
        return Chore.objects.filter(is_completed=False).select_related("assigned_to", "created_by")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.utils import timezone

        context["now"] = timezone.now()
        return context


class ChoreCreateView(LoginRequiredMixin, CreateView):
    model = Chore
    form_class = ChoreForm
    template_name = "chores/chore_form.html"
    success_url = reverse_lazy("chores:list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        household = form.cleaned_data.get("household")
        if household:
            household.add_member(self.request.user)
        form.instance.household = household
        messages.success(self.request, "Chore created.")
        return super().form_valid(form)


class ChoreUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Chore
    form_class = ChoreForm
    template_name = "chores/chore_form.html"
    success_url = reverse_lazy("chores:list")

    def test_func(self):
        chore = self.get_object()
        member = chore.household and chore.household.memberships.filter(user=self.request.user).exists()
        return chore.created_by == self.request.user or chore.assigned_to == self.request.user or member

    def form_valid(self, form):
        messages.success(self.request, "Chore updated.")
        return super().form_valid(form)


@require_POST
def complete_chore(request, pk):
    if not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")
    chore = get_object_or_404(Chore, pk=pk)
    member = chore.household and chore.household.memberships.filter(user=request.user).exists()
    if chore.created_by != request.user and chore.assigned_to != request.user and chore.claimed_by != request.user and not member:
        return HttpResponseRedirect(reverse_lazy("chores:list"))
    next_chore = chore.complete(request.user)
    messages.success(request, "Chore completed.")
    if next_chore:
        messages.info(request, "The next occurrence was scheduled.")
    return redirect("chores:list")


class HouseholdListView(ListView):
    model = Household
    context_object_name = "households"
    template_name = "chores/household_list.html"

    def get_queryset(self):
        return Household.objects.filter(is_public=True).prefetch_related("memberships__user")


class HouseholdDetailView(ListView):
    model = Chore
    context_object_name = "chores"
    template_name = "chores/household_detail.html"

    def get_household(self):
        return get_object_or_404(Household, slug=self.kwargs["slug"], is_public=True)

    def get_queryset(self):
        return Chore.objects.filter(household=self.get_household()).select_related("claimed_by", "assigned_to")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        household = self.get_household()
        context["household"] = household
        context["members"] = household.memberships.select_related("user", "user__persona")
        counts = CompletionHistory.objects.filter(chore__household=household).values("completed_by__username").annotate(completed_count=Count("id")).order_by("completed_count", "completed_by__username")
        context["stats"] = counts
        context["recommendations"] = self.get_queryset().filter(is_completed=False, claimed_by__isnull=True).order_by("due_date", "name")[:3]
        context["is_member"] = (
            self.request.user.is_authenticated
            and household.memberships.filter(user=self.request.user).exists()
        )
        context["deadline_alerts"] = self.get_queryset().filter(is_completed=False, claimed_by__isnull=False, due_date__lte=timezone.now() + timedelta(days=2)).order_by("due_date")
        return context


class HouseholdCreateView(LoginRequiredMixin, CreateView):
    model = Household
    form_class = HouseholdForm
    template_name = "chores/household_form.html"
    success_url = reverse_lazy("chores:households")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        self.object.add_member(self.request.user)
        return response


@login_required
@require_POST
def join_household(request, slug):
    household = get_object_or_404(Household, slug=slug, is_public=True)
    try:
        household.add_member(request.user)
    except Exception as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f"Joined {household.name}.")
    return redirect("chores:household", slug=slug)


@login_required
@require_POST
def claim_chore(request, pk):
    chore = get_object_or_404(Chore, pk=pk)
    if chore.household and not chore.household.memberships.filter(user=request.user).exists():
        return HttpResponseRedirect(reverse_lazy("chores:list"))
    if not chore.is_completed and not chore.claimed_by_id:
        chore.claimed_by = request.user
        chore.save(update_fields=("claimed_by", "updated_at"))
    return redirect("chores:household", slug=chore.household.slug) if chore.household else redirect("chores:list")


@require_POST
def unclaim_chore(request, pk):
    chore = get_object_or_404(Chore, pk=pk)
    if chore.claimed_by == request.user and not chore.is_overdue:
        chore.claimed_by = None
        chore.save(update_fields=("claimed_by", "updated_at"))
    return redirect("chores:household", slug=chore.household.slug) if chore.household else redirect("chores:list")
