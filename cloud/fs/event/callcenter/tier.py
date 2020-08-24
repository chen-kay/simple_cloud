from cloud.fs.event.api import ApiEvent


class Tier(ApiEvent):
    def get_list(self):
        """列表
        """
        msg = "callcenter_config tier list"
        return self.send(msg)
