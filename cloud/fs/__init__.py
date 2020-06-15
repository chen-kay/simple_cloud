'''
'''
from django.core.exceptions import ImproperlyConfigured

from cloud.fs.settings import fs_settings


def _get_backends():
    backends = []
    for backend in fs_settings.DEFAULT_SERVICE_BACKENDS:
        backends.append(backend())
    if not backends:
        raise ImproperlyConfigured(
            'No authentication backends have been defined. Does '
            'DEFAULT_SERVICE_BACKENDS contain anything?')
    return backends


def get_backends():
    return _get_backends()


default_app_config = 'cloud.fs.apps.FsConfig'