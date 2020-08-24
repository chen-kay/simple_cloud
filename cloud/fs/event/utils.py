from cloud.fs.event.api import ApiEvent
from cloud.fs.settings import fs_settings
from cloud.fs.utils import encrypt_mobile


class Utils(ApiEvent):
    def originate_queue_test(self,
                             mobile,
                             queue_name,
                             domain,
                             caller='',
                             phoneId='',
                             project_id='',
                             gateway=None):
        '''呼叫
        mobile: 坐席回显的号码
        queue_name: 外呼队列
        domain: 域名
        caller: 送达vos主叫
        phoneId: 呼叫号码id
        gateway: 外呼使用网关
        '''
        if not gateway:
            gateway = fs_settings.DEFAULT_GATEWAY_NAME
        msg = """bgapi originate {{sip_h_X-Phoneid={phoneId},sip_h_X-Proid={project_id},sip_h_X-Protype=1,cc_export_vars=sip_h_X-Phoneid,origination_caller_id_number={caller},effective_caller_id_number={encrypt},call_timeout=30,agent_timeout=5,originate_timeout=30}}sofia/gateway/{gateway}/{mobile} {queue_name} XML {domain}""".format( # noqa
            **{
                'phoneId': phoneId,
                'project_id': project_id,
                'caller': caller,
                'mobile': mobile,
                'encrypt': encrypt_mobile(mobile),
                'gateway': gateway,
                'queue_name': queue_name,
                'domain': domain,
            })
        return self.send(msg)
