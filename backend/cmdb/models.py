from django.db import models


class ServerPlatform(models.Model):
    server_platform = models.CharField("server_platform", max_length=255, help_text="服务器平台", blank=True)
    insert_time = models.DateTimeField("插入时间", null=True, auto_now_add=True, help_text="插入时间")
    update_time = models.DateTimeField("更新时间", null=True, auto_now=True, help_text="更新时间")

    class Meta:
        ordering = ["id"]
        db_table = "cmdb_server_platform"

class AccountManagement(models.Model):
    account_name = models.CharField("账号", max_length=255, help_text="账号")
    login_username = models.CharField("云账号用户名", max_length=255, null=True, help_text="云账号用户名", blank=True)
    accesskey_id =  models.CharField("云账号访问id", max_length=255, null=True, help_text="云账号访问id", blank=True)
    accesskey_secret = models.CharField("云账号访问密钥", max_length=255, null=True, help_text="云账号访问密钥", blank=True)
    region = models.CharField("区域", max_length=255, null=True, help_text="区域", blank=True)
    server_platform = models.ForeignKey("ServerPlatform", on_delete=models.CASCADE)
    insert_time = models.DateTimeField("插入时间", null=True, auto_now_add=True, help_text="插入时间")
    update_time = models.DateTimeField("更新时间", null=True, auto_now=True, help_text="更新时间")

    class Meta:
        ordering = ["id"]
        db_table = "cmdb_server_account"


class ServerInstance(models.Model):
    server_platform = models.ForeignKey("ServerPlatform", on_delete=models.CASCADE)
    account_name = models.ForeignKey("AccountManagement", on_delete=models.CASCADE)
    instanceid = models.CharField("实例id", max_length=100, unique=True, help_text="实例id", blank=True)
    instancename = models.CharField("实例名称", max_length=100, null=True, help_text="实例名称", blank=True)
    instancetype = models.CharField("实例类型", max_length=255, null=True, help_text="实例类型", blank=True)
    hostname = models.CharField("主机名称", max_length=255, null=True, help_text="主机名称", blank=True)
    region   = models.CharField("区域", max_length=255, null=True, help_text="区域", blank=True)
    zone  = models.CharField("实例可用区", max_length=255, null=True, help_text="实例可用区", blank=True)
    osname = models.CharField("OS", max_length=255, null=True, help_text="OS", blank=True)
    ostype = models.CharField("os类型", max_length=255, null=True, help_text="os类型", blank=True)
    cpu = models.CharField("cpu", max_length=255, null=True, help_text="cpu", blank=True)
    memory = models.CharField("内存", max_length=255, null=True, help_text="内存", blank=True)
    public_ip = models.CharField("公网ip", max_length=255, null=True, help_text="公网ip", blank=True)
    primary_ip = models.CharField("内网ip", max_length=255, null=True, help_text="内网ip", blank=True)
    status = models.CharField("运行状态", max_length=255, null=True, help_text="运行状态", blank=True)
    remote_port = models.IntegerField("远程登录端口", default=22, null=True, help_text="远程登录端口", blank=True)
    remote_auth = models.ForeignKey("ServerRemoteAccount", null=True,  on_delete=models.CASCADE, help_text="远程连接的登录账号", blank=True)
    remote_frequently = models.BooleanField("服务器远程是否常用标识", default=False, help_text="服务器远程是否常用标识", blank=True)
    create_time = models.CharField("创建时间", max_length=255, null=True, help_text="创建时间", blank=True)
    exprire_time = models.CharField("过期时间", max_length=255, null=True, help_text="过期时间", blank=True)
    start_time = models.CharField("启动时间", max_length=255, null=True, help_text="启动时间", blank=True)
    insert_time = models.DateTimeField("插入时间", null=True, auto_now_add=True, help_text="插入时间")
    update_time = models.DateTimeField("更新时间", null=True, auto_now=True, help_text="更新时间")

    def __str__(self):
        return self.instanceid


    class Meta:
        ordering = ["id"]
        db_table = "cmdb_server_instance"


class CloudCost(models.Model):
    server_platform = models.ForeignKey("ServerPlatform", on_delete=models.CASCADE)
    account_name = models.ForeignKey("AccountManagement", on_delete=models.CASCADE)
    bill_cycle = models.CharField("账单周期", max_length=255, null=True, help_text="账单周期", blank=True)
    cost = models.DecimalField("费用", max_digits=13, decimal_places=2, null=True, help_text="费用", blank=True)
    cost_usd = models.DecimalField("费用-美元", max_digits=13, decimal_places=2, null=True, help_text="费用-美元", blank=True)
    insert_time = models.DateTimeField("插入时间", null=True, auto_now_add=True, help_text="插入时间")
    update_time = models.DateTimeField("更新时间", null=True, auto_now=True, help_text="更新时间")


    class Meta:
        # ordering = ["id"]
        db_table = "cmdb_cloud_cost"

class ServerRemoteAccount(models.Model):
    remote_name = models.CharField("远程登录名称", max_length=255, null=True, help_text="远程登录名称")
    remote_username = models.CharField("远程登录用户名", max_length=255, null=True, help_text="远程登录用户名", blank=True)
    remote_password = models.CharField("远程登录密码", max_length=255, null=True, help_text="远程登录密码", blank=True)
    # login_port = models.IntegerField("远程登录端口", max_length=255, null=True, help_text="远程登录端口")
    remote_type = models.IntegerField("远程登录类型", default=0, null=True, help_text="0为密码登录，1为密码登录", blank=True)
    remote_private_key = models.CharField("远程登录密钥", max_length=255, null=True, help_text="远程登录密钥", blank=True)
    remark = models.CharField("备注", max_length=255, null=True, help_text="备注", blank=True)
    insert_time = models.DateTimeField("插入时间", null=True, auto_now_add=True, help_text="插入时间")
    update_time = models.DateTimeField("更新时间", null=True, auto_now=True, help_text="更新时间")


    class Meta:
        db_table = "cmdb_server_remote_account"


# class ServerRemoteList(models.Model):
#     server_name = models.CharField("服务器名称", max_length=100, null=True, help_text="实例名称")
#     server_platform = models.ForeignKey("ServerPlatform", on_delete=models.CASCADE)
#     server_account_name = models.ForeignKey("AccountManagement", on_delete=models.CASCADE)
#     server_remote_port = models.IntegerField("远程登录端口", null=True, help_text="远程登录端口")
#     server_remote_auth = models.ForeignKey("ServerLoginAccount", on_delete=models.CASCADE)
#     insert_time = models.DateTimeField("插入时间", null=True, auto_now_add=True, help_text="插入时间")
#     update_time = models.DateTimeField("更新时间", null=True, auto_now=True, help_text="更新时间")
#     class Meta:
#         db_table = "cmdb_server_remote_list"


class ServerRemoteRecord(models.Model):
    record_user = models.CharField("远程操作用户", max_length=255, null=True, help_text="远程操作用户")
    record_host = models.CharField("远程操作服务器名称", max_length=255, null=True, help_text="远程操作服务器名称")
    record_filepath = models.CharField("录像文件", max_length=255, null=True, help_text="录像文件")
    record_start_time = models.DateTimeField("录像开始时间", max_length=255, null=True, help_text="录像开始时间", blank=True)
    record_end_time = models.DateTimeField("录像结束时间", max_length=255, null=True, help_text="录像结束时间",
                                             blank=True)
    insert_time = models.DateTimeField("插入时间", null=True, auto_now_add=True, help_text="插入时间")
    update_time = models.DateTimeField("更新时间", null=True, auto_now=True, help_text="更新时间")

    class Meta:
        db_table = "cmdb_server_remote_record"
