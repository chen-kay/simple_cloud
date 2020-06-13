from .base import BaseXml
from .configuration import Configuration
from .dialplan import Dialplan
from .directory import Directory


class XmlConfig(BaseXml):
    directory = Directory
    dialplan = Dialplan
    configuration = Configuration

    def __new__(cls, request):
        section = request.data['section']
        obj = getattr(cls, section, None)
        if obj:
            obj.section = section
            return obj(request)
        return super().__new__(cls)
