from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
# Create your models here.

class SSLMonitors(models.Model):
    ssl_domain = models.CharField("证书绑定域名", max_length=255, null=True, help_text="证书绑定域名")
    ssl_type = models.CharField("类型", max_length=255, null=True, help_text="类型")
    ssl_status = models.CharField("状态", max_length=255, null=True, help_text="状态")
    ssl_expire_time = models.DateTimeField("过期时间", max_length=255, null=True, help_text="过期时间")
    ssl_expire_days = models.IntegerField("过期天数", null=True,  help_text="过期天数")
    ssl_account = models.CharField("证书所在账号", max_length=255, null=True, help_text="证书所在账号")
    ssl_notice_enable = models.BooleanField("是否开启通知", null=True, help_text="是否开启通知", default=True)
    insert_time = models.DateTimeField("插入时间", null=True, auto_now_add=True, help_text="插入时间")
    update_time = models.DateTimeField("更新时间", null=True, auto_now=True, help_text="更新时间")

    class Meta:
        db_table = "monitors_ssl"

# 添加信号接收器
@receiver(pre_save, sender=SSLMonitors)
def update_timestamp(sender, instance, **kwargs):
    instance.update_time = timezone.now()

class DomainMonitors(models.Model):
    domain_name = models.CharField("域名名称", max_length=255, null=True, help_text="域名名称")
    domain_status = models.CharField("域名状态", max_length=255, null=True, help_text="域名状态")
    domain_expire_time = models.DateTimeField("域名过期时间", max_length=255, null=True, help_text="域名过期时间")
    domain_expire_days = models.IntegerField("域名过期天数", null=True,  help_text="域名过期天数")
    domain_account = models.CharField("域名所在账号", max_length=255, null=True, help_text="域名所在账号")
    domain_notice_enable = models.BooleanField("是否开启通知", null=True, help_text="是否开启通知", default=True)
    doman_remark = models.CharField("备注", max_length=255, null=True, help_text="备注")
    insert_time = models.DateTimeField("插入时间", null=True, auto_now_add=True, help_text="插入时间")
    update_time = models.DateTimeField("更新时间", null=True, auto_now=True, help_text="更新时间")

    class Meta:
        db_table = "monitors_domain"

class WebMonitors(models.Model):
    web_uri = models.CharField("网站URI", max_length=255, null=True, help_text="网站URI")
    web_account = models.CharField("网站所在账号", max_length=255, null=True, help_text="网站所在账号")
    web_status = models.CharField("网站状态", max_length=255, null=True, help_text="网站状态", default="正常")
    web_check_enable = models.BooleanField("网站检查是否开启", null=True, help_text="网站检查是否开启", default=True)
    web_http_enable = models.BooleanField("网站HTTP检查是否开启", null=True, help_text="网站HTTP检查是否开启", default=True)
    web_https_enable = models.BooleanField("网站HTTPS检查是否开启", null=True, help_text="网站HTTPS检查是否开启", default=True)
    web_notice_enable = models.BooleanField("网站通知是否开启", null=True, help_text="网站通知是否开启", default=True)
    insert_time = models.DateTimeField("插入时间", null=True, auto_now_add=True, help_text="插入时间")
    update_time = models.DateTimeField("更新时间", null=True, auto_now=True, help_text="更新时间")

    class Meta:
        db_table = "monitors_web"

@receiver(pre_save, sender=WebMonitors)
def update_timestamp(sender, instance, **kwargs):
    instance.update_time = timezone.now()


class WebMonitorsResult(models.Model):
    web_uri = models.CharField("网站URI", max_length=255, null=True, help_text="网站URI")
    web_status = models.CharField("网站状态", max_length=255, null=True, help_text="网站状态")
    web_http_status = models.BooleanField("网站HTTP状态", null=True, help_text="网站HTTP状态")
    web_https_status = models.BooleanField("网站HTTPS状态", null=True, help_text="网站HTTPS状态")
    web_http_response_time = models.FloatField("网站HTTP响应时间", null=True, help_text="网站HTTP响应时间")
    web_https_response_time = models.FloatField("网站HTTPS响应时间", null=True, help_text="网站HTTPS响应时间")
    insert_time = models.DateTimeField("插入时间", null=True, auto_now_add=True, help_text="插入时间")
    update_time = models.DateTimeField("更新时间", null=True, auto_now=True, help_text="更新时间")

    class Meta:
        db_table = "monitors_web_result"
        indexes = [
            models.Index(fields=['web_uri'], name='web_uri_idx'),
            models.Index(fields=['insert_time'], name='insert_time_idx'),
        ]