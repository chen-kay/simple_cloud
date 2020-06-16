'''企业相关
'''
import json

from .base import BaseRedis


class DomainRedis(BaseRedis):
    domain = 'company_list'

    def get_domain(self):
        try:
            res = self.redis.get(self.domain)
            return json.loads(res)
        except Exception:
            return []
