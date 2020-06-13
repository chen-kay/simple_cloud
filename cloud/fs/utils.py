try:
    import ESL
except Exception:
    pass


def get_connection(ip, port, passwd):
    assert ESL, "No module named 'ESL'"
    con = ESL.ESLconnection(ip, port, passwd)
    if not con.connected():
        return None
    return con


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
