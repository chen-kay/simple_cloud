from cloud.fs.conf.base import BaseXml
from freeswitch.configuration import Section
from freeswitch.configuration.param import Param


class EventSocket(BaseXml):
    def generate_xml_conf(self, data):
        section = Section('settings')
        for name, value in data:
            param = Param(name, value)
            section.addVariable(param)
        self.xml.addSection(section)

    def get_xml_data(self):
        return (
            ('nat-map', False),
            ('listen-ip', '0.0.0.0'),
            ('listen-port', '8021'),
            ('apply-inbound-acl', 'wan.auto'),
            ('password', 'ClueCon'),
        )
