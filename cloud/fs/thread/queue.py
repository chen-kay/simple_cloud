import threading
from time import sleep

from cloud.fs.event import utils
from cloud.fs.models import (service_compute_nums, service_datum_result,
                             service_extract_datum, service_get_gateway,
                             service_get_project)
from cloud.fs.settings import fs_settings


class Queue(threading.Thread):
    def __init__(self, domain, project_id):
        self.stopped = False
        self.status = 1
        self.domain = domain
        self.project_id = project_id

        self.handle = utils.Utils()
        threading.Thread.__init__(self, daemon=True)

    @property
    def queue_name(self):
        return '{0}_{1}'.fromat(self.domain, self.project_id)

    @property
    def caller(self):
        return '{0}_{1}'.fromat(self.domain, self.project_id)

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
            conn = self.handle.conn
            if not conn.connected():
                self.handle.re_connection()
                continue
            self.get_project_info()
            if not self.execting:
                break
            self.get_sys_gateway()
            out_nums = self.compute_out_nums()
            datum = self.get_extract_mobile(out_nums)
            for mobile_id, mobile in datum:
                res, result = self.execute_outbound(mobile_id, mobile)
                if not result:
                    # 呼叫发生错误 --> 更改呼叫结果未接通
                    service_datum_result(mobile_id)
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
        info = service_get_project(self.project_id)
        self.max_calling = info.get('max_calling', None)
        self.ratio = info.get('ratio', None)
        self.status = info.get('status', None)

    def get_sys_gateway(self):
        '''获取网关信息
        '''
        gw = service_get_gateway(self.domain)
        self.gateway = gw or fs_settings.DEFAULT_GATEWAY_NAME

    def compute_out_nums(self):
        '''计算外呼数量
        '''
        return service_compute_nums(self.project_id)

    def get_extract_mobile(self, nums):
        '''提取号码
        '''
        res = set()
        for ind in range(nums):
            datum = service_extract_datum(self.project_id)
            if datum:
                res.add(datum)
            else:
                break
        return res

    def execute_outbound(self, phoneId, mobile):
        '''执行呼叫
        '''
        print(phoneId, mobile)
        return '测试呼叫', True
        # return self.handle.originate_queue_test(mobile,
        #                                         self.queue_name,
        #                                         phoneId=phoneId,
        #                                         caller=self.caller,
        #                                         gateway=self.gateway)
