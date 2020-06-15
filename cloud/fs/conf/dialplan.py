from cloud.fs.models import ServiceBackends as _backends
from cloud.fs.settings import fs_settings
from freeswitch.dialplan.condition import Condition
from freeswitch.dialplan.context import Context

from .base import BaseXml


class Dialplan(BaseXml):
    def __init__(self, request):
        super().__init__(request)
        self.context = self.request.data.get('Caller-Context', 'default')

    def generate_xml_conf(self, data):
        context = self.context
        self.xml = Context(context)
        for extension, continue_, conds in data:
            ext = self.xml.addExtension(extension, continue_)
            for field, exp, cont, acts in conds:
                cond = Condition(attr=field, val=exp)
                for act, val, inline in acts:
                    cond.addAction(act, val)
                ext.addCondition(cond)

    def get_xml_data(self):
        '''
        context: 企业域名
        direction: 呼叫方向
            inbound. 呼出
            outbound: 呼入
        dest: 被叫号码

        header
        '''
        context = self.request.data.get('Caller-Context', None)
        if context == 'default':
            return self.hangup(context)
        direction = self.request.data.get('Call-Direction', None)
        dest = self.request.data.get('Caller-Destination-Number', None)

        phoneId = self.request.data.get('variable_sip_h_X-Phoneid', None)

        caller = context
        if direction == 'inbound':
            domain = self.request.data.get('variable_domain_name', None)
            if domain != context:
                return self.hangup(context)
            gateway = _backends.service_get_gateway_name(context)  # 获取企业配置网关
            if not gateway:
                gateway = fs_settings.DEFAULT_GATEWAY_NAME
            if phoneId:
                dest, proId = _backends.service_get_mobile(phoneId)  # 获取真实被叫
                caller = '{0}_{1}'.format(context, proId)  # 设置主叫为 域名 + 业务id
            if not dest:
                return self.hangup(context)
            return [
                (
                    'sys_inbound',
                    False,
                    [(
                        'destination_number',
                        '^(.*)$',
                        False,
                        [
                            ('set', 'RECORD_STEREO=true', False),
                            ('set', 'RECORD_ANSWER_REQ=true', False),
                            ('set', 'media_bug_answer_req=true', False),
                            ('set', 'recording={0}'.format(self.record_path),
                             False),
                            ('set',
                             'execute_on_answer1=record_session ${recording}',
                             False),
                            ('set',
                             'effective_caller_id_number={0}'.format(caller),
                             False),
                            ('bridge',
                             'sofia/gateway/{0}/{1}'.format(gateway,
                                                            dest), False),
                            # ('bridge', 'user/1000@system', False),
                        ])]),
            ]
        elif direction == 'outbound':
            if self.request.data.get('Channel-Call-State', 'EARLY') != 'EARLY':
                return [('sys_callcenter', False,
                         [('destination_number', '^(.*)$', False, [
                             ('callcenter', '${destination_number}', False),
                         ])])]
            if not _backends.get_service_queue(dest):
                return self.hangup(context)
            return [('sys_callcenter', False, [
                ('destination_number', '^(.*)$', False, [
                    ('set',
                     'execute_on_answer1=Transfer ${destination_number} XML %s'
                     % context, False),
                    ('set', 'park_timeout=30', False),
                    ('park', '', False),
                ]),
            ])]
        return self.hangup()

    def hangup(self, context):
        return [
            ('context', False, [('destination_number', '^(.*)$', False, [
                ('hangup', None, False),
            ])]),
        ]

    @property
    def record_path(self):
        return fs_settings.DEFAULT_RECORDING_PATH + '/recording/${strftime(%Y)}/${strftime(%Y-%m)}/${strftime(%d)}/${caller_id_number}_${strftime(%Y%m%d-%H%M%S)}_${destination_number}.mp3'
