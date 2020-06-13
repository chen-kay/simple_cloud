from cloud.fs.conf.base import BaseXml
from cloud.fs.models import service_get_queue
from freeswitch.configuration import Section
from freeswitch.configuration.queue import Queue
from cloud.fs.settings import fs_settings


class Callcenter(BaseXml):
    def generate_xml_conf(self, data):
        queues = Section('queues')
        for row in data:
            queue_name = row.get('queue_name', None)
            queue = Queue(name=queue_name)
            for name, value in self.params.items():
                queue.addParameter(name, value)
            queues.addVariable(queue)
        self.xml.addSection(queues)

    def get_xml_data(self):
        print(self.request.data)
        name = self.request.data.get('CC-Queue', None)
        if name:
            return service_get_queue(name)
        return None

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
