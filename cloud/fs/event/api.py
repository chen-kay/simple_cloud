from cloud.fs.event.base import BaseEvent


class ApiEvent(object):
    def __init__(self):
        self.event = BaseEvent()

    def send(self, msg, bgapi=False):
        return self.event.send(msg, bgapi=bgapi)
