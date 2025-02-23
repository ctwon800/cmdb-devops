# Generated by Django 4.2.13 on 2025-01-10 15:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BatchCommandRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('command', models.TextField(verbose_name='执行的命令')),
                ('execution_time', models.DateTimeField(auto_now_add=True, verbose_name='执行时间')),
                ('output', models.JSONField(help_text='存储所有WebSocket输出信息', verbose_name='执行结果')),
                ('status', models.CharField(default='running', help_text='running: 执行中, completed: 已完成, failed: 执行失败', max_length=20, verbose_name='执行状态')),
                ('executor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='执行人')),
            ],
            options={
                'verbose_name': '批量命令执行记录',
                'verbose_name_plural': '批量命令执行记录',
                'db_table': 'batch_command_record',
                'ordering': ['-execution_time'],
            },
        ),
    ]
