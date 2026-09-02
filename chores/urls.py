from django.urls import path

from . import views

app_name = "chores"

urlpatterns = [
    path("", views.ChoreListView.as_view(), name="list"),
    path("new/", views.ChoreCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.ChoreUpdateView.as_view(), name="edit"),
    path("<int:pk>/complete/", views.complete_chore, name="complete"),
    path("households/", views.HouseholdListView.as_view(), name="households"),
    path("households/new/", views.HouseholdCreateView.as_view(), name="household-create"),
    path("households/<slug:slug>/", views.HouseholdDetailView.as_view(), name="household"),
    path("households/<slug:slug>/join/", views.join_household, name="household-join"),
    path("<int:pk>/claim/", views.claim_chore, name="claim"),
    path("<int:pk>/unclaim/", views.unclaim_chore, name="unclaim"),
]
