from cloud.fs.event import base


class Tier(base.BaseEvent):
    def get_list(self):
        """列表
        """
        msg = "callcenter_config tier list"
        return self.send(msg)
