import math
from queue import Queue

from cloud.fs.settings import fs_settings

from .models import Datum, Domain, Gateway, Project, User

datum_queue = Queue()


class ServiceBackend:
    user = User
    gateway = Gateway
    project = Project
    domain = Domain
    datum = Datum

    def get_service_domain(self):
        '''获取系统企业标识
        return: [{'name':''}]
        '''
        return self.domain.objects.all().values('name')

    def get_service_gateway(self, domain=None):
        '''获取系统服务网关 - 系统落地网关
        '''
        if domain:
            try:
                gw = self.gateway.objects.get(domain=domain)
                return gw.to_dict()
            except Exception:
                return None
        return [r.to_dict() for r in self.gateway.objects.all()]

    def get_service_directory(self, username):
        '''获取系统用户 - 可注册电话
        '''
        try:
            user, domain = username.split('@')
            ins = self.user.objects.get(username=user, domain__name=domain)
            return ins.to_dict()
        except Exception as e:
            print(e)
            return None

    def get_service_project(self, project_id):
        '''获取系统项目业务 - 系统自动外呼队列
        '''
        try:
            ins = self.project.objects.get(id=project_id)
            return ins.to_dict()
        except Exception as e:
            print(e)
            return None

    def get_service_mobile(self, mobile_id):
        '''获取呼叫号码
        '''
        try:
            ins = self.datum.objects.get(pk=mobile_id)
            return (ins.mobile, ins.project.id)
        except Exception as e:
            print(e)
            return None, None

    def get_compute_nums(self, project_id, callmax=0, ratio=0):
        '''计算当前外呼数量
        '''
        ring = 0
        queue = 0
        answer = 0
        free = 0
        return self._compute_call_nums(ring=ring,
                                       queue=queue,
                                       answer=answer,
                                       free=free,
                                       callmax=callmax,
                                       ratio=ratio)

    def get_extract_datum(self, project_id):
        '''提取项目资料 -> 用于自动外呼执行呼叫
        '''
        if datum_queue.empty():
            for r in self.datum.objects.filter(project=project_id):
                datum_queue.put((r.id, r.mobile))
        try:
            return datum_queue.get_nowait()
        except KeyError:
            return None

    def change_datum_result(self,
                            phoneId,
                            status=2,
                            callsec=0,
                            recording=None):
        '''修改资料呼叫结果
        phoneId: 资料id
        status: 呼叫结果 1.接通 2.未接通 3.呼损
        callsec: 坐席通话时长
        recording: 录音文件地址
        '''
        try:
            datum = self.datum.objects.get(pk=phoneId)
            datum.status = status
            datum.callsec = callsec
            datum.recording = recording
            return datum.save(update_fields=['status', 'callsec', 'recording'])
        except Exception:
            return None

    def handle_cdr_save(self, uuid, cdr):
        '''通话结束返回 处理话单
        '''

    def _compute_call_nums(self,
                           ring=0,
                           queue=0,
                           answer=0,
                           free=0,
                           callmax=0,
                           ratio=0):
        '''计算待呼叫量
        '''
        if free == 0:
            return 0
        all_nums = ring + queue + answer
        if all_nums > callmax:
            return 0
        ratio_nums = math.ceil(free * ratio)
        if ring > ratio_nums:
            return 0
        free_nums = ratio_nums - ring
        max_nums = callmax - all_nums
        call_nums = max_nums if free_nums > max_nums else free_nums

        _default_rate = self.rate
        return call_nums if call_nums > _default_rate else _default_rate

    @property
    def rate(self):
        return fs_settings.DEFAULT_AUTO_CALL_RATE
