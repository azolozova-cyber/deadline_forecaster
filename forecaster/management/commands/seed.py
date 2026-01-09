from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forecaster.models import Project, TeamMember, Task, TaskStatusLog
from datetime import date, timedelta, datetime
import random
import pytz


class Command(BaseCommand):
    help = "Seeds the database with initial data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # Clear existing data to prevent weird graphs
        TaskStatusLog.objects.all().delete()
        Task.objects.all().delete()
        Project.objects.all().delete()
        TeamMember.objects.all().delete()
        
        # Create Superuser
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
            self.stdout.write("Created superuser: admin/admin")

        user = User.objects.get(username="admin")

        # Create members
        members = []
        roles = ["backend", "frontend", "qa", "manager", "designer"]
        names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi"]
        for name, role in zip(names, roles * 2):
            member, created = TeamMember.objects.get_or_create(
                full_name=name, 
                defaults={"role": role, "hourly_rate": random.randint(30, 80)}
            )
            members.append(member)

        # Create Projects
        for i in range(1, 4):
            # Spread start dates back in time
            start_date = date.today() - timedelta(days=random.randint(60, 120))
            project = Project.objects.create(
                name=f"Project {i} - {'Alpha' if i==1 else 'Beta' if i==2 else 'Gamma'}",
                description=f"Complex development project #{i} focusing on scalable architecture.",
                start_date=start_date,
                deadline=date.today() + timedelta(days=30),
                owner=user,
            )

            # Add members
            project.members.set(random.sample(members, k=4))

            # Create Tasks with History
            # We want around 30 tasks per project
            num_tasks = 30
            
            for j in range(1, num_tasks + 1):
                # Random creation date between project start and now
                days_since_start = (date.today() - start_date).days
                creation_delta = random.randint(0, days_since_start - 5)
                creation_date = start_date + timedelta(days=creation_delta)
                creation_dt = datetime.combine(creation_date, datetime.min.time()).replace(tzinfo=pytz.UTC)

                complexity = random.choice([1, 2, 3, 5, 8])
                estimated = complexity * random.randint(2, 6)
                
                # Determine final status
                final_status = random.choices(
                    ["todo", "in_progress", "done"], 
                    weights=[30, 40, 30], 
                    k=1
                )[0]

                assignee = random.choice(members) if final_status != "todo" or random.random() > 0.5 else None

                task = Task.objects.create(
                    title=f"Task {j}: {random.choice(['Implement', 'Fix', 'Design', 'Refactor'])} feature X",
                    project=project,
                    assignee=assignee,
                    complexity=complexity,
                    estimated_hours=estimated,
                    actual_hours=int(estimated * random.uniform(0.8, 1.5)) if final_status == "done" else None,
                    status=final_status,
                    due_date=creation_date + timedelta(days=random.randint(5, 14)),
                )
                
                # Hack to set created_at (auto_now_add usually prevents this)
                task.created_at = creation_dt
                task.save()

                # Generate logs
                # 1. Created (Todo)
                TaskStatusLog.objects.create(
                    task=task,
                    old_status=None,
                    new_status="todo",
                    timestamp=creation_dt
                )

                # 2. If moved to In Progress
                if final_status in ["in_progress", "done"]:
                    move_inprogress_date = creation_date + timedelta(days=random.randint(1, 3))
                    move_inprogress_dt = datetime.combine(move_inprogress_date, datetime.min.time()).replace(tzinfo=pytz.UTC)
                    
                    # Ensure log isn't in future
                    if move_inprogress_dt > datetime.now(pytz.UTC):
                         move_inprogress_dt = datetime.now(pytz.UTC)

                    TaskStatusLog.objects.create(
                        task=task,
                        old_status="todo",
                        new_status="in_progress",
                        timestamp=move_inprogress_dt
                    )
                
                # 3. If moved to Done
                if final_status == "done":
                    move_done_date = creation_date + timedelta(days=random.randint(4, 10))
                    move_done_dt = datetime.combine(move_done_date, datetime.min.time()).replace(tzinfo=pytz.UTC)

                    if move_done_dt > datetime.now(pytz.UTC):
                         move_done_dt = datetime.now(pytz.UTC)

                    TaskStatusLog.objects.create(
                        task=task,
                        old_status="in_progress",
                        new_status="done",
                        timestamp=move_done_dt
                    )

        self.stdout.write("Seeding complete with historical data.")
