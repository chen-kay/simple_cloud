from .base import BaseEvent


class ESLEvent(BaseEvent):
    def events_channels(self, callback):
        conn = self.conn
        if conn and conn.connected:
            conn.events(
                "plain",
                "CHANNEL_PROGRESS CHANNEL_ANSWER CHANNEL_BRIDGE CHANNEL_HANGUP"
            )
            try:
                while True:
                    e = conn.recvEvent()
                    if e and callback:
                        callback(e)
            except Exception as e:
                raise e
