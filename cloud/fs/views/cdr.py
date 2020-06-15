import os
from datetime import datetime
from urllib.parse import unquote

from lxml import etree
from rest_framework.response import Response
from rest_framework.views import APIView

from cloud.fs.event.callcenter.agent import Agent
from cloud.fs.models import CallResult
from cloud.fs.models import ServiceBackends as _backends


class cdrHandle:
    def __init__(self, uuid, data):
        self.direction = ''
        self.result_id = None  # 资料id
        self.mobile = ''  # 被叫号码
        self.duration = 0  # 接通时长
        self.billsec = 0  # 通话时长
        self.callsec = 0  # 通话时长
        self.start_time = None  # 发起呼叫时间
        self.answer_time = None  # 接通时间
        self.bridge_time = None  # 转坐席时间
        self.end_time = None  # 挂机时间
        self.hangup_cause = ''  # 挂机原因
        self.hangup_source = ''  # 挂机方
        self.user = None  # 接线坐席id
        self.status = 2  # 通话结果状态
        self.recording = ''  # 录音
        self.queue_name = ''  # 队列
        self.caller_id_name = ''
        self.caller_id_number = ''
        self.callee_id_name = ''
        self.callee_id_number = ''

        self.user_name = None
        try:
            self.xml = etree.XML(data)

            self.variables = self.xml.find('variables')
            self.callflow = self.xml.find('callflow')
            self.caller_profile = self.callflow.find('caller_profile')

            self.result_id = self.get_variables('sip_h_X-Phoneid', None)

            self.direction = self.get_variables('direction')

            self.generate_time()

            self.hangup_cause = self.get_variables('hangup_cause')
            self.hangup_source = self.get_hangup_source()

            if self.direction == 'inbound':
                '''手动外呼
                '''
                self.generate_inbound()
            elif self.direction == 'outbound':
                self.generate_outbound()

            self.generate_profile()
        except Exception as e:
            print(e)
            self.xml = None

    def generate_time(self):
        self.duration = self.get_variables('duration')
        self.billsec = self.get_variables('billsec')

        self.start_time = self.get_variables_date('start_epoch')
        self.answer_time = self.get_variables_date('answer_epoch')
        self.bridge_time = self.get_variables_date('bridge_epoch')
        self.end_time = self.get_variables_date('end_epoch')

    def generate_profile(self):
        self.caller_id_name = self.get_profile('caller_id_name')
        print(self.caller_id_name)
        self.caller_id_number = self.get_profile('caller_id_number')
        self.callee_id_name = self.get_profile('callee_id_name')
        self.callee_id_number = self.get_profile('callee_id_number')

    def generate_inbound(self):
        username = self.get_variables('user_name')
        domain_name = self.get_variables('domain_name')
        self.user_name = '{0}@{1}'.format(username, domain_name)
        self.user = _backends.service_get_userid(self.user_name)

        if self.answer_time:
            self.status = 1
            self.recording = self.get_unquote('recording')
            diff = (self.end_time - self.answer_time).seconds
            self.callsec = diff if diff else 1

    def generate_outbound(self):
        self.queue_name = self.get_variables('cc_queue')
        if self.queue_name:
            self.status = 3
            self.user_name = self.get_unquote('cc_agent')
            if self.user_name:
                self.sign_out(self.user_name)
                self.user = _backends.service_get_userid(self.user_name)
                self.recording = self.get_unquote('cc_record_filename')
                self.status = 1
                self.callsec = 1
                if self.bridge_time:
                    diff = (self.end_time - self.bridge_time).seconds
                    self.callsec = diff if diff else 1

    def get_unquote(self, key):
        recording = self.get_variables(key)
        return unquote(recording, 'utf8') if recording else ''

    def save_cdr_data(self):
        pass

    def sign_out(self, username):
        '''坐席签出
        '''
        Agent().sign_out(username)

    def get_hangup_source(self):
        hangup_source = ''
        sip_hangup_disposition = self.get_variables('sip_hangup_disposition')
        if sip_hangup_disposition == 'recv_bye':
            hangup_source = '被叫挂断'
        elif sip_hangup_disposition == 'send_cancel':
            hangup_source = '主叫取消'
        elif sip_hangup_disposition == 'recv_refuse':
            hangup_source = '被叫拒绝'
        elif sip_hangup_disposition == 'send_bye':
            hangup_source = '主叫挂断'
        return hangup_source

    def get_profile(self, key, default=''):
        val = self.caller_profile.find(key)
        if val is not None and val.text:
            return val.text
        return default

    def get_variables(self, key, default=''):
        val = self.variables.find(key)
        if val is not None and val.text:
            return val.text
        return default

    def get_variables_date(self, key, default='0'):
        value = self.get_variables(key, default=default)
        if not value or value == '0':
            return None
        return datetime.fromtimestamp(int(value))

    def save_result(self):
        result = CallResult(
            result_id=self.result_id,
            mobile=self.mobile,
            direction=self.direction,
            duration=self.duration,
            billsec=self.billsec,
            callsec=self.callsec,
            start_time=self.start_time,
            answer_time=self.answer_time,
            bridge_time=self.bridge_time,
            end_time=self.end_time,
            hangup_cause=self.hangup_cause,
            hangup_source=self.hangup_source,
            user=self.user,
            status=self.status,
            recording=self.recording,
            queue_name=self.queue_name,
            caller_id_name=self.caller_id_name,
            caller_id_number=self.caller_id_number,
            callee_id_name=self.callee_id_name,
            callee_id_number=self.callee_id_number,
        )
        result.save()


class CdrViews(APIView):
    '''话单处理
    '''
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        a_uuid = request.GET.get('uuid')
        cdr = request.data.get('cdr', None)
        try:
            handle = cdrHandle(a_uuid, cdr)
            if handle.result_id:
                handle.save_result()
        except Exception as e:
            print(e)
            saveLog(cdr, a_uuid)

        # 修改资料呼叫结果
        # datum = Datum.objects.get(pk=handle.result_id)
        # datum.status = handle.status
        # datum.recording = handle.recording
        # datum.user = handle.user
        # datum.save(update_fields=['status', 'recording', 'user'])
        return Response()


def saveLog(cdr, a_uuid):
    nowdate = datetime.now()
    path = 'cdr/tempcdr/{0}-{1}/{2}/'.format(nowdate.year, nowdate.month,
                                             nowdate.day)
    if not os.path.exists(path):
        os.makedirs(path)
    f1 = open(path + a_uuid + '.xml', 'w')
    f1.write(cdr)
    f1.close()
