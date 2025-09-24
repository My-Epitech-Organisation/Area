from django.urls import path
from . import views

urlpatterns = [
    path("healthz", views.healthz, name="healthz"),
    path("about.json", views.about_json, name="about_json"),
    path("api/areas", views.areas_list, name="areas_list"),
    path("api/areas/<uuid:area_id>", views.area_detail, name="area_detail"),
    path("api/areas/<uuid:area_id>/simulate", views.area_simulate, name="area_simulate"),
]
