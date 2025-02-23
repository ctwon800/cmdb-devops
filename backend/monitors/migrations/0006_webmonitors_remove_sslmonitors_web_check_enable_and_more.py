# Generated by Django 4.2.13 on 2025-01-03 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitors', '0005_alter_sslmonitors_web_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebMonitors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('web_uri', models.CharField(help_text='网站URI', max_length=255, null=True, verbose_name='网站URI')),
                ('web_account', models.CharField(help_text='网站所在账号', max_length=255, null=True, verbose_name='网站所在账号')),
                ('web_status', models.CharField(default='正常', help_text='网站状态', max_length=255, null=True, verbose_name='网站状态')),
                ('web_check_enable', models.BooleanField(default=True, help_text='网站检查是否开启', null=True, verbose_name='网站检查是否开启')),
                ('web_http_enable', models.BooleanField(default=True, help_text='网站HTTP检查是否开启', null=True, verbose_name='网站HTTP检查是否开启')),
                ('web_https_enable', models.BooleanField(default=True, help_text='网站HTTPS检查是否开启', null=True, verbose_name='网站HTTPS检查是否开启')),
                ('web_notice_enable', models.BooleanField(default=True, help_text='网站通知是否开启', null=True, verbose_name='网站通知是否开启')),
                ('insert_time', models.DateTimeField(auto_now_add=True, help_text='插入时间', null=True, verbose_name='插入时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
            ],
            options={
                'db_table': 'monitors_web',
            },
        ),
        migrations.RemoveField(
            model_name='sslmonitors',
            name='web_check_enable',
        ),
        migrations.RemoveField(
            model_name='sslmonitors',
            name='web_http_enable',
        ),
        migrations.RemoveField(
            model_name='sslmonitors',
            name='web_https_enable',
        ),
        migrations.RemoveField(
            model_name='sslmonitors',
            name='web_notice_enable',
        ),
        migrations.RemoveField(
            model_name='sslmonitors',
            name='web_status',
        ),
    ]
