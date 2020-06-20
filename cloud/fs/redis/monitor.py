'''坐席监控
'''
import time

from cloud.fs.settings import fs_settings

from .base import BaseRedis


class MonitorRedis(BaseRedis):
    min_connect = 'min_connect-{project_id}'
    min_disconnect = 'min_disconnect-{project_id}'
    min_loss = 'min_loss-{project_id}'

    expired_time = fs_settings.DEFAULT_EXPIRED_TIME

    def on_end(self, project_id, status):
        if not project_id:
            return
        if status == 1:
            self.set_connect(project_id)
        if status == 3:
            self.set_loss(project_id)
        else:
            self.set_disconnect(project_id)

    def set_connect(self, project_id):
        '''设置接通
        '''
        connect = self.min_connect.format(project_id=project_id)
        self.redis.rpush(connect, int(time.time()))

    def set_loss(self, project_id):
        '''设置呼损
        '''
        loss = self.min_loss.format(project_id=project_id)
        self.redis.rpush(loss, int(time.time()))

    def set_disconnect(self, project_id):
        '''设置未接通
        '''
        disconnect = self.min_disconnect.format(project_id=project_id)
        self.redis.rpush(disconnect, int(time.time()))

    def expired(self):
        self.expired_connect()
        self.expired_disconnect()
        self.expired_loss()

    def expired_connect(self):
        '''过期接通
        '''
        connect = self.min_connect.format(project_id='*')
        self.clear_expired(connect)

    def expired_loss(self):
        '''过期呼损
        '''
        loss = self.min_loss.format(project_id='*')
        self.clear_expired(loss)

    def expired_disconnect(self):
        '''过期未接通
        '''
        disconnect = self.min_disconnect.format(project_id='*')
        self.clear_expired(disconnect)

    def clear_expired(self, name):
        tt = int(time.time())
        for key in self.redis.scan_iter(name):
            key = key.decode()
            raw = self.redis.lindex(key, index=0)
            if int(raw) < tt - self.expired_time:
                self.redis.lpop(key)
            else:
                break
