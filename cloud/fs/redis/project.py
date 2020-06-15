'''项目相关
'''
from .base import BaseRedis


class ProjectRedis(BaseRedis):
    '''项目操作reids
    '''
    def get_project(self, project_id):
        return {}