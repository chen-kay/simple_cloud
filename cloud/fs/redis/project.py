'''项目相关
'''
import json

from .base import BaseRedis


class ProjectRedis(BaseRedis):
    '''项目操作reids
    '''
    project = 'project_{project_id}'
    datum_list = '{project_id}_datum_list'
    datum = '{project_id}_{datum_id}_list'

    def get_project(self, project_id):
        try:
            res = self.redis.get(self.project.format(project_id=project_id))
            return json.loads(res)
        except Exception:
            return {}

    def get_datum(self, project_id):
        try:
            datum_list = self.datum_list.format(project_id=project_id)
            # datum_set = self.redis.sinter(datum_list)
            for datum_id in self.redis.sinter(datum_list):
                datum = self.datum.format(project_id=project_id,
                                          datum_id=datum_id.decode())
                res = self.redis.spop(datum)
                if res:
                    data = json.loads(res)
                    return data.get('id'), data.get('mobile')
            return None, None
        except Exception as e:
            print(e)
            return None, None

    def get_datum_info(self, mobile_id):
        pass
