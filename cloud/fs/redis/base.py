from django_redis import get_redis_connection


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
            return get_redis_connection('default')
        except Exception as e:
            print(e)
            return None
