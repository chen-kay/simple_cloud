import logging
import os
import traceback
from datetime import datetime
from urllib.parse import unquote

from django.db.models import F
from lxml import etree
from rest_framework.response import Response
from rest_framework.views import APIView

from cloud.fs.event.callcenter.agent import Agent
from cloud.fs.event.callcenter.queue import Queue
from cloud.fs.models import CallResult, DatumResult
from cloud.fs.models import ServiceBackends as _backends
from cloud.fs.redis import call, monitor

logger = logging.getLogger('logs')


class cdrHandle:
    agent = Agent()
    queue = Queue()

    def __init__(self, uuid, data):
        self.direction = ''
        self.result_id = None  # 资料id
        self.company_id = None  # 企业id
        self.project_id = None
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
            self.project_id = self.get_variables('sip_h_X-Proid', None)

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
            logger.error(traceback.format_exc())
            self.xml = None
        finally:
            if self.result_id and self.project_id:
                monitor.on_end(self.project_id, self.status)

    def generate_time(self):
        self.duration = self.get_variables('duration')
        self.billsec = self.get_variables('billsec')

        self.start_time = self.get_variables_date('start_epoch')
        self.answer_time = self.get_variables_date('answer_epoch')
        self.bridge_time = self.get_variables_date('bridge_epoch')
        self.end_time = self.get_variables_date('end_epoch')

    def generate_profile(self):
        self.caller_id_name = self.get_profile('caller_id_name')
        self.caller_id_number = self.get_profile('caller_id_number')
        self.callee_id_name = self.get_profile('callee_id_name')
        self.callee_id_number = self.get_profile('callee_id_number')

    def generate_inbound(self):
        username = self.get_variables('user_name')
        domain_name = self.get_variables('domain_name')
        self.user_name = '{0}@{1}'.format(username, domain_name)
        self.user = _backends.service_get_userid(self.user_name)
        print(self.user_name, self.user)

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
                # self.sign_out(self.user_name)
                self.user = _backends.service_get_userid(self.user_name)
                self.recording = self.get_unquote('cc_record_filename')
                self.status = 1
                self.callsec = 1
                if self.bridge_time:
                    diff = (self.end_time - self.bridge_time).seconds
                    self.callsec = diff if diff else 1
            if self.check_end():
                self.unload_queue(self.queue_name)

    def get_unquote(self, key):
        recording = self.get_variables(key)
        return unquote(recording, 'utf8') if recording else ''

    def save_cdr_data(self):
        pass

    def sign_out(self, username):
        '''坐席签出
        '''
        self.agent.sign_out(username)

    def check_end(self):
        if not self.project_id:
            return False
        ring = call.get_ring(self.project_id)
        answer = call.get_ring(self.project_id)
        queue = call.get_ring(self.project_id)
        if ring == 0 and answer == 0 and queue == 0:
            return True
        return False

    def unload_queue(self, queue_name):
        '''卸载项目
        '''
        self.queue.unload(queue_name)

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
        # 修改资料呼叫结果
        try:
            datum = DatumResult.objects.get(pk=self.result_id)

            self.save_callresult(datum)

            if datum.source != 1:
                datum.source = self.status
            datum.callsec = F('callsec') + self.callsec
            if self.status == 1:
                datum.callnum = F('callnum') + 1
            if self.user:
                datum.user_id = self.user
            datum.callrecord = self.recording
            datum.call_time = datetime.now()
            datum.save(update_fields=[
                'source', 'callrecord', 'callsec', 'callnum', 'user_id',
                'call_time'
            ])

        except Exception as e:
            logger.error(traceback.format_exc())
            raise e

    def save_callresult(self, datum):
        try:
            result = CallResult(
                pid_id=self.result_id,
                company_id=datum.company_id,
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
                project_id=datum.project_id,
                user_id=self.user,
                status=self.status,
                recording=self.recording,
                queue_name=self.queue_name,
                caller_id_name=self.caller_id_name,
                caller_id_number=self.caller_id_number,
                callee_id_name=self.callee_id_name,
                callee_id_number=self.callee_id_number,
            )
            result.save()
        except Exception as e:
            logger.error(traceback.format_exc())
            print(e)


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
            if handle.result_id and handle.project_id:
                handle.save_result()
        except Exception as e:
            logger.error(traceback.format_exc())
            print(e)
            saveLog(cdr, a_uuid)

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
