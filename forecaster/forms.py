from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "assignee",
            "complexity",
            "estimated_hours",
            "actual_hours",
            "status",
            "due_date",
        ]
        widgets = {
            "due_date": forms.DateInput(
                attrs={"type": "date", "class": "border rounded p-2 w-full"}
            ),
            "title": forms.TextInput(attrs={"class": "border rounded p-2 w-full"}),
            "assignee": forms.Select(attrs={"class": "border rounded p-2 w-full"}),
            "complexity": forms.Select(attrs={"class": "border rounded p-2 w-full"}),
            "estimated_hours": forms.NumberInput(
                attrs={"class": "border rounded p-2 w-full"}
            ),
            "actual_hours": forms.NumberInput(
                attrs={"class": "border rounded p-2 w-full"}
            ),
            "status": forms.Select(attrs={"class": "border rounded p-2 w-full"}),
        }
