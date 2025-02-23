# Generated by Django 3.2.19 on 2024-05-11 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SSLMonitors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ssl_domain', models.CharField(help_text='证书绑定域名', max_length=255, null=True, verbose_name='证书绑定域名')),
                ('ssl_type', models.CharField(help_text='类型', max_length=255, null=True, verbose_name='类型')),
                ('ssl_status', models.CharField(help_text='状态', max_length=255, null=True, verbose_name='状态')),
                ('ssl_expire_time', models.DateTimeField(help_text='过期时间', max_length=255, null=True, verbose_name='过期时间')),
                ('ssl_expire_days', models.CharField(help_text='过期天数', max_length=255, null=True, verbose_name='过期天数')),
                ('ssl_account', models.CharField(help_text='证书所在账号', max_length=255, null=True, verbose_name='证书所在账号')),
                ('ssl_notice_enable', models.BooleanField(default=True, help_text='是否开启通知', null=True, verbose_name='是否开启通知')),
                ('insert_time', models.DateTimeField(auto_now_add=True, help_text='插入时间', null=True, verbose_name='插入时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
            ],
            options={
                'db_table': 'monitors_ssl',
            },
        ),
    ]
