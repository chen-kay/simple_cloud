from .base import BaseEvent


class ESLEvent(BaseEvent):
    def events_channels(self, callback):
        conn = self.conn
        if conn and conn.connected:
            conn.events(
                "plain",
                "CHANNEL_CREATE CHANNEL_ANSWER CHANNEL_BRIDGE CHANNEL_HANGUP CHANNEL_DESTROY"
            )
            try:
                while True:
                    e = conn.recvEvent()
                    if e and callback:
                        callback(e)
            except Exception as e:
                setattr(self, self.cache_conn, None)
                raise e
