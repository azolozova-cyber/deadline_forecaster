import io
import urllib
import base64
import matplotlib
import pandas as pd
from .models import Project

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def get_image_uri(fig):
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = "data:image/png;base64," + urllib.parse.quote(string)
    return uri


def generate_status_chart(project_id):
    project = Project.objects.get(id=project_id)
    tasks = project.tasks.all()

    if not tasks.exists():
        return None

    df = pd.DataFrame(list(tasks.values("status")))
    if df.empty:
        return None

    # Map status codes to display names
    status_map = dict(project.tasks.model.STATUS_CHOICES)
    df["status_display"] = df["status"].map(status_map)

    counts = df["status_display"].value_counts()

    fig, ax = plt.subplots(figsize=(6, 4))
    counts.plot(kind="pie", autopct="%1.1f%%", ax=ax, startangle=90, cmap="Pastel1")
    ax.set_ylabel("")
    ax.set_title(f"Task Statuses for {project.name}")

    return get_image_uri(fig)


def generate_workload_chart(project_id):
    """Generates a bar chart of estimated hours per team member."""
    project = Project.objects.get(id=project_id)
    tasks = project.tasks.all()
    if not tasks.exists():
        return None

    data = []
    for task in tasks:
        assignee = task.assignee.full_name if task.assignee else "Unassigned"
        hours = task.estimated_hours
        data.append({"assignee": assignee, "hours": hours})

    df = pd.DataFrame(data)
    if df.empty:
        return None

    workload = df.groupby("assignee")["hours"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(7, 4))
    workload.plot(kind="bar", ax=ax, color="coral")
    ax.set_title("Hit by Bus Risk: Workload Distribution")
    ax.set_ylabel("Total Estimated Hours")
    ax.set_xlabel("Team Member")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    return get_image_uri(fig)


def generate_backlog_chart(project_id):
    """
    Generates a line chart showing the cumulative growth of the project scope.
    This serves as a 'Backlog Growth Probability' visualizer.
    """
    project = Project.objects.get(id=project_id)
    tasks = project.tasks.all().order_by("created_at")

    if not tasks.exists():
        return None

    data = []
    for task in tasks:
        data.append({
            "date": task.created_at.date(),
            "scope": task.estimated_hours
        })

    df = pd.DataFrame(data)
    if df.empty:
        return None

    df["date"] = pd.to_datetime(df["date"])
    # Group by date and sum hours, then cumulative sum
    daily = df.groupby("date")["scope"].sum().cumsum()

    fig, ax = plt.subplots(figsize=(7, 4))
    daily.plot(ax=ax, kind="line", marker="o", color="purple", linestyle="--")

    ax.set_title("Backlog Growth (Scope Creep)")
    ax.set_ylabel("Cumulative Estimated Hours")
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    return get_image_uri(fig)


def calculate_bus_factor_alert(project_id):
    """
    Returns a string warning if the bus factor is critical.
    Bus Factor 1 means if 1 specific person leaves, the project stalls.
    """
    project = Project.objects.get(id=project_id)
    tasks = project.tasks.all()

    if not tasks.exists():
        return "No tasks to analyze."

    total_hours = sum(t.estimated_hours for t in tasks)
    if total_hours == 0:
        return "Total scope is 0 hours."

    metrics = {}
    for task in tasks:
        name = task.assignee.full_name if task.assignee else "Unassigned"
        metrics[name] = metrics.get(name, 0) + task.estimated_hours

    alerts = []
    # If any single person handles > 40% of total hours, that's a risk.
    for name, hours in metrics.items():
        share = hours / total_hours
        if share > 0.40:
            alerts.append(f"CRITICAL: {name} handles {share:.1%} of total workload.")

    if not alerts:
        return "Project load is well-distributed. Low 'Hit by Bus' risk."

    return " | ".join(alerts)
