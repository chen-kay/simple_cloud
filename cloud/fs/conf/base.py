import time

from freeswitch import XMLCurlFactory


class BaseXml(object):
    xml = None
    section = None

    def __init__(self, request, *args, **kwargs):
        self.request = request

    def render_xml(self):
        data = self.get_xml_data()
        if data:
            self.generate_xml_conf(data)

    def generate_xml_conf(self, data):
        raise NotImplementedError('`generate_xml_conf()` must be implemented.')

    def get_xml_data(self):
        raise NotImplementedError('`get_xml_data()` must be implemented.')

    def to_xml(self):
        xml = XMLCurlFactory(data=self.data, section=self.section)
        return xml.convert()

    @property
    def data(self):
        return self.xml.todict() if self.xml else None


# 计算时间函数
def print_run_time(func):
    def wrapper(*args, **kw):
        local_time = time.time()
        res = func(*args, **kw)
        print('current Function [%s] run time is %.2f' %
              (func.__name__, time.time() - local_time))
        return res

    return wrapper
