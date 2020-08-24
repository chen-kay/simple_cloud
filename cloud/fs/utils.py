import logging
import traceback

try:
    import ESL
except Exception:
    pass

logger = logging.getLogger('logs')


class ESLConnException(Exception):
    pass


def get_connection(ip, port, passwd):
    try:
        assert ESL, "No module named 'ESL'"
        con = ESL.ESLconnection(ip, port, passwd)
        return con
    except Exception:
        logger.error(traceback.format_exc(limit=None))
        raise ESLConnException()


def encrypt_mobile(mobile):
    '''号码脱敏
    '''
    if type(mobile) != str:
        if type(mobile) == int:
            mobile = str(mobile)
        else:
            return mobile
    return (mobile[0:3] + '****' +
            mobile[len(mobile) - 4:]) if len(mobile) > 7 else mobile
