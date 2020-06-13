from queue import Queue

from .models import Datum, Domain, Gateway, Project, User

datum_queue = Queue()


class ServiceBackend:
    user = User
    gateway = Gateway
    project = Project
    domain = Domain
    datum = Datum

    def get_service_directory(self, domain):
        '''获取系统用户 - 可注册电话
        '''
        return self.user.objects.filter(domain=domain).values(
            'domain', 'username', 'password')

    def get_service_gateway(self, domain=None):
        '''获取系统服务网关 - 系统落地网关
        '''
        if domain:
            try:
                return self.gateway.objects.get(domain=domain).gateway_name
            except Exception:
                return None
        return self.gateway.objects.all().values('gateway_name', 'username',
                                                 'password', 'realm',
                                                 'register')

    def get_service_domain(self):
        '''获取系统企业标识
        '''
        return self.domain.objects.all().values('name')

    def get_service_queue(self, queue_name=None):
        if not queue_name:
            return None
        try:
            domain, _id = queue_name.split('_')
            queryset = self.project.objects.filter(flag=2,
                                                   domain=domain,
                                                   id=_id)
            return queryset.values('queue_name')
        except Exception:
            return None

    def get_service_project(self, project_id):
        '''获取系统项目业务 - 系统自动外呼队列
        '''
        try:
            project = self.project.objects.get(id=project_id)
            return {
                'id': project.pk,
                'domain': project.domain,
                'max_calling': project.max_calling,
                'ratio': project.ratio,
                'status': project.status
            }
        except Exception as e:
            print(e)
            return None

    def handle_cdr_save(self, uuid, cdr):
        '''通话结束返回 处理话单
        '''

    def get_service_mobile(self, mobile_id):
        '''获取呼叫号码
        '''
        return mobile_id

    def check_project_status(self, project_id):
        '''判断项目执行状态 -> 用于自动外呼停止外呼线程
        '''
        try:
            project = self.project.objects.get(id=project_id)
            return project.status
        except Exception:
            return None

    def get_compute_nums(self, project_id):
        '''计算当前外呼数量
        '''
        return 1

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
