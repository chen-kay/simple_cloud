'''项目相关
'''
import json

from .base import BaseRedis


class ProjectRedis(BaseRedis):
    '''项目操作reids
    '''
    project = 'project_{project_id}'
    datum = 'list_{project_id}'

    def get_project(self, project_id):
        try:
            res = self.redis.get(self.project.format(project_id=project_id))
            return json.loads(res)
        except Exception:
            return {}

    def get_datum(self, project_id):
        try:
            res = self.redis.lpop(self.datum.format(project_id=project_id))
            if res:
                data = json.loads(res)
                return data.get('id'), data.get('mobile')
            return None, None
        except Exception as e:
            print(e)
            return None, None

    def get_datum_info(self, mobile_id):
        pass
