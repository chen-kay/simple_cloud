'''网关相关
'''
from .base import BaseRedis


class GatewayRedis(BaseRedis):
    def get_gateway(self):
        return []

    def gat_domain_gateway(self, domain):
        return {}
