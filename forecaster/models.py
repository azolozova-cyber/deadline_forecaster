from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    deadline = models.DateField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    ROLES = [
        ("backend", "Backend Developer"),
        ("frontend", "Frontend Developer"),
        ("qa", "QA Engineer"),
        ("manager", "Project Manager"),
        ("designer", "Designer"),
    ]
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=50, choices=ROLES)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    daily_capacity = models.IntegerField(default=8, help_text="Available hours per day")
    projects = models.ManyToManyField(Project, related_name="members")

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class EmployeeMetric(models.Model):
    member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name="metrics")
    metric_type = models.CharField(max_length=50)  # e.g., 'velocity', 'bus_factor_contribution'
    value = models.FloatField()
    date_recorded = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.full_name} - {self.metric_type}: {self.value}"



class Task(models.Model):
    STATUS_CHOICES = [
        ("todo", "To Do"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
    ]
    COMPLEXITY_CHOICES = [
        (1, "Low (1)"),
        (2, "Medium (2)"),
        (3, "High (3)"),
        (5, "Very High (5)"),
        (8, "Extreme (8)"),
    ]

    title = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assignee = models.ForeignKey(
        TeamMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    complexity = models.IntegerField(choices=COMPLEXITY_CHOICES, default=1)
    estimated_hours = models.IntegerField(help_text="Estimated time in hours")
    actual_hours = models.IntegerField(
        null=True, blank=True, help_text="Actual time spent"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="todo")
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
