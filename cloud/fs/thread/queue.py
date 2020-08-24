import threading
from time import sleep

from django.db.models import F

from cloud.fs.event import utils
from cloud.fs.models import DatumResult, HujiaoMeans, HujiaoProject
from cloud.fs.models import ServiceBackends as _backends
from cloud.fs.settings import fs_settings


class Queue(threading.Thread):
    def __init__(self, domain, project_id):
        self.stopped = False
        self.status = 1
        self.domain = domain
        self.project_id = project_id
        self.company_id = None

        self.handle = utils.Utils()
        threading.Thread.__init__(self, daemon=True)

        try:
            self.hujiao_project = HujiaoProject.objects.get(id=self.project_id)
        except Exception:
            self.hujiao_project = None

    @property
    def queue_name(self):
        return '{0}_{1}'.format(self.domain, self.project_id)

    @property
    def caller(self):
        return '{0}_{1}'.format(self.domain, self.project_id)

    def run(self):
        print('{0} - {1} : started'.format(self.domain, self.project_id))
        while not self.stopped:
            '''
            1. 获取项目信息 -> 主叫、并发系数、执行状态
            2. 获取呼叫网关
            3. 计算呼叫量
            4. 提取号码
            5. 外呼
            '''
            self.get_project_info()
            # if not self.execting:
            #     break
            self.get_sys_gateway()
            out_nums = self.compute_out_nums()
            if not out_nums:
                sleep(1)
                continue
            # datum = self.get_extract_mobile(out_nums)
            for item in range(out_nums):
                datum = self.get_datum_result()
                if datum:
                    res, result = self.execute_outbound(datum.pk, datum.phone)
                    # if not result:
                    # 呼叫发生错误 --> 更改呼叫结果未接通
                    # _backends.service_datum_result(mobile_id)
                else:
                    print('无号码')
                    break
            sleep(1)
        print('{0} - {1} : stopped'.format(self.domain, self.project_id))

    def stop(self):
        self.stopped = True

    @property
    def execting(self):
        if self.status != 1:
            return False
        return True

    def get_project_info(self):
        '''获取业务信息
        '''
        info = _backends.service_get_project(self.project_id)
        max_calling = info.get('max_calling', 0)
        ratio = info.get('ratio', 0)
        self.max_calling = int(max_calling) if max_calling else 0
        self.ratio = float(ratio) if ratio else 0
        self.status = info.get('status', None)
        self.company_id = info.get('company_id', None)

    def get_sys_gateway(self):
        '''获取网关信息
        '''
        gw = _backends.service_get_gateway_name(self.domain)
        self.gateway = gw or fs_settings.DEFAULT_GATEWAY_NAME

    def compute_out_nums(self):
        '''计算外呼数量
        '''
        return _backends.service_compute_nums(self.project_id,
                                              callmax=self.max_calling,
                                              ratio=self.ratio)

    def get_extract_mobile(self, nums):
        '''提取号码
        '''
        res = set()
        for ind in range(nums):
            mobile_id, mobile = _backends.service_extract_datum(
                self.project_id)
            if mobile_id and mobile:
                res.add((mobile_id, mobile))
            else:
                print('无号码')
                break
        return res

    def execute_outbound(self, phoneId, mobile):
        '''执行呼叫
        '''
        return self.handle.originate_queue_test(mobile,
                                                self.queue_name,
                                                domain=self.domain,
                                                phoneId=phoneId,
                                                project_id=self.project_id,
                                                caller=self.caller,
                                                gateway=self.gateway)

    def get_datum_result(self):
        '''获取项目资料
        '''
        mobile_id, mobile = _backends.service_extract_datum(self.project_id)
        if mobile_id and mobile:
            datum = DatumResult.objects.create(company_id=self.company_id,
                                               project_id=self.project_id,
                                               datum_id=mobile_id,
                                               phone=mobile)
            self.diff_project_datum()
            self.diff_means_num(mobile_id)
            return datum
        return None

    def diff_project_datum(self):
        """
        剩余资料数-1
        """
        try:
            if self.hujiao_project:
                self.hujiao_project.surplus_nums = F('surplus_nums') - 1
                self.hujiao_project.save(update_fields=['surplus_nums'])
        except Exception:
            pass

    def diff_means_num(self, ziliao):
        try:
            hujiao_means = HujiaoMeans.objects.get(id=ziliao)
            print(hujiao_means)
            hujiao_means.live_no = F('live_no') - 1
            hujiao_means.save(update_fields=['live_no'])
        except Exception:
            pass
