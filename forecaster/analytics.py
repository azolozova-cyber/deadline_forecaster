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


def generate_status_dynamics_chart(project_id):
    """
    Generates a stacked area chart (ribbon chart) showing the number of tasks
    in each status (Todo, In Progress, Done) over time.
    """
    project = Project.objects.get(id=project_id)
    # Fetch all logs for this project's tasks, ordered by time
    logs = pd.DataFrame(
        list(
            project.tasks.model.status_logs.field.model.objects.filter(
                task__project=project
            ).values("task_id", "new_status", "timestamp")
        )
    )

    if logs.empty:
        return None

    logs["timestamp"] = pd.to_datetime(logs["timestamp"])
    # Ensure logs are TZ-aware (UTC) to match consistent comparison
    if logs["timestamp"].dt.tz is None:
        logs["timestamp"] = logs["timestamp"].dt.tz_localize("UTC")
    else:
        logs["timestamp"] = logs["timestamp"].dt.tz_convert("UTC")

    logs = logs.sort_values("timestamp")

    # Get date range: from first log to today
    # Normalize start_date and make it UTC
    start_date = logs["timestamp"].min().normalize()
    
    # Get current time in UTC and normalize
    end_date = pd.Timestamp.now(tz="UTC").normalize()
    
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")

    # Reconstruct state for each day
    # We will iterate through days and snapshot the status of all tasks
    
    # Track current status of each task: {task_id: status}
    task_status_state = {}
    
    # Result storage
    history = []

    # Pointer for logs
    log_idx = 0
    total_logs = len(logs)

    for single_date in date_range:
        # Move forward in logs until we pass the current single_date (end of day)
        day_end = single_date + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        
        while log_idx < total_logs and logs.iloc[log_idx]["timestamp"] <= day_end:
            row = logs.iloc[log_idx]
            task_status_state[row["task_id"]] = row["new_status"]
            log_idx += 1
        
        # Snapshot
        counts = {"todo": 0, "in_progress": 0, "done": 0}
        for status in task_status_state.values():
            if status in counts:
                counts[status] += 1
        
        counts["date"] = single_date
        history.append(counts)

    df_hist = pd.DataFrame(history)
    df_hist = df_hist.set_index("date")

    if df_hist.empty:
        return None

    # Plotting
    fig, ax = plt.subplots(figsize=(8, 5))
    
    dates = df_hist.index
    todo = df_hist["todo"]
    in_progress = df_hist["in_progress"]
    done = df_hist["done"]

    # Stackplot
    ax.stackplot(dates, todo, in_progress, done, 
                 labels=["To Do", "In Progress", "Done"],
                 colors=["#cbd5e1", "#60a5fa", "#4ade80"], 
                 alpha=0.8)

    ax.set_title("Project Dynamics: Task Status Evolution")
    ax.set_ylabel("Number of Tasks")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    return get_image_uri(fig)
