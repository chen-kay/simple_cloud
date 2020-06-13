from django.db import models

from cloud import fs


def service_get_directory(domain):
    '''获取企业用户信息
    '''
    name = 'get_service_directory'
    for backend in fs.get_backends():
        if hasattr(backend, name):
            return getattr(backend, name)(domain)
    return None


def service_get_gateway(domain=None):
    '''获取企业网关信息
    '''
    name = 'get_service_gateway'
    for backend in fs.get_backends():
        if hasattr(backend, name):
            return getattr(backend, name)(domain=domain)
    return None


def service_get_domain():
    '''获取企业域名信息
    '''
    name = 'get_service_domain'
    for backend in fs.get_backends():
        if hasattr(backend, name):
            return getattr(backend, name)()
    return None


def service_get_queue(queue_name):
    '''获取项目队列信息
    '''
    name = 'get_service_queue'
    for backend in fs.get_backends():
        if backend and hasattr(backend, name):
            return getattr(backend, name)(queue_name)
    return None


def service_get_project(project_id):
    '''获取执行项目信息
    '''
    name = 'get_service_project'
    for backend in fs.get_backends():
        if backend and hasattr(backend, name):
            return getattr(backend, name)(project_id)
    return None


def service_cdr_handle(uuid, cdr):
    '''话单处理
    '''
    name = 'handle_cdr_save'
    for backend in fs.get_backends():
        if backend and hasattr(backend, name):
            getattr(backend, name)(uuid, cdr)


def service_get_mobile(mobile_id):
    '''获取呼叫真实号码
    '''
    name = 'get_service_mobile'
    for backend in fs.get_backends():
        if backend and hasattr(backend, name):
            return getattr(backend, name)(mobile_id)
    return mobile_id


def service_compute_nums(project_id):
    '''计算外呼量
    '''
    name = 'get_compute_nums'
    for backend in fs.get_backends():
        if backend and hasattr(backend, name):
            return getattr(backend, name)(project_id)
    return 0


def service_extract_datum(project_id):
    '''提取项目资料
    '''
    name = 'get_extract_datum'
    for backend in fs.get_backends():
        if backend and hasattr(backend, name):
            return getattr(backend, name)(project_id)
    return None


def service_datum_result(mobile_id, status=2, callsec=0, recording=None):
    '''修改资料呼叫结果
    '''
    name = 'change_datum_result'
    for backend in fs.get_backends():
        if backend and hasattr(backend, name):
            return getattr(backend, name)(mobile_id,
                                          status=status,
                                          callsec=callsec,
                                          recording=recording)
    return None


class Domain(models.Model):
    '''企业
    '''
    name = models.CharField('企业标识', max_length=10, db_index=True)


class User(models.Model):
    '''用户
    '''
    domain = models.CharField('企业标识', max_length=10, db_index=True)
    username = models.CharField('账号', max_length=50, db_index=True)
    password = models.CharField(verbose_name='密码', max_length=50)

    class Meta:
        unique_together = ('domain', 'username')


class Gateway(models.Model):
    '''网关
    '''
    domain = models.CharField('企业标识', max_length=10, db_index=True)
    name = models.CharField(verbose_name='网关名称（数字+字母）', max_length=20)
    username = models.CharField(verbose_name='配置账户', max_length=50, null=True)
    password = models.CharField(verbose_name='配置密码', max_length=50, null=True)
    realm = models.CharField(verbose_name='IP地址', max_length=50)
    register = models.BooleanField(verbose_name='是否注册', default=False)
    default = models.BooleanField(verbose_name='默认网关', default=False)

    gateway_name = models.CharField(verbose_name='网关标识:企业标识+_+网关名称',
                                    max_length=20,
                                    unique=True)


class Project(models.Model):
    '''项目管理
    '''
    domain = models.CharField('企业标识', max_length=10, db_index=True)
    name = models.CharField('项目名称', max_length=100)
    flag = models.IntegerField('项目类型',
                               choices=((1, '手动外呼'), (2, '自动外呼')),
                               default=1)
    caller = models.CharField('主叫号码', max_length=100)

    max_calling = models.IntegerField(verbose_name='最大并发', default=1)
    ratio = models.DecimalField(verbose_name='系数',
                                max_digits=4,
                                decimal_places=2,
                                default=1)
    status = models.IntegerField('状态',
                                 choices=((0, '等待'), (1, '执行')),
                                 default=0)
    queue_name = models.CharField('队列标识:企业标识+_+项目id',
                                  max_length=100,
                                  unique=True)


class Datum(models.Model):
    mobile = models.CharField('号码', max_length=50)
    project = models.ForeignKey(Project, models.DO_NOTHING, verbose_name='项目')
    status = models.IntegerField('状态',
                                 choices=((1, '接通'), (2, '未接通'), (3, '呼损')),
                                 default=2)
    callsec = models.IntegerField('通话时长', default=0)
    recording = models.CharField('录音文件地址',
                                 max_length=200,
                                 default='',
                                 blank=True)
