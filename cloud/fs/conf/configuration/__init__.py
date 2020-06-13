from cloud.fs.conf.base import BaseXml
from freeswitch.configuration import Configuration as _Configuration

from .acl import Acl
from .callcenter import Callcenter
from .event_socket import EventSocket
from .sofia import Sofia
from .xml_cdr import XmlCdr


class Configuration(BaseXml):
    acl = Acl
    event_socket = EventSocket
    xml_cdr = XmlCdr
    callcenter = Callcenter

    sofia = Sofia

    def __new__(cls, request):
        key_value = request.data['key_value']
        obj = getattr(cls, key_value.split('.')[0], None)
        print(key_value)
        if obj:
            _method = obj(request)
            _method.section = cls.section
            _method.xml = _Configuration(key_value)
            return _method
        return super().__new__(cls)

    def get_xml_data(self):
        return None
