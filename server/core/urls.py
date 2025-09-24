from django.urls import path
from . import views

urlpatterns = [
    path("healthz", views.healthz, name="healthz"),
    path("about.json", views.about_json, name="about_json"),
]
