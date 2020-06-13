from cloud.fs.conf.base import BaseXml
from freeswitch.configuration import Section
from freeswitch.configuration.list import List
from freeswitch.configuration.node import Node


class Acl(BaseXml):
    def generate_xml_conf(self, data):
        section = Section('network-lists')
        for name, default, nodes in data:
            list_ = List(name=name, default=default)
            for perm, add in nodes:
                node = Node(perm, add)
                list_.addNode(node)
            section.addVariable(list_)
        self.xml.addSection(section)

    def get_xml_data(self):
        return ((
            'lan',
            'allow',
            (
                ('deny', '192.168.42.0/24'),
                ('allow', '192.168.42.42/32'),
            ),
        ), (
            'wan.auto',
            'allow',
            (('allow', '0.0.0.0/32'), ),
        ), (
            'loopback.auto',
            'allow',
            (('allow', '0.0.0.0/32'), ),
        ))
