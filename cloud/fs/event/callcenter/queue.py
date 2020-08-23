# from cloud.fs.event import base
from cloud.fs.event.esl import esl_event


class Queue(object):
    def load(self, queue_name):
        '''加载
        '''
        msg = "callcenter_config queue load {0}".format(queue_name)
        return esl_event.send(msg)

    def unload(self, queue_name):
        '''卸载
        '''
        msg = "callcenter_config queue unload {0}".format(queue_name)
        return esl_event.send(msg)