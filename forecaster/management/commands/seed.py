from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forecaster.models import Project, TeamMember, Task
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = "Seeds the database with initial data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # Create Superuser
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
            self.stdout.write("Created superuser: admin/admin")

        user = User.objects.get(username="admin")

        # Create members
        members = []
        roles = ["backend", "frontend", "qa", "manager", "designer"]
        names = ["Alice", "Bob", "Charlie", "David", "Eve"]
        for name, role in zip(names, roles):
            member, created = TeamMember.objects.get_or_create(
                full_name=name, defaults={"role": role, "hourly_rate": 50}
            )
            members.append(member)

        # Create Projects and Tasks
        for i in range(1, 4):
            project, created = Project.objects.get_or_create(
                name=f"Project {i}",
                defaults={
                    "description": f"Description for Project {i}",
                    "start_date": date.today(),
                    "deadline": date.today() + timedelta(days=30),
                    "owner": user,
                },
            )

            # Add members
            project.members.set(random.sample(members, k=2))

            # Create Tasks
            for j in range(1, 6):
                Task.objects.create(
                    title=f"Task {j} for {project.name}",
                    project=project,
                    assignee=random.choice(members),
                    complexity=random.choice([1, 2, 3, 5]),
                    estimated_hours=random.randint(2, 20),
                    actual_hours=random.randint(2, 25)
                    if random.choice([True, False])
                    else None,
                    status=random.choice(["todo", "in_progress", "done"]),
                    due_date=date.today() + timedelta(days=random.randint(5, 20)),
                )

        self.stdout.write("Seeding complete.")
