import time

from django.conf import settings


def asset_version(request):
    """Bust browser cache of CSS/JS while DEBUG is on."""
    return {"ASSET_V": int(time.time()) if settings.DEBUG else "1"}
