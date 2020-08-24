from django.conf import settings
from django.test.signals import setting_changed
from django.utils.module_loading import import_string

DEFAULTS = {
    'DEFAULT_EXPIRED_TIME': 300,
    'DEFAULT_AUTO_CALL_RATE': 50,
    'DEFAULT_SERVICE_BACKENDS': ['cloud.fs.backends.ServiceBackend'],
    'DEFAULT_RECORDING_PATH': '/home',
    'DEFAULT_EXTERNAL_SIP_PORT': '14060',
    'DEFAULT_EXT_RTP_IP': '192.168.10.82',
    'DEFAULT_EXT_SIP_IP': '192.168.10.82',
    'DEFAULT_INTERNAL_SIP_PORT': '14080',
    'DEFAULT_WS_BINDING': ':14066',
    'DEFAULT_WSS_BINDING': ':16443',
    'DEFAULT_LISTEN_PORT': '8021',
    'DEFAULT_EVENT_IP': '192.168.10.82',
    'DEFAULT_EVENT_PORT': '8021',
    'DEFAULT_EVENT_PASSWD': 'ClueCon',
    'DEFAULT_GATEWAY_NAME': 'system',
    'DEFAULT_GATEWAY': {
        'realm': '192.168.10.125:5060',
        'caller-id-in-from': True,
        'from-user': '',
        'from-domain': '',
        'register': False,
    }
}

IMPORT_STRINGS = [
    'DEFAULT_SERVICE_BACKENDS',
]


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import '%s' for API setting '%s'. %s: %s." % (
            val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class APISettings:
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        if user_settings:
            self._user_settings = self.__check_user_settings(user_settings)
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'FS_FRAMEWORK', {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def __check_user_settings(self, user_settings):
        return user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')


fs_settings = APISettings(None, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*args, **kwargs):
    setting = kwargs['setting']
    if setting == 'FS_FRAMEWORK':
        fs_settings.reload()


setting_changed.connect(reload_api_settings)
