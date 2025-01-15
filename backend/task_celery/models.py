from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class BatchCommandRecord(models.Model):
    """批量命令执行记录表"""
    executor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="执行人"
    )
    command = models.TextField(
        verbose_name="执行的命令"
    )
    execution_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="执行时间"
    )
    output = models.JSONField(
        verbose_name="执行结果",
        help_text="存储所有WebSocket输出信息"
    )
    status = models.CharField(
        max_length=20,
        default="running",
        verbose_name="执行状态",
        help_text="running: 执行中, completed: 已完成, failed: 执行失败"
    )

    class Meta:
        db_table = 'batch_command_record'
        verbose_name = '批量命令执行记录'
        verbose_name_plural = verbose_name
        ordering = ['-execution_time']