from django.urls import path

from . import views

app_name = "schedules"

urlpatterns = [
    path("", views.weekly_schedule, name="weekly"),
    path("healthz/", views.health, name="health"),
    path("class/add/", views.class_create, name="class_create"),
    path("class/<int:pk>/edit/", views.class_edit, name="class_edit"),
    path("class/<int:pk>/delete/", views.class_delete, name="class_delete"),
]
