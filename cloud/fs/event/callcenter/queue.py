from cloud.fs.event.api import ApiEvent


class Queue(ApiEvent):
    def load(self, queue_name):
        '''加载
        '''
        msg = "bgapi callcenter_config queue load {0}".format(queue_name)
        return self.send(msg)

    def unload(self, queue_name):
        '''卸载
        '''
        msg = "bgapi callcenter_config queue unload {0}".format(queue_name)
        return self.send(msg)