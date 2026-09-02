from django.urls import path

from . import views

app_name = "chores"

urlpatterns = [
    path("", views.ChoreListView.as_view(), name="list"),
    path("new/", views.ChoreCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.ChoreUpdateView.as_view(), name="edit"),
    path("<int:pk>/complete/", views.complete_chore, name="complete"),
]
