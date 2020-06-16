'''用户相关
'''
from .base import BaseRedis


class UserRedis(BaseRedis):
    '''用户操作reids
    '''
    user = '{username}'
    sign_out = 'sign-out-{project_id}'

    def get_sign_out(self, project_id):
        sign_out = self.sign_out.format(project_id=project_id)
        return self.redis.scard(sign_out)

    def get_user(self, username):
        user = self.user.format(username=username)
        return self.redis.hget(user)