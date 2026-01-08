from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, Task
from .forms import TaskForm
from .analytics import generate_status_chart


def project_list(request):
    projects = Project.objects.all()
    return render(request, "forecaster/project_list.html", {"projects": projects})


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    chart = generate_status_chart(pk)
    return render(
        request, "forecaster/project_detail.html", {"project": project, "chart": chart}
    )


def task_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            return redirect("project_detail", pk=project.pk)
    else:
        form = TaskForm()
    return render(
        request, "forecaster/task_form.html", {"form": form, "project_id": project.pk}
    )


def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            return redirect("project_detail", pk=task.project.pk)
    else:
        form = TaskForm(instance=task)
    return render(
        request,
        "forecaster/task_form.html",
        {"form": form, "project_id": task.project.pk},
    )
