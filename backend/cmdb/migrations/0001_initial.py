# Generated by Django 3.2.19 on 2024-03-04 11:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccountManagement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_name', models.CharField(help_text='账号', max_length=255, verbose_name='账号')),
                ('login_username', models.CharField(blank=True, help_text='云账号用户名', max_length=255, null=True, verbose_name='云账号用户名')),
                ('accesskey_id', models.CharField(blank=True, help_text='云账号访问id', max_length=255, null=True, verbose_name='云账号访问id')),
                ('accesskey_secret', models.CharField(blank=True, help_text='云账号访问密钥', max_length=255, null=True, verbose_name='云账号访问密钥')),
                ('region', models.CharField(blank=True, help_text='区域', max_length=255, null=True, verbose_name='区域')),
                ('insert_time', models.DateTimeField(auto_now_add=True, help_text='插入时间', null=True, verbose_name='插入时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
            ],
            options={
                'db_table': 'cmdb_server_account',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ServerPlatform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server_platform', models.CharField(blank=True, help_text='服务器平台', max_length=255, verbose_name='server_platform')),
                ('insert_time', models.DateTimeField(auto_now_add=True, help_text='插入时间', null=True, verbose_name='插入时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
            ],
            options={
                'db_table': 'cmdb_server_platform',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ServerRemoteAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remote_name', models.CharField(help_text='远程登录名称', max_length=255, null=True, verbose_name='远程登录名称')),
                ('remote_username', models.CharField(blank=True, help_text='远程登录用户名', max_length=255, null=True, verbose_name='远程登录用户名')),
                ('remote_password', models.CharField(blank=True, help_text='远程登录密码', max_length=255, null=True, verbose_name='远程登录密码')),
                ('remote_type', models.IntegerField(blank=True, default=0, help_text='0为密码登录，1为密码登录', null=True, verbose_name='远程登录类型')),
                ('remote_private_key', models.CharField(blank=True, help_text='远程登录密钥', max_length=255, null=True, verbose_name='远程登录密钥')),
                ('remark', models.CharField(blank=True, help_text='备注', max_length=255, null=True, verbose_name='备注')),
                ('insert_time', models.DateTimeField(auto_now_add=True, help_text='插入时间', null=True, verbose_name='插入时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
            ],
            options={
                'db_table': 'cmdb_server_remote_account',
            },
        ),
        migrations.CreateModel(
            name='ServerRemoteRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_user', models.CharField(help_text='远程操作用户', max_length=255, null=True, verbose_name='远程操作用户')),
                ('record_host', models.CharField(help_text='远程操作服务器名称', max_length=255, null=True, verbose_name='远程操作服务器名称')),
                ('record_filepath', models.CharField(help_text='录像文件', max_length=255, null=True, verbose_name='录像文件')),
                ('record_start_time', models.DateTimeField(blank=True, help_text='录像开始时间', max_length=255, null=True, verbose_name='录像开始时间')),
                ('record_end_time', models.DateTimeField(blank=True, help_text='录像结束时间', max_length=255, null=True, verbose_name='录像结束时间')),
                ('insert_time', models.DateTimeField(auto_now_add=True, help_text='插入时间', null=True, verbose_name='插入时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
            ],
            options={
                'db_table': 'cmdb_server_remote_record',
            },
        ),
        migrations.CreateModel(
            name='ServerInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instanceid', models.CharField(blank=True, help_text='实例id', max_length=100, unique=True, verbose_name='实例id')),
                ('instancename', models.CharField(blank=True, help_text='实例名称', max_length=100, null=True, verbose_name='实例名称')),
                ('instancetype', models.CharField(blank=True, help_text='实例类型', max_length=255, null=True, verbose_name='实例类型')),
                ('hostname', models.CharField(blank=True, help_text='主机名称', max_length=255, null=True, verbose_name='主机名称')),
                ('region', models.CharField(blank=True, help_text='区域', max_length=255, null=True, verbose_name='区域')),
                ('zone', models.CharField(blank=True, help_text='实例可用区', max_length=255, null=True, verbose_name='实例可用区')),
                ('osname', models.CharField(blank=True, help_text='OS', max_length=255, null=True, verbose_name='OS')),
                ('ostype', models.CharField(blank=True, help_text='os类型', max_length=255, null=True, verbose_name='os类型')),
                ('cpu', models.CharField(blank=True, help_text='cpu', max_length=255, null=True, verbose_name='cpu')),
                ('memory', models.CharField(blank=True, help_text='内存', max_length=255, null=True, verbose_name='内存')),
                ('public_ip', models.CharField(blank=True, help_text='公网ip', max_length=255, null=True, verbose_name='公网ip')),
                ('primary_ip', models.CharField(blank=True, help_text='内网ip', max_length=255, null=True, verbose_name='内网ip')),
                ('status', models.CharField(blank=True, help_text='运行状态', max_length=255, null=True, verbose_name='运行状态')),
                ('remote_port', models.IntegerField(blank=True, default=22, help_text='远程登录端口', null=True, verbose_name='远程登录端口')),
                ('remote_frequently', models.BooleanField(blank=True, default=False, help_text='服务器远程是否常用标识', verbose_name='服务器远程是否常用标识')),
                ('create_time', models.CharField(blank=True, help_text='创建时间', max_length=255, null=True, verbose_name='创建时间')),
                ('exprire_time', models.CharField(blank=True, help_text='过期时间', max_length=255, null=True, verbose_name='过期时间')),
                ('start_time', models.CharField(blank=True, help_text='启动时间', max_length=255, null=True, verbose_name='启动时间')),
                ('insert_time', models.DateTimeField(auto_now_add=True, help_text='插入时间', null=True, verbose_name='插入时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('account_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmdb.accountmanagement')),
                ('remote_auth', models.ForeignKey(blank=True, help_text='远程连接的登录账号', null=True, on_delete=django.db.models.deletion.CASCADE, to='cmdb.serverremoteaccount')),
                ('server_platform', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmdb.serverplatform')),
            ],
            options={
                'db_table': 'cmdb_server_instance',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='CloudCost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bill_cycle', models.CharField(blank=True, help_text='账单周期', max_length=255, null=True, verbose_name='账单周期')),
                ('cost', models.DecimalField(blank=True, decimal_places=2, help_text='费用', max_digits=13, null=True, verbose_name='费用')),
                ('cost_usd', models.DecimalField(blank=True, decimal_places=2, help_text='费用-美元', max_digits=13, null=True, verbose_name='费用-美元')),
                ('insert_time', models.DateTimeField(auto_now_add=True, help_text='插入时间', null=True, verbose_name='插入时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('account_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmdb.accountmanagement')),
                ('server_platform', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmdb.serverplatform')),
            ],
            options={
                'db_table': 'cmdb_cloud_cost',
            },
        ),
        migrations.AddField(
            model_name='accountmanagement',
            name='server_platform',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmdb.serverplatform'),
        ),
    ]
