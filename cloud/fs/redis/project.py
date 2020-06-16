'''项目相关
'''
from .base import BaseRedis


class ProjectRedis(BaseRedis):
    '''项目操作reids
    '''
    project = 'project_{project_id}'
    datum = 'list_{project_id}'

    def get_project(self, project_id):
        project = self.project.format(project_id=project_id)
        return self.redis.hget(project)

    def get_datum_list(self, project_id):
        datum = self.datum.format(project_id=project_id)
        return self.redis.lpop(datum)
