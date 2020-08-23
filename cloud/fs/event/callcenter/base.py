# from cloud.fs.event import base
from cloud.fs.event.esl import esl_event


class Callcenter(object):
    event = 'callcenter_config'

    def send(self, msg, *args, **kwargs):
        msg = '{0} {1}'.format(self.event, msg)
        return esl_event.send(msg, *args, **kwargs)
