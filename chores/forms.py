from django import forms
from django.contrib.auth import get_user_model

from .models import Chore


class ChoreForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
    )

    class Meta:
        model = Chore
        fields = ("name", "description", "recurrence", "due_date", "assigned_to")
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = get_user_model().objects.order_by("username")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("recurrence") != Chore.Recurrence.NONE and not cleaned_data.get("due_date"):
            self.add_error("due_date", "A due date is required for recurring chores.")
        return cleaned_data
