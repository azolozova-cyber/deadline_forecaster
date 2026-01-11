from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, Task
from .forms import TaskForm
from .analytics import (
    generate_status_chart,
    generate_workload_chart,
    generate_backlog_chart,
    generate_status_dynamics_chart,
    generate_velocity_chart,
    generate_accuracy_scatter_chart,
    calculate_project_forecast,
    get_bus_factor_data,
)


def project_list(request):
    projects = Project.objects.all()
    return render(request, "forecaster/project_list.html", {"projects": projects})


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Analytics
    status_chart = generate_status_chart(pk)
    workload_chart = generate_workload_chart(pk)
    backlog_chart = generate_backlog_chart(pk)
    dynamics_chart = generate_status_dynamics_chart(pk)
    velocity_chart = generate_velocity_chart(pk)
    accuracy_chart = generate_accuracy_scatter_chart(pk)
    
    forecast = calculate_project_forecast(pk)
    bus_factor_data = get_bus_factor_data(pk)

    # Task Pagination
    task_list = project.tasks.all().order_by("-created_at")
    task_paginator = Paginator(task_list, 10)  # Show 10 tasks per page
    task_page_number = request.GET.get("page")
    task_page_obj = task_paginator.get_page(task_page_number)

    # Bus Factor Pagination
    bus_paginator = Paginator(bus_factor_data, 5)  # Show 5 members per page
    bus_page_number = request.GET.get("bus_page")
    bus_page_obj = bus_paginator.get_page(bus_page_number)

    return render(
        request,
        "forecaster/project_detail.html",
        {
            "project": project,
            "status_chart": status_chart,
            "workload_chart": workload_chart,
            "backlog_chart": backlog_chart,
            "dynamics_chart": dynamics_chart,
            "velocity_chart": velocity_chart,
            "accuracy_chart": accuracy_chart,
            "forecast": forecast,
            "bus_factor_data": bus_page_obj,
            "tasks": task_page_obj,
        },
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
