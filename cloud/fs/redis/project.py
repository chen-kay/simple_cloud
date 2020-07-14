'''项目相关
'''
import json

from .base import BaseRedis


class ProjectRedis(BaseRedis):
    '''项目操作reids
    '''
    project = 'project_{project_id}'
    datum = '{project_id}_*_list'

    def get_project(self, project_id):
        try:
            res = self.redis.get(self.project.format(project_id=project_id))
            return json.loads(res)
        except Exception:
            return {}

    def get_datum(self, project_id):
        try:
            key = self.datum.format(project_id=project_id)
            datums = [item.decode() for item in self.redis.keys(key)]
            for item in datums:
                res = self.redis.lpop(item)
                if res:
                    data = json.loads(res)
                    return data.get('id'), data.get('phone')
                else:
                    self.redis.delete(item)
            return None, None
        except Exception as e:
            print(e)
            return None, None

    def get_datum_info(self, mobile_id):
        pass