import logging
import threading
import traceback
from time import sleep

from cloud.fs.redis import monitor

from .queue import Queue
from .status import Status

logger = logging.getLogger('logs')


class FsThread(threading.Thread):
    # queue_list = {}
    queue = Queue
    status = Status
    monitor = monitor

    def __init__(self):
        threading.Thread.__init__(self, daemon=True)

    def run(self):
        while True:
            try:
                self.monitor.expired()
            except Exception as e:
                logger.error(traceback.format_exc())
                print(e)
            sleep(1)

    def start_queue_thread(self, domain, project_id):
        # queue_name = '{0}_{1}'.format(domain, project_id)
        # if queue_name in self.queue_list:
        #     return False
        _thread = self.queue(domain, project_id)
        # self.queue_list[queue_name] = _thread
        _thread.start()
        return True

    def stop_queue_thread(self, domain, project_id):
        pass
        # queue_name = '{0}_{1}'.format(domain, project_id)
        # _thread = self.queue_list.get(queue_name, None)
        # if _thread:
        #     _thread.stop()
        #     del _thread
        #     self.queue_list.pop(queue_name)

    def start_status_thead(self):
        '''启动呼叫状态线程
        '''
        _thread = self.status()
        _thread.start()


fs_thread = FsThread()
fs_thread.start()
# fs_thread.start_status_thead()
