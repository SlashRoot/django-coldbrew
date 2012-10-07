from django.conf.global_settings import *
import os
import sys


STATIC_ROOT = MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')
COFFEESCRIPT_LOCATION = STATIC_ROOT

INSTALLED_APPS = (
    "coldbrew",
)
COFFEESCRIPT_MTIME_DELAY = 2
COFFEESCRIPT_OUTPUT_DIR = "COFFEESCRIPT_CACHE"

DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME':'notreal',
            }
        }
        
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        'coffeescript': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

from coldbrew.settings import *