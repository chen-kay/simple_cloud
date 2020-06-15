# Generated by Django 3.0.7 on 2020-06-14 12:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=10, verbose_name='企业标识')),
            ],
        ),
        migrations.CreateModel(
            name='Gateway',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(db_index=True, max_length=10, verbose_name='企业标识')),
                ('name', models.CharField(max_length=20, verbose_name='网关名称（数字+字母）')),
                ('username', models.CharField(max_length=50, null=True, verbose_name='配置账户')),
                ('password', models.CharField(max_length=50, null=True, verbose_name='配置密码')),
                ('realm', models.CharField(max_length=50, verbose_name='IP地址')),
                ('register', models.BooleanField(default=False, verbose_name='是否注册')),
                ('default', models.BooleanField(default=False, verbose_name='默认网关')),
                ('gateway_name', models.CharField(max_length=20, unique=True, verbose_name='网关标识:企业标识+_+网关名称')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(db_index=True, max_length=10, verbose_name='企业标识')),
                ('name', models.CharField(max_length=100, verbose_name='项目名称')),
                ('flag', models.IntegerField(choices=[(1, '手动外呼'), (2, '自动外呼')], default=1, verbose_name='项目类型')),
                ('caller', models.CharField(max_length=100, verbose_name='主叫号码')),
                ('max_calling', models.IntegerField(default=1, verbose_name='最大并发')),
                ('ratio', models.DecimalField(decimal_places=2, default=1, max_digits=4, verbose_name='系数')),
                ('status', models.IntegerField(choices=[(0, '等待'), (1, '执行')], default=0, verbose_name='状态')),
                ('queue_name', models.CharField(max_length=100, unique=True, verbose_name='队列标识:企业标识+_+项目id')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(db_index=True, max_length=10, verbose_name='企业标识')),
                ('username', models.CharField(db_index=True, max_length=50, verbose_name='账号')),
                ('password', models.CharField(max_length=50, verbose_name='密码')),
            ],
            options={
                'unique_together': {('domain', 'username')},
            },
        ),
        migrations.CreateModel(
            name='Datum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile', models.CharField(max_length=50, verbose_name='号码')),
                ('status', models.IntegerField(choices=[(1, '接通'), (2, '未接通'), (3, '呼损')], default=2, verbose_name='状态')),
                ('callsec', models.IntegerField(default=0, verbose_name='通话时长')),
                ('recording', models.CharField(blank=True, default='', max_length=200, verbose_name='录音文件地址')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='fs.Project', verbose_name='项目')),
            ],
        ),
    ]
