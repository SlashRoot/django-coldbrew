from django.conf import settings
import os


POSIX_COMPATIBLE = True if os.name == 'posix' else False
COFFEESCRIPT_EXECUTABLE = getattr(settings, "COFFEESCRIPT_EXECUTABLE", "coffee")
COFFEESCRIPT_USE_CACHE = getattr(settings, "COFFEESCRIPT_USE_CACHE", True)
COFFEESCRIPT_CACHE_TIMEOUT = getattr(settings, "COFFEESCRIPT_CACHE_TIMEOUT", 60 * 60 * 24 * 30) # 30 days
COFFEESCRIPT_MTIME_DELAY = getattr(settings, "COFFEESCRIPT_MTIME_DELAY", 10) # 10 seconds
COFFEESCRIPT_OUTPUT_DIR = getattr(settings, "COFFEESCRIPT_OUTPUT_DIR", "COFFEESCRIPT_CACHE")

COLDBREW_FAIL_LOUD = getattr(settings, 'COLDBREW_FAIL_LOUD', settings.DEBUG)

try:
    COFFEESCRIPT_LOCATION = settings.COFFEESCRIPT_LOCATION
except AttributeError:
    try:
        COFFEESCRIPT_LOCATION = settings.STATIC_ROOT
    except AttributeError:
        COFFEESCRIPT_LOCATION = settings.MEDIA_ROOT

if not COFFEESCRIPT_LOCATION:
    raise RuntimeError('In order to use django-coffeescript, you must specify either COFFEESCRIPT_LOCATION, STATIC_ROOT, or MEDIA_ROOT in settings')