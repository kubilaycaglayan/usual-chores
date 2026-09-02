from django import forms
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from .models import Chore, Household


class ChoreForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
    )

    class Meta:
        model = Chore
        fields = ("name", "description", "recurrence", "due_date", "assigned_to", "household")
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, household=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = get_user_model().objects.order_by("username")
        self.household = household
        self.fields["household"].required = False

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("recurrence") != Chore.Recurrence.NONE and not cleaned_data.get("due_date"):
            self.add_error("due_date", "A due date is required for recurring chores.")
        return cleaned_data


class HouseholdForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = ("name",)

    def save(self, commit=True):
        household = super().save(commit=False)
        household.slug = slugify(household.name)
        if commit:
            household.save()
        return household
