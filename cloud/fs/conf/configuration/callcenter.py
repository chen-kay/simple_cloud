from cloud.fs.conf.base import BaseXml
from cloud.fs.models import ServiceBackends as _backends
from cloud.fs.settings import fs_settings
from freeswitch.configuration import Section
from freeswitch.configuration.queue import Queue
from freeswitch.configuration.param import Param


class Callcenter(BaseXml):
    def generate_xml_conf(self, queue_name=None):
        queues = Section('queues')
        if queue_name:
            queue = Queue(name=queue_name)
            for name, value in self.params.items():
                queue.addParameter(name, value)
            queues.addVariable(queue)

        self.xml.addSection(queues)

    def get_xml_data(self):
        # self.generate_xml_base()
        name = self.request.data.get('CC-Queue', None)
        if name:
            if _backends.service_get_queue(name):
                return name
        self.generate_xml_conf()
        return None

    def generate_xml_base(self):
        settings = Section('settings')
        param = Param(
            "odbc-dsn",
            "pgsql://hostaddr=127.0.0.1 dbname=freeswitch user=aofeng password='aofeng_10086' options='-c client_min_messages=NOTICE' application_name='freeswitch3'"
        )
        settings.addVariable(param)

        self.xml.addSection(settings)

    @property
    def params(self):
        return {
            'strategy': 'random',  # 呼叫模式
            'moh-sound': '',  # $${hold_music}
            'record-template': fs_settings.DEFAULT_RECORDING_PATH +
            '/recording/${strftime(%Y)}/${strftime(%Y-%m)}/${strftime(%d)}/${caller_id_number}-${strftime(%Y%m%d-%H%M%S)}-${cc_agent}.mp3',
            'time-base-score': 'system',
            'max-wait-time': '16',
            'max-wait-time-with-no-agent': '16',
            'max-wait-time-with-no-agent-time-reached': '5',
            'tier-rules-apply': 'false',
            'tier-rule-wait-second': '300',
            'tier-rule-wait-multiply-level': 'true',
            'tier-rule-no-agent-no-wait': 'false',
            'discard-abandoned-after': '60',
            'abandoned-resume-allowed': 'false',
        }
