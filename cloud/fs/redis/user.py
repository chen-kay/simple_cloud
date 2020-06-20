'''用户相关
'''
import json

from .base import BaseRedis


class UserRedis(BaseRedis):
    '''用户操作reids
    '''
    user = '{username}'
    sign_in = 'sign-in-{project_id}'

    def get_sign_in(self, project_id):
        sign_in = self.sign_in.format(project_id=project_id)
        nums = self.redis.get(sign_in)
        if nums:
            nums = int(self.redis.get(sign_in).decode())
            return nums if nums > 0 else 0
        return 0

    def get_user(self, username):
        try:
            res = self.redis.get(self.user.format(username=username))
            return json.loads(res)
        except Exception:
            return {}
