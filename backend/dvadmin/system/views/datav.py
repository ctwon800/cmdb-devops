#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/14 15:49
# @Author  : harry
import datetime
import json
import re
import time
import pytz
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from conf.env import DATABASE_USER, DATABASE_NAME
from dvadmin.system.models import Users, LoginLog, FileList
from dvadmin.system.views.login_log import LoginLogSerializer
from dvadmin.utils.json_response import DetailResponse
from django.db import connection
from django.utils.timezone import now
from django.db.models import Count
from django.db.models.functions import TruncDate

from dvadmin.utils.string_util import format_bytes
from cmdb.models import ServerInstance, ServerPlatform, CloudCost, AccountManagement
from monitors.models import DomainMonitors, SSLMonitors


def get_month_cloud_cost():
    pass


def jx_timestamp():
    cur_time = datetime.datetime.now()
    a = datetime.datetime.strftime(cur_time, '%Y-%m-%d %H:%M:%S')
    timeStamp = int(time.mktime(time.strptime(a, "%Y-%m-%d %H:%M:%S")))
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


class DataVViewSet(GenericViewSet):
    queryset = LoginLog.objects.all()
    serializer_class = LoginLogSerializer
    extra_filter_backends = []
    ordering_fields = ['create_datetime']



    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def domain_detail(self, request):
        """
        域名详情
        :param request:
        :return:
        """
        domain_total = DomainMonitors.objects.all().count()
        # 取出快过期的一个域名和剩余天数
        domain_expiring_soon = DomainMonitors.objects.order_by("domain_expire_days")[:1]
        for i in domain_expiring_soon:
            domain_expiring_soon_name = i.domain_name
            domain_expiring_soon_days = i.domain_expire_days

        return DetailResponse(data={"domain_total": domain_total, "domain_expiring_soon_name": domain_expiring_soon_name, "domain_expiring_soon_days": domain_expiring_soon_days}, msg="获取成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def ssl_detail(self, request):
        """
        证书详情
        :param request:
        :return:
        """
        ssl_total = SSLMonitors.objects.all().count()
        # 取出快过期的一个域名和剩余天数
        ssl_expiring_soon = SSLMonitors.objects.filter(ssl_expire_days__isnull=False).order_by("ssl_expire_days")[:1]
        for i in ssl_expiring_soon:
            ssl_expiring_soon_name = i.ssl_domain
            ssl_expiring_soon_days = i.ssl_expire_days
            print(ssl_expiring_soon_name, ssl_expiring_soon_days)
        return DetailResponse(data={"ssl_total": ssl_total, "ssl_expiring_soon_name": ssl_expiring_soon_name, "ssl_expiring_soon_days": ssl_expiring_soon_days}, msg="获取成功")




    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def month_cost_count(self, request):
        """
        服务器总数
        :param request:
        :return:
        """
        now_time = datetime.datetime.now()
        last_year_time = now_time + datetime.timedelta(days=-365)
        last_year_month = last_year_time.strftime('%Y-%m')
        result = CloudCost.objects.filter(bill_cycle__gte=last_year_month).values("bill_cycle").annotate(total_price=Sum("cost")).order_by("bill_cycle")[:12]
        return DetailResponse(data=result, msg="获取成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def server_total(self, request):
        """
        服务器总数
        :param request:
        :return:
        """
        server_total = ServerInstance.objects.all().count()
        return DetailResponse(data={"server_total": server_total}, msg="获取成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def server_distribute_detail(self, request):
        """
        服务器总数
        :param request:
        :return:
        """
        aliyun_platform_id = ServerPlatform.objects.get(server_platform="ALIYUN").id
        aws_platform_id = ServerPlatform.objects.get(server_platform="AWS").id
        aliyun_server_total = ServerInstance.objects.filter(server_platform_id=aliyun_platform_id).count()
        aws_server_total = ServerInstance.objects.filter(server_platform_id=aws_platform_id).count()
        other_server_total = 0

        data = {
            'aliyun_server_total': aliyun_server_total,
            'aws_server_total': aws_server_total,
            'other_server_total': other_server_total
        }
        return DetailResponse(data=data, msg="获取成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def users_login_total(self, request):
        """
        用户登录总数数据
        :param request:
        :return:
        """
        login_total = LoginLog.objects.all().count()
        return DetailResponse(data={"login_total": login_total}, msg="获取成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def users_total(self, request):
        """
        用户总数
        :param request:
        :return:
        """
        users_total = Users.objects.all().count()
        return DetailResponse(data={"users_total": users_total, }, msg="获取成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def attachment_total(self, request):
        """
        附件统计数据
        :param request:
        :return:
        """
        count = FileList.objects.all().count()
        if count != 0:
            data = FileList.objects.aggregate(sum_size=Sum('size'))
        else:
            data = {"sum_size": 0}
        return DetailResponse(data={"count": count, "occupy_space": format_bytes(data.get('sum_size') or 0)},
                              msg="获取成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def database_total(self, request):
        """
        数据库统计数据
        :param request:
        :return:
        """
        count = len(connection.introspection.table_names())
        database_type = connection.settings_dict['ENGINE']
        sql = None
        if 'mysql' in database_type:
            sql = "SELECT SUM(data_length + index_length) AS size FROM information_schema.TABLES WHERE table_schema = DATABASE()"
        elif 'postgres' in database_type or 'psqlextra' in database_type:
            sql = """SELECT SUM(pg_total_relation_size(quote_ident(schemaname) || '.' || quote_ident(tablename))) AS size FROM pg_tables WHERE schemaname = current_schema();"""
        elif 'oracle' in database_type:
            sql = "SELECT SUM(bytes) AS size FROM user_segments"
        elif 'microsoft' in database_type:
            sql = "SELECT SUM(size) * 8 AS size FROM sys.database_files"
        else:
            space = 0
        if sql:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    space = result[0]
                except Exception as e:
                    print(e)
                    space = '无权限'
        return DetailResponse(data={"count": count, "space": format_bytes(space or 0)}, msg="获取成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def registered_user(self, request):
        """
        用户注册趋势
        :param request:
        :return:
        """
        today = datetime.datetime.today()
        seven_days_ago = today - datetime.timedelta(days=30)

        users = Users.objects.filter(date_joined__gte=seven_days_ago).annotate(day=TruncDay('date_joined')).values(
            'day').annotate(count=Count('id'))

        result = []
        for i in range(30):
            date = (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            count = 0
            for user in users:
                if user['day'] == date:
                    count = user['count']
                    break
            result.append({'day': date, 'count': count})

        # users_last_month = Users.objects.filter(date_joined__gte=last_month).annotate(day=TruncDate('date_joined')).values('day').annotate(count=Count('id'))
        return DetailResponse(data={"registered_user_list": result}, msg="获取成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def registered_user(self, request):
        """
        用户注册趋势
        :param request:
        :return:
        """
        day = 30
        today = datetime.datetime.today()
        seven_days_ago = today - datetime.timedelta(days=day)
        users = Users.objects.filter(create_datetime__gte=seven_days_ago).annotate(
            day=TruncDay('create_datetime')).values(
            'day').annotate(count=Count('id')).order_by('-day')
        result = []
        data_dict = {ele.get('day').strftime('%Y-%m-%d'): ele.get('count') for ele in users}
        for i in range(day):
            date = (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            result.append({'day': date, 'count': data_dict[date] if date in data_dict else 0})
        result = sorted(result, key=lambda x: x['day'])
        return DetailResponse(data={"registered_user_list": result}, msg="获取成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def login_user(self, request):
        """
        用户登录趋势
        :param request:
        :return:
        """
        day = 30
        today = datetime.datetime.today()
        seven_days_ago = today - datetime.timedelta(days=day)
        users = LoginLog.objects.filter(create_datetime__gte=seven_days_ago).annotate(
            day=TruncDay('create_datetime')).values(
            'day').annotate(count=Count('id')).order_by('-day')
        result = []
        data_dict = {ele.get('day').strftime('%Y-%m-%d'): ele.get('count') for ele in users}
        for i in range(day):
            date = (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            result.append({'day': date, 'count': data_dict[date] if date in data_dict else 0})
        result = sorted(result, key=lambda x: x['day'])
        return DetailResponse(data={"login_user": result}, msg="获取成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def users_active(self, request):
        """
        用户新增活跃数据统计
        :param request:
        :return:
        """
        today = datetime.date.today()
        seven_days_ago = today - datetime.timedelta(days=6)
        thirty_days_ago = today - datetime.timedelta(days=29)

        today_users = Users.objects.filter(date_joined__date=today).count()
        today_logins = Users.objects.filter(last_login__date=today).count()
        three_days_users = Users.objects.filter(date_joined__gte=seven_days_ago).count()
        seven_days_users = Users.objects.filter(date_joined__gte=thirty_days_ago).count()
        seven_days_active = Users.objects.filter(last_login__gte=seven_days_ago).values('last_login').annotate(
            count=Count('id', distinct=True)).count()
        monthly_active = Users.objects.filter(last_login__gte=thirty_days_ago).values('last_login').annotate(
            count=Count('id', distinct=True)).count()

        data = {
            'today_users': today_users,
            'today_logins': today_logins,
            'three_days': three_days_users,
            'seven_days': seven_days_users,
            'seven_days_active': seven_days_active,
            'monthly_active': monthly_active
        }
        return DetailResponse(data=data, msg="获取成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def login_region(self, request):
        """
        登录用户区域分布
        :param request:
        :return:
        """
        CHINA_PROVINCES = [
            {'name': '北京', 'code': '110000'},
            {'name': '天津', 'code': '120000'},
            {'name': '河北省', 'code': '130000'},
            {'name': '山西省', 'code': '140000'},
            {'name': '内蒙古', 'code': '150000'},
            {'name': '辽宁省', 'code': '210000'},
            {'name': '吉林省', 'code': '220000'},
            {'name': '黑龙江省', 'code': '230000'},
            {'name': '上海', 'code': '310000'},
            {'name': '江苏省', 'code': '320000'},
            {'name': '浙江省', 'code': '330000'},
            {'name': '安徽省', 'code': '340000'},
            {'name': '福建省', 'code': '350000'},
            {'name': '江西省', 'code': '360000'},
            {'name': '山东省', 'code': '370000'},
            {'name': '河南省', 'code': '410000'},
            {'name': '湖北省', 'code': '420000'},
            {'name': '湖南省', 'code': '430000'},
            {'name': '广东省', 'code': '440000'},
            {'name': '广西', 'code': '450000'},
            {'name': '海南省', 'code': '460000'},
            {'name': '重庆', 'code': '500000'},
            {'name': '四川省', 'code': '510000'},
            {'name': '贵州省', 'code': '520000'},
            {'name': '云南省', 'code': '530000'},
            {'name': '西藏', 'code': '540000'},
            {'name': '陕西省', 'code': '610000'},
            {'name': '甘肃省', 'code': '620000'},
            {'name': '青海省', 'code': '630000'},
            {'name': '宁夏', 'code': '640000'},
            {'name': '新疆', 'code': '650000'},
            {'name': '台湾', 'code': '710000'},
            {'name': '香港', 'code': '810000'},
            {'name': '澳门', 'code': '820000'},
            {'name': '钓鱼岛', 'code': '900000'},
            {'name': '未知区域', 'code': '000000'},
        ]
        provinces = [x['name'] for x in CHINA_PROVINCES]
        day = 30
        today = datetime.datetime.today()
        seven_days_ago = today - datetime.timedelta(days=day)
        province_data = LoginLog.objects.filter(create_datetime__gte=seven_days_ago).values('province').annotate(
            count=Count('id')).order_by('-count')
        province_dict = {p: 0 for p in provinces}
        for ele in province_data:
            if ele.get('province') in province_dict:
                province_dict[ele.get('province')] += ele.get('count')
            else:
                province_dict['未知区域'] += ele.get('count')
        data = [{'region': key, 'count': val} for key, val in province_dict.items()]
        data = sorted(data, key=lambda x: x['count'], reverse=True)
        return DetailResponse(data=data, msg="获取成功")


