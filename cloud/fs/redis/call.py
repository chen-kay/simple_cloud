'''通话相关
'''
from .base import BaseRedis


class CallRedis(BaseRedis):
    '''通话相关redis
    '''
    ring = 'ring-{0}'
    queue = 'queue-{0}'
    answer = 'answer-{0}'

    def get_ring(self, project_id):
        '''获取振铃中
        '''
        ring = self.ring.format(project_id)
        self.redis.scard(ring)

    def get_queue(self, project_id):
        '''获取振铃中
        '''
        queue = self.queue.format(project_id)
        self.redis.scard(queue, project_id)

    def get_answer(self, project_id):
        '''获取振铃中
        '''
        answer = self.answer.format(project_id)
        self.redis.scard(answer, project_id)

    def set_ring(self, project_id, phone_id):
        '''设置振铃中
        '''
        ring = self.ring.format(project_id)
        self.redis.sadd(ring, phone_id)

    def set_queue(self, project_id, phone_id):
        '''设置队列
        '''
        queue = self.queue.format(project_id)
        self.redis.sadd(queue, phone_id)

    def set_answer(self, project_id, phone_id):
        '''设置接通中
        '''
        answer = self.answer.format(project_id)
        self.redis.sadd(answer, phone_id)

    def clear_redis(self, project_id, phone_id):
        '''清除redis
        '''
        ring = self.ring.format(project_id)
        queue = self.queue.format(project_id)
        answer = self.answer.format(project_id)
        self.redis.srem(ring, phone_id)
        self.redis.srem(queue, phone_id)
        self.redis.srem(answer, phone_id)
