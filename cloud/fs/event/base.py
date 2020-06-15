from cloud.fs.settings import fs_settings
from cloud.fs.utils import get_connection

_DEFAULT_IP = fs_settings.DEFAULT_EVENT_IP
_DEFAULT_PORT = fs_settings.DEFAULT_EVENT_PORT
_DEFAULT_PWD = fs_settings.DEFAULT_EVENT_PASSWD


class BaseEvent:
    def __init__(self):
        self.conn = self.__connection()

    def __connection(self):
        self.conn_error = None
        try:
            return get_connection(_DEFAULT_IP, _DEFAULT_PORT, _DEFAULT_PWD)
        except Exception as e:
            self.conn_error = str(e)
            return None

    def re_connection(self):
        self.conn = self.__connection()

    def send(self, msg, bgapi=False, *args, **kwargs):
        conn = self.conn
        last_msg = None
        if not conn:
            return 'get_connection(_, `{0}`, `{1}`) Error{2}'.format(
                _DEFAULT_PORT, _DEFAULT_PWD, self.conn_error), False
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
