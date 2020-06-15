'''用户相关
'''
from .base import BaseRedis


class UserRedis(BaseRedis):
    '''用户操作reids
    '''
    sign_out = 'sign-out-{0}'

    def get_sign_out(self, project_id):
        sign_out = self.sign_out.format(project_id)
        return self.redis.scard(sign_out)

    def get_user(self, username):
        return {}