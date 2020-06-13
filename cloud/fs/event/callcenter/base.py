from cloud.fs.event import base


class Callcenter(base.BaseEvent):
    event = 'callcenter_config'

    def send(self, msg, *args, **kwargs):
        msg = '{0} {1}'.format(self.event, msg)
        return super().send(msg, *args, **kwargs)
