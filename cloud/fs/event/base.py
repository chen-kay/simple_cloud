import logging
import traceback

from cloud.fs.settings import fs_settings
from cloud.fs.utils import ESLConnException, get_connection

_DEFAULT_IP = fs_settings.DEFAULT_EVENT_IP
_DEFAULT_PORT = fs_settings.DEFAULT_EVENT_PORT
_DEFAULT_PWD = fs_settings.DEFAULT_EVENT_PASSWD

logger = logging.getLogger('logs')


class BaseEvent(object):
    def get_connection(self):
        try:
            print('FreeSWITCH Connecting  {0}:{1}....'.format(
                _DEFAULT_IP, _DEFAULT_PORT))
            conn = get_connection(_DEFAULT_IP, _DEFAULT_PORT, _DEFAULT_PWD)
            if conn.connected():
                print('FreeSWITCH is Connection!')
                return conn
            raise ESLConnException('FreeSWITCH Connection Error!')
        except ESLConnException as e:
            raise e
        except Exception:
            logger.error(traceback.format_exc())
            raise ESLConnException

    def send(self, msg, bgapi=False, conn=None):
        try:
            if conn:
                return self._send(conn, msg, bgapi=bgapi)
            conn = self.get_connection()
            return self._send(conn, msg, bgapi=bgapi)
        except ESLConnException:
            print('FreeSWITCH Connecting Error')
            return None, False
        except Exception as e:
            logger.error(traceback.format_exc(limit=None))
            raise e

    def _send(self, conn, msg, bgapi=False):
        last_msg = None
        if conn:
            res = None
            if isinstance(msg, list):
                res = []
                for item in msg:
                    last_msg = self.get_body(conn, item, bgapi=bgapi)
                    res.append((item, last_msg))
            else:
                last_msg = self.get_body(conn, msg, bgapi=bgapi)
                res = (msg, last_msg)
            return res, True if last_msg.find('+OK') >= 0 else False
        return None, False

    def get_body(self, conn, msg, bgapi=False):
        if bgapi:
            msg = 'bgapi {0}'.format(msg)
        e = conn.api(msg)
        return e.getBody()
