'''接口相关
用户初始化
用户退出（断开websocket）
用户签入
用户签出
切换队列
    user: ${username}@${domain}  坐席工号
    queue: ${domain}_${project_id} 项目队列
    old_queue: ${domain}_${project_id} 坐席切换队列之前的队列


启动项目（缓）
暂停项目（缓）
重载网关

测试
    呼叫测试
'''
from django.urls import path
from rest_framework import exceptions, serializers, viewsets
from rest_framework.response import Response

from cloud.fs.event import utils
from cloud.fs.event.callcenter import agent, tier
from cloud.fs.models import ServiceBackends as _backends
from cloud.fs.thread import fs_thread


class EmptyFields(serializers.Serializer):
    pass


class UserFields(serializers.Serializer):
    user = serializers.CharField(max_length=100,
                                 help_text='user: ${username}@${domain}  坐席工号')


class QueueFields(serializers.Serializer):
    user = serializers.CharField(max_length=100,
                                 help_text='user: ${username}@${domain}  坐席工号')
    queue = serializers.CharField(max_length=100,
                                  help_text='${domain}_${project_id} 项目队列')
    old_queue = serializers.CharField(
        max_length=100,
        help_text='${domain}_${project_id} 坐席切换队列之前的队列',
        required=False)


class MobileFields(serializers.Serializer):
    mobile = serializers.CharField(max_length=100, help_text='mobile: 测试号码')
    phoneId = serializers.CharField(max_length=100,
                                    help_text='phoneId: 测试号码id')


class BaseViews(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []

    serializer_class = UserFields

    def get_queryset(self):
        return []


class Initialize(BaseViews):
    '''用户初始化
    '''
    def update(self, request, *args, **kwargs):
        user = request.data.get('user', None)
        if not user:
            raise exceptions.NotAcceptable(detail='请求不被允许')
        handle = agent.Agent()
        res, result = handle.init_user(user)
        return Response({'data': res, 'ok': result})


class DestroyUser(BaseViews):
    '''用户退出（断开websocket）
    '''
    def update(self, request, *args, **kwargs):
        user = request.data.get('user', None)
        if not user:
            raise exceptions.NotAcceptable(detail='请求不被允许')
        handle = agent.Agent()
        res, result = handle.del_user(user)
        return Response({'data': res, 'ok': result})


class SignIn(BaseViews):
    '''用户签入
    '''
    def update(self, request, *args, **kwargs):
        user = request.data.get('user', None)
        if not user:
            raise exceptions.NotAcceptable(detail='请求不被允许')
        handle = agent.Agent()
        res, result = handle.sign_in(user)
        return Response({'data': res, 'ok': result})


class SignOut(BaseViews):
    '''用户签出
    '''
    def update(self, request, *args, **kwargs):
        user = request.data.get('user', None)
        if not user:
            raise exceptions.NotAcceptable(detail='请求不被允许')
        handle = agent.Agent()
        res, result = handle.sign_out(user)
        return Response({'data': res, 'ok': result})


class QueueChange(BaseViews):
    '''切换队列
    '''
    serializer_class = QueueFields

    def update(self, request, *args, **kwargs):
        user = request.data.get('user', None)  # 用户
        queue = request.data.get('queue', None)  # 新队列
        old_queue = request.data.get('old_queue', None)  # 旧队列
        if not user:
            raise exceptions.NotAcceptable(detail='请求不被允许')
        handle = agent.Agent()
        res = []
        result = True
        if queue:
            res, result = handle.in_queue(user, queue)
        if result and old_queue:
            if queue != old_queue:
                handle.out_queue(user, old_queue)
        return Response({'data': res, 'ok': result})


class QueueStart(BaseViews):
    '''启动项目
    '''
    serializer_class = EmptyFields

    def update(self, request, pk, *args, **kwargs):
        ins = _backends.service_get_project(pk)
        if not ins:
            return Response({'msg': '项目不存在', 'ok': False})
        fs_thread.start_queue_thread(ins.get('domain'), ins.get('id'))
        return Response({'data': None, 'ok': True})


class QueueStop(BaseViews):
    '''禁用项目
    '''
    serializer_class = EmptyFields

    def update(self, request, pk, *args, **kwargs):
        ins = _backends.service_get_project(pk)
        if not ins:
            return Response({'msg': '项目不存在', 'ok': False})
        fs_thread.stop_queue_thread(ins.get('domain'), ins.get('id'))
        return Response({'data': None, 'ok': True})


class TestAutoCaller(BaseViews):
    serializer_class = MobileFields

    def update(self, request, pk, *args, **kwargs):
        mobile = request.data.get('mobile', None)
        phoneId = request.data.get('phoneId', None)
        if not mobile or not phoneId:
            raise exceptions.NotAcceptable(detail='请求不被允许')
        ins = _backends.service_get_project(pk)
        handle = utils.Utils()
        if not ins:
            return Response({'msg': '项目不存在', 'ok': False})
        queue_name = '{0}_{1}'.format(ins.get('domain'), ins.get('id'))
        res, result = handle.originate_queue_test(mobile,
                                                  queue_name,
                                                  domain=ins.get('domain'),
                                                  phoneId=phoneId)
        return Response({'data': res, 'ok': result})


class AgentList(BaseViews):
    def list(self, request, *args, **kwargs):
        handle = agent.Agent()
        res, result = handle.get_list()
        if not result:
            return Response({'data': res, 'ok': result})
        _, _list = res
        rows = _list.split('\n')
        data = []
        columns = []
        for row in rows:
            if not row or row == '+OK':
                continue
            if not columns:
                columns = row.split('|')
            else:
                data.append({
                    columns[ind]: val
                    for ind, val in enumerate(row.split('|'))
                })
        return Response({'data': data, 'ok': result})


class TierList(BaseViews):
    def list(self, request, *args, **kwargs):
        handle = tier.Tier()
        res, result = handle.get_list()
        if not result:
            return Response({'data': res, 'ok': result})
        _, _list = res
        rows = _list.split('\n')
        data = []
        columns = []
        for row in rows:
            if not row or row == '+OK':
                continue
            if not columns:
                columns = row.split('|')
            else:
                data.append({
                    columns[ind]: val
                    for ind, val in enumerate(row.split('|'))
                })
        return Response({'data': data, 'ok': result})


init = Initialize.as_view({'put': 'update'})
destroy = DestroyUser.as_view({'put': 'update'})
login = SignIn.as_view({'put': 'update'})
logout = SignOut.as_view({'put': 'update'})
agent_list = AgentList.as_view({'get': 'list'})
tier_list = TierList.as_view({'get': 'list'})
queue_change = QueueChange.as_view({'put': 'update'})
queue_start = QueueStart.as_view({'put': 'update'})
queue_stop = QueueStop.as_view({'put': 'update'})
queue_test = TestAutoCaller.as_view({'put': 'update'})

app_name = 'api'
urlpatterns = [
    path('init', init),
    path('destroy', destroy),
    path('sign/in', login),
    path('sign/out', logout),
    path('agent/list', agent_list),
    path('tier/list', tier_list),
    path('queue/change', queue_change),
    path('queue/<int:pk>/start', queue_start),
    path('queue/<int:pk>/stop', queue_stop),
    path('queue/<int:pk>/test', queue_test),
]
