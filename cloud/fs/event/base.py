from cloud.fs.settings import fs_settings
from cloud.fs.utils import get_connection

_DEFAULT_IP = fs_settings.DEFAULT_EVENT_IP
_DEFAULT_PORT = fs_settings.DEFAULT_EVENT_PORT
_DEFAULT_PWD = fs_settings.DEFAULT_EVENT_PASSWD


class BaseEvent:
    cache_conn = '__cache_conn'

    @property
    def conn(self):
        return self.get_connection()

    def get_connection(self):
        cache = self.cache_conn
        conn = getattr(self, cache, None)
        if not conn:
            setattr(self, cache, self._get_connection())
        return getattr(self, cache)

    def _get_connection(self):
        try:
            print('FreeSWITCH Connecting....')
            return get_connection(_DEFAULT_IP, _DEFAULT_PORT, _DEFAULT_PWD)
        except Exception as e:
            print(e)
            return None

    def send(self, msg, bgapi=False, *args, **kwargs):
        conn = self.conn
        last_msg = None
        if not conn:
            return 'get_connection(_, `{0}`, `{1}`) Error'.format(
                _DEFAULT_PORT, _DEFAULT_PWD), False
        try:
            if conn.connected():
                res = None
                if isinstance(msg, list):
                    res = []
                    for item in msg:
                        last_msg = self._send_msg(item)
                        res.append((item, last_msg))
                else:
                    last_msg = self._send_msg(msg)
                    res = (msg, last_msg)
                return res, True if last_msg.find('+OK') >= 0 else False
            return None, False
        except Exception as e:
            return str(e), False

    def _send_msg(self, msg):
        e = self.conn.api(msg)
        return e.getBody()
