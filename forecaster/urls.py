from django.urls import path
from . import views

urlpatterns = [
    path("", views.project_list, name="project_list"),
    path("project/<int:pk>/", views.project_detail, name="project_detail"),
    path("project/<int:project_id>/task/add/", views.task_create, name="task_create"),
    path("task/<int:pk>/edit/", views.task_edit, name="task_edit"),
]
