#!/usr/bin/env python
# coding=utf-8
import logging
import threading
from time import sleep

# from cloud.fs.event.esl import ESLEvent
import redis


class BaseRedis:
    @property
    def redis(self):
        return self.get_redis_connection()

    def get_redis_connection(self):
        cache = '__cache_redis'
        reids = getattr(self, cache, None)
        if not reids:
            setattr(self, cache, self._get_redis_connection())
        return getattr(self, cache)

    def _get_redis_connection(self):
        try:
            pool = redis.ConnectionPool(host='49.232.19.228',
                                        port=6379,
                                        password='TP+tp13579')
            return redis.Redis(connection_pool=pool)
        except Exception as e:
            print(e)
            return None


class CallRedis(BaseRedis):
    '''通话相关redis
    '''
    ring = 'test-{project_id}'
    queue = 'test-{project_id}'
    answer = 'test-{project_id}'

    def get_ring(self, project_id):
        '''获取振铃中
        '''
        ring = self.ring.format(project_id=project_id)
        return self.redis.scard(ring)

    def get_queue(self, project_id):
        '''获取振铃中
        '''
        queue = self.queue.format(project_id=project_id)
        return self.redis.scard(queue)

    def get_answer(self, project_id):
        '''获取振铃中
        '''
        answer = self.answer.format(project_id=project_id)
        return self.redis.scard(answer)

    def set_ring(self, project_id, phone_id):
        '''设置振铃中
        '''
        ring = self.ring.format(project_id=project_id)
        self.redis.sadd(ring, phone_id)

    def set_queue(self, project_id, phone_id):
        '''设置队列
        '''
        queue = self.queue.format(project_id=project_id)
        self.redis.sadd(queue, phone_id)

    def set_answer(self, project_id, phone_id):
        '''设置接通中
        '''
        answer = self.answer.format(project_id=project_id)
        self.redis.sadd(answer, phone_id)

    def clear_redis(self, project_id, phone_id):
        '''清除redis
        '''
        ring = self.ring.format(project_id=project_id)
        queue = self.queue.format(project_id=project_id)
        answer = self.answer.format(project_id=project_id)
        self.redis.srem(ring, phone_id)
        self.redis.srem(queue, phone_id)
        self.redis.srem(answer, phone_id)


def get_connection(ip, port, passwd):
    import ESL
    assert ESL, "No module named 'ESL'"
    con = ESL.ESLconnection(ip, port, passwd)
    if not con.connected():
        return None
    return con


class BaseEvent:
    @property
    def conn(self):
        return self.get_connection()

    def get_connection(self):
        cache = '__cache_conn'
        conn = getattr(self, cache, None)
        if not conn:
            setattr(self, cache, self._get_connection())
        return getattr(self, cache)

    def _get_connection(self):
        try:
            return get_connection('49.232.19.228', 8021, 'ClueCon')
        except Exception as e:
            print(e)
            return None

    def send(self, msg, bgapi=False, *args, **kwargs):
        conn = self.conn
        last_msg = None
        if not conn:
            return 'get_connection(_, `{0}`, `{1}`) Error{2}'.format(
                '8021', 'ClueCon', self.conn_error), False
        try:
            if conn.connected():
                res = None
                if isinstance(msg, list):
                    res = []
                    for item in msg:
                        last_msg = self._send_msg(item)
                        res.append((item, last_msg))
                else:
                    last_msg = self._send_msg(msg)
                    res = (msg, last_msg)
                return res, True if last_msg.find('+OK') >= 0 else False
            return None, False
        except Exception as e:
            return str(e), False

    def _send_msg(self, msg):
        e = self.conn.api(msg)
        return e.getBody()


class ESLEvent(BaseEvent):
    def events_channels(self, callback):
        conn = self.conn
        if conn and conn.connected:
            conn.events(
                "plain",
                "CHANNEL_CREATE CHANNEL_PROGRESS CHANNEL_ANSWER CHANNEL_BRIDGE CHANNEL_HANGUP"
            )
            try:
                while True:
                    e = conn.recvEvent()
                    print(e)
                    if e and callback:
                        callback(e)
            except Exception as e:
                raise e


class Status(threading.Thread):
    call = CallRedis()

    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self.conn = ESLEvent()

    def run(self):
        print('Thread Status starting.')
        while True:
            try:
                self.conn.events_channels(self.handle_channels)
            except Exception as e:
                print(e)
            sleep(10)
        print('Thread Status stoped.')

    def handle_channels(self, e):
        event_name = e.getHeader('Event-Name')
        # direction = e.getHeader('Call-Direction')
        phone_id = e.getHeader('variable_sip_h_X-Phoneid')
        project_id = e.getHeader('variable_sip_h_X-Proid')
        profile = e.getHeader('variable_sofia_profile_name')
        print(event_name, project_id, phone_id)
        logging.debug(e.serialize())
        if phone_id and project_id and profile == 'external':
            if event_name == 'CHANNEL_CREATE':
                '''设置振铃中
                '''
            # if event_name == 'CHANNEL_PROGRESS':
            #     '''设置振铃中
            #     '''
            #     self.call.set_ring(phone_id, project_id)
            elif event_name == 'CHANNEL_ANSWER':
                '''设置已接通
                '''
                self.call.set_queue(phone_id, project_id)
            elif event_name == 'CHANNEL_BRIDGE':
                '''设置通话中
                '''
                self.call.set_answer(phone_id, project_id)
            elif event_name == 'CHANNEL_HANGUP':
                '''设置挂机
                '''
                self.call.clear_redis(phone_id, project_id)


logging.basicConfig(filename='test_socket.log', level=logging.DEBUG)

thread = Status()
thread.start()
call = thread.call
while True:
    ring = call.get_ring(10)
    answer = call.get_answer(10)
    queue = call.get_queue(10)
    print(ring, answer, queue)

    sleep(1)
