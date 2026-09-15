from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.app, name="app"),
    re_path(r"^api/ontology/(?P<name>[\w-]+)\.json$", views.ontology_json, name="ontology_json"),
    re_path(r"^api/data/(?P<name>[\w-]+)\.json$", views.data_json, name="data_json"),
    re_path(r"^ontology/(?P<name>[\w-]+)\.json$", views.ontology_json, name="ontology_json_compat"),
    re_path(r"^data/(?P<name>[\w-]+)\.json$", views.data_json, name="data_json_compat"),
]
