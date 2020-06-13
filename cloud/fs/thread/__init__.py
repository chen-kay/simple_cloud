import threading
from time import sleep

from .queue import Queue


class FsThread(threading.Thread):
    queue_list = {}
    queue = Queue

    def __init__(self):
        threading.Thread.__init__(self, daemon=True)

    def run(self):
        while True:
            sleep(1000)

    def start_queue_thread(self, domain, project_id):
        queue_name = '{0}_{1}'.format(domain, project_id)
        if queue_name in self.queue_list:
            return False
        _thread = self.queue(domain, project_id)
        self.queue_list[queue_name] = _thread
        _thread.start()
        return True

    def stop_queue_thread(self, domain, project_id):
        queue_name = '{0}_{1}'.format(domain, project_id)
        _thread = self.queue_list.get(queue_name, None)
        if _thread:
            _thread.stop()
            del _thread
            self.queue_list.pop(queue_name)


fs_thread = FsThread()
fs_thread.start()
