from django.shortcuts import render, get_object_or_404
from .models import Project
from .analytics import generate_status_chart

def project_list(request):
    projects = Project.objects.all()
    return render(request, 'forecaster/project_list.html', {'projects': projects})

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    chart = generate_status_chart(pk)
    return render(request, 'forecaster/project_detail.html', {'project': project, 'chart': chart})