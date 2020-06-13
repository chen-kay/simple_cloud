from cloud.fs.conf.base import BaseXml
from freeswitch.configuration import Section
from freeswitch.configuration.param import Param


class XmlCdr(BaseXml):
    def generate_xml_conf(self, data):
        section = Section('settings')
        for name, value in data:
            param = Param(name, value)
            section.addVariable(param)
        self.xml.addSection(section)

    def get_xml_data(self):
        return (
            ('url', '{0}{1}'.format(self.request.build_absolute_uri(), 'cdr')),
            ('log-dir', ''),
            ('log-b-leg', 'false'),
            ('prefix-a-leg', 'true'),
            ('encode', 'true'),
        )
