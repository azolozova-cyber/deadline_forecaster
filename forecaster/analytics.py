import io
import urllib
import base64
import matplotlib
import pandas as pd
from .models import Project

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


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

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = "data:image/png;base64," + urllib.parse.quote(string)
    return uri
