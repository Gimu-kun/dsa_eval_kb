import json

from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import render

ONTOLOGY_FILES = {
    "concepts",
    "hierarchy",
    "instances",
    "relations",
    "assertions",
    "rules",
    "operands",
    "functions",
}
DATA_FILES = {
    "instances",
    "assertions",
    "operands",
}


def app(request):
    return render(request, "kb/app.html")


def _json_file(directory, name, allowed):
    if name not in allowed:
        raise Http404("Unknown JSON resource")
    path = directory / f"{name}.json"
    if not path.is_file():
        raise Http404("JSON file not found")
    with path.open(encoding="utf-8") as fh:
        payload = json.load(fh)
    response = JsonResponse(payload, json_dumps_params={"ensure_ascii": False})
    response["Cache-Control"] = "no-store"
    return response


def ontology_json(request, name):
    return _json_file(settings.ONTOLOGY_DIR, name, ONTOLOGY_FILES)


def data_json(request, name):
    return _json_file(settings.DATA_DIR, name, DATA_FILES)
