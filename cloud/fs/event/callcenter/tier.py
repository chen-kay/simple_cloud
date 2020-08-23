# from cloud.fs.event import base
from cloud.fs.event.esl import esl_event


class Tier(object):
    def get_list(self):
        """列表
        """
        msg = "callcenter_config tier list"
        return esl_event.send(msg)
