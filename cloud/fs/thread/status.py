import logging
import threading
import traceback
from time import sleep

from cloud.fs.event.base import BaseEvent, ESLConnException
from cloud.fs.redis import call

logger = logging.getLogger('logs')


class Status(threading.Thread):
    call = call

    def __init__(self):
        threading.Thread.__init__(self, daemon=True)

    def run(self):
        print('Thread Status starting.')
        while True:
            try:
                conn = BaseEvent().get_connection()
                self.handle_event(conn)
            except ESLConnException:
                print('FreeSWITCH Connecting Error')
            except Exception:
                logger.error(traceback.format_exc())
            sleep(5)
        print('Thread Status stoped.')

    def handle_event(self, conn):
        events = 'CHANNEL_CREATE CHANNEL_ANSWER CHANNEL_BRIDGE CHANNEL_HANGUP CHANNEL_DESTROY'  # noqa
        print('connected', conn.connected())
        if conn:
            conn.events("plain", events)
            self.start_listen_event(conn)

    def start_listen_event(self, conn):
        while True:
            e = conn.recvEvent()
            if e:
                self.handle_channels(e)

    def handle_channels(self, e):
        event_name = e.getHeader('Event-Name')
        phone_id = e.getHeader('variable_sip_h_X-Phoneid')
        project_id = e.getHeader('variable_sip_h_X-Proid')
        pro_type = e.getHeader('variable_sip_h_X-Protype')
        profile = e.getHeader('variable_sofia_profile_name')

        if event_name == 'SERVER_DISCONNECTED':
            raise Exception('FreeSWITCH is DISCONNECTED')

        print(event_name, phone_id, project_id, profile)
        if str(pro_type) not in ['1', '2']:
            return
        if phone_id and project_id and profile == 'external':
            if event_name == 'CHANNEL_CREATE':
                '''设置振铃中
                '''
                self.call.set_ring(project_id, phone_id)
            elif event_name == 'CHANNEL_ANSWER':
                '''设置已接通
                '''
                self.call.set_answer(project_id, phone_id)
            elif event_name == 'CHANNEL_BRIDGE':
                '''设置通话中
                '''
                self.call.set_queue(project_id, phone_id)
            elif event_name == 'CHANNEL_HANGUP':
                '''设置挂机
                '''
                self.call.clear_redis(project_id, phone_id)
            elif event_name == 'CHANNEL_DESTROY':
                '''设置销毁
                '''
                self.call.clear_redis(project_id, phone_id)
