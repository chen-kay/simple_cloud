'''企业相关
'''
from .base import BaseRedis


class DomainRedis(BaseRedis):
    domain = 'company_list'

    def get_domain(self):
        self.redis.scard(self.domain)
        return []
