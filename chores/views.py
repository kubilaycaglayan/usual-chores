from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, UpdateView

from .forms import ChoreForm
from .models import Chore


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
        messages.success(self.request, "Chore created.")
        return super().form_valid(form)


class ChoreUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Chore
    form_class = ChoreForm
    template_name = "chores/chore_form.html"
    success_url = reverse_lazy("chores:list")

    def test_func(self):
        chore = self.get_object()
        return chore.created_by == self.request.user or chore.assigned_to == self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Chore updated.")
        return super().form_valid(form)


@require_POST
def complete_chore(request, pk):
    if not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")
    chore = get_object_or_404(Chore, pk=pk)
    if chore.created_by != request.user and chore.assigned_to != request.user:
        return HttpResponseRedirect(reverse_lazy("chores:list"))
    next_chore = chore.complete(request.user)
    messages.success(request, "Chore completed.")
    if next_chore:
        messages.info(request, "The next occurrence was scheduled.")
    return redirect("chores:list")
