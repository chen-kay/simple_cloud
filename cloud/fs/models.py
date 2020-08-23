from django.db import models

from cloud import fs


def _get_backends(name, *args, **kwargs):
    for backend in fs.get_backends():
        if hasattr(backend, name):
            return getattr(backend, name)(*args, **kwargs)
    return None


class ServiceBackends:
    @classmethod
    def service_get_domain(cls):
        '''获取企业域名信息
        '''
        return _get_backends('get_service_domain')

    @classmethod
    def service_get_gateway(cls, domain=None):
        '''获取企业网关信息
        '''
        return _get_backends('get_service_gateway', domain=domain)

    @classmethod
    def service_get_gateway_name(cls, domain=None):
        '''获取企业网关名称
        '''
        gateway = cls.service_get_gateway(domain=domain)
        return gateway.get('gateway_name') if gateway else None

    @classmethod
    def service_get_directory(cls, username):
        '''获取企业用户信息
        '''
        return _get_backends('get_service_directory', username)

    @classmethod
    def service_get_userid(cls, username):
        '''
        '''
        user = cls.service_get_directory(username)
        return user.get('id') if user else None

    @classmethod
    def service_get_project(cls, project_id):
        '''获取项目队列信息
        '''
        return _get_backends('get_service_project', project_id)

    @classmethod
    def service_get_queue(cls, queue_name):
        '''获取项目队列信息
        '''
        try:
            _id = queue_name.split('_')[-1]
            return cls.service_get_project(_id)
        except Exception:
            return None

    @classmethod
    def service_get_mobile(cls, mobile_id):
        '''获取呼叫真实号码
        '''
        return _get_backends('get_service_mobile', mobile_id)

    @classmethod
    def service_compute_nums(cls, project_id, callmax=0, ratio=0):
        '''计算外呼量
        '''
        return _get_backends('get_compute_nums',
                             project_id,
                             callmax=callmax,
                             ratio=ratio)

    @classmethod
    def service_extract_datum(cls, project_id):
        '''提取项目资料
        '''
        return _get_backends('get_extract_datum', project_id)

    @classmethod
    def service_datum_result(cls, project_id):
        '''修改资料呼叫结果
        '''
        return _get_backends('change_datum_result', project_id)


class Domain(models.Model):
    '''企业
    '''
    name = models.CharField('企业标识', max_length=10, db_index=True)


class User(models.Model):
    '''用户
    '''
    domain = models.ForeignKey(Domain, models.DO_NOTHING, verbose_name='企业')
    username = models.CharField('账号', max_length=50, db_index=True)
    password = models.CharField(verbose_name='密码', max_length=50)

    def __str__(self):
        return '{0}@{1}'.format(self.username, self.domain.name)

    def to_dict(self):
        return {
            'id': self.id,
            'domain': self.domain.name,
            'username': self.username,
            'password': self.password,
            'eff_caller': self.username
        }

    class Meta:
        unique_together = ('domain', 'username')


class Gateway(models.Model):
    '''网关
    '''
    domain = models.ForeignKey(Domain, models.DO_NOTHING, verbose_name='企业')
    name = models.CharField(verbose_name='网关名称（数字+字母）', max_length=20)
    username = models.CharField(verbose_name='配置账户', max_length=50, null=True)
    password = models.CharField(verbose_name='配置密码', max_length=50, null=True)
    realm = models.CharField(verbose_name='IP地址', max_length=50)
    register = models.BooleanField(verbose_name='是否注册', default=False)

    def __str__(self):
        return '{0}_{1}'.format(self.domain.name, self.name)

    def to_dict(self):
        return {
            'gateway_name': str(self),
            'username': self.username,
            'password': self.password,
            'realm': self.realm,
            'register': self.register,
        }


class Project(models.Model):
    '''项目管理
    '''
    domain = models.ForeignKey(Domain, models.DO_NOTHING, verbose_name='企业')
    name = models.CharField('项目名称', max_length=100)
    flag = models.IntegerField('项目类型',
                               choices=((1, '手动外呼'), (2, '自动外呼')),
                               default=1)
    max_calling = models.IntegerField(verbose_name='最大并发', default=1)
    ratio = models.DecimalField(verbose_name='系数',
                                max_digits=4,
                                decimal_places=2,
                                default=1)
    status = models.IntegerField('状态',
                                 choices=((0, '等待'), (1, '执行')),
                                 default=0)

    def __str__(self):
        return '{0}_{1}'.format(self.domain.name, self.id)

    def to_dict(self):
        return {
            'id': self.id,
            'domain': self.domain.name,
            'max_calling': self.max_calling,
            'ratio': self.ratio,
            'status': self.status,
            'queue_name': str(self),
        }


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


class DatumResult(models.Model):
    '''呼叫结果
    '''
    company_id = models.IntegerField('企业id')
    project_id = models.IntegerField('项目id')
    user_id = models.IntegerField('坐席id', null=True)
    datum_id = models.CharField('项目资料', max_length=50, db_index=True)
    phone = models.CharField(verbose_name='号码', max_length=50, db_index=True)
    source = models.IntegerField(verbose_name='最后一次呼叫状态',
                                 choices=((1, '接通'), (2, '未接通'), (3, '呼损')),
                                 default=2)
    callsec = models.IntegerField(verbose_name='呼叫总时长', default=0)
    callnum = models.IntegerField(verbose_name='接通次数', default=0)
    callrecord = models.CharField(verbose_name='最后一次录音地址',
                                  max_length=200,
                                  null='',
                                  default=None)
    call_time = models.DateTimeField(verbose_name='最后一次接通时间',
                                     null=True,
                                     default=None)

    create_date = models.DateField(verbose_name='提号时间',
                                   auto_now_add=True,
                                   db_index=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'hujiao_datumresult'


class CallResult(models.Model):
    '''呼叫记录
    '''
    pid_id = models.IntegerField('DatumResult:id', null=True)
    company_id = models.IntegerField('企业id')
    project_id = models.IntegerField('项目id')
    user_id = models.IntegerField('坐席id', null=True)

    mobile = models.CharField('号码', max_length=50)
    direction = models.CharField('呼叫类型', max_length=20, blank=True, default='')
    duration = models.IntegerField('呼叫时长', default=0)
    billsec = models.IntegerField('接通时长', default=0)
    callsec = models.IntegerField('通话时长', default=0)
    start_time = models.DateTimeField('呼叫时间', null=True)
    answer_time = models.DateTimeField('应答时间', null=True)
    bridge_time = models.DateTimeField('接通时间', null=True)
    end_time = models.DateTimeField('挂机时间', null=True)
    hangup_cause = models.CharField('挂机原因',
                                    max_length=50,
                                    blank=True,
                                    default='')
    hangup_source = models.CharField('挂机方',
                                     max_length=50,
                                     blank=True,
                                     default='')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    create_date = models.DateField('创建日期', auto_now_add=True, db_index=True)

    queue_name = models.CharField('队列', max_length=50, blank=True, default='')

    status = models.IntegerField('状态',
                                 choices=((1, '接通'), (2, '未接通'), (3, '呼损')),
                                 default=2)
    recording = models.CharField('录音地址',
                                 max_length=200,
                                 blank=True,
                                 default='')

    caller_id_name = models.CharField('主叫名',
                                      max_length=100,
                                      blank=True,
                                      default='')
    caller_id_number = models.CharField('主叫号码',
                                        max_length=100,
                                        blank=True,
                                        default='')
    callee_id_name = models.CharField('被叫名',
                                      max_length=100,
                                      blank=True,
                                      default='')
    callee_id_number = models.CharField('被叫号码',
                                        max_length=100,
                                        blank=True,
                                        default='')

    class Meta:
        managed = False
        db_table = 'fs_callresult'


class HujiaoProject(models.Model):
    surplus_nums = models.IntegerField('剩余资料数', default=0)

    class Meta:
        managed = False
        db_table = 'hujiao_project'

        
class HujiaoMeans(models.Model):
    live_no = models.IntegerField('剩余资料数', default=0)

    class Meta:
        managed = False
        db_table = 'hujiao_ziliao'
