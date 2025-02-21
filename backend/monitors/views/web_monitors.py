import logging
import concurrent.futures
from contextlib import contextmanager
from monitors.utils.db_pool import DatabasePool

from dvadmin.utils.json_response import DetailResponse

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from application import dispatch
from monitors.models import WebMonitors
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.serializers import CustomModelSerializer
from monitors.utils.dingtalk import send_dingtalk_message
import json
from monitors.utils.web_domain_monitoring import check_web_status
from monitors.views.ssl_monitors import update_k8s_cluster_domain

def notify_ding_talk(uri, web_status, consecutive_errors):
    # 钉钉通知
    content = f"""\n![web站点异常](https://q5.itc.cn/images01/20240129/c88baac1abc64da8be22ad8b6acb0f65.jpeg)\n ### web站点异常提醒\n - 站点uri：{uri}\n - 站点状态：{web_status}\n - 站点连续检测异常：{consecutive_errors}次
    """
    # 获取钉钉配置
    access_token = dispatch.get_system_config_values("configdingtalk.access_token")
    secret = dispatch.get_system_config_values("configdingtalk.secret")
    logging.info("准备发送钉钉通知")
    # 发送钉钉通知
    send_dingtalk_message(content, access_token, secret)


@contextmanager
def get_pooled_connection():
    """获取连接池中的连接"""
    conn = None
    try:
        conn = DatabasePool.get_connection()
        yield conn
    finally:
        if conn:
            conn.close()  # 将连接归还到连接池

def process_single_uri(uri):
    try:
        with get_pooled_connection() as conn:
            cursor = conn.cursor()
            
            # 查询监控配置
            cursor.execute(
                "SELECT web_http_enable, web_https_enable FROM monitors_web WHERE web_uri = %s",
                [uri]
            )
            web_monitor = cursor.fetchone()
            
            if not web_monitor:
                logging.error(f"未找到URI为 {uri} 的监控配置")
                return False
                
            web_http_enable, web_https_enable = web_monitor
            results = check_web_status(uri, web_http_enable, web_https_enable)
            
            # 处理状态
            http_status = True
            https_status = True
            http_response_time = 0
            https_response_time = 0
            
            for result in results:
                if result['protocol'] == 'http':
                    http_status = result.get('http_status', True)
                    http_response_time = result.get('response_time', 0)
                elif result['protocol'] == 'https':
                    https_status = result.get('https_status', True)
                    https_response_time = result.get('response_time', 0)
            
            web_status = "正常" if (http_status and https_status) else "异常"
            
            try:
                # 开始事务
                conn.begin()
                
                # 创建监控结果
                cursor.execute("""
                    INSERT INTO monitors_web_result 
                    (web_uri, web_http_status, web_https_status, web_http_response_time, 
                     web_https_response_time, web_status, insert_time) 
                    VALUES (%s, %s, %s, %s, %s, %s, CONVERT_TZ(NOW(), 'UTC', 'Asia/Shanghai'))
                """, [uri, http_status, https_status, http_response_time, 
                      https_response_time, web_status])
                
                # 更新监控状态
                cursor.execute("""
                    UPDATE monitors_web 
                    SET web_status = %s 
                    WHERE web_uri = %s
                """, [web_status, uri])
                
                # 查询最近结果
                cursor.execute("""
                    SELECT web_status 
                    FROM monitors_web_result
                    WHERE web_uri = %s 
                    ORDER BY insert_time DESC 
                    LIMIT 10
                """, [uri])
                recent_results = [row[0] for row in cursor.fetchall()]
                
                # 提交事务
                conn.commit()
                
                # 从最新记录开始计算连续异常的次数
                consecutive_errors = 0
                for status in recent_results:  # recent_results已经是按时间倒序排列
                    if status == "异常":
                        consecutive_errors += 1
                    else:
                        break

                if len(recent_results) >= 3 and all(status == "异常" for status in recent_results[:3]):
                    if len(recent_results) >= 10 and all(status == "异常" for status in recent_results):
                        logging.error(f"网站 {uri} 连续10次检测均显示异常，不再进行通知钉钉")
                    else:
                        logging.error(f"网站 {uri} 最近连续五次检测均显示异常，通知钉钉")
                        notify_ding_talk(uri, web_status, consecutive_errors)
                
            except Exception as e:
                conn.rollback()
                raise e
                
        # return True
        return f" {uri} 监控更新成功, 状态为 {web_status}"
        
    except Exception as e:
        logging.error(f"处理 {uri} 时发生错误: {str(e)}")
        return False


def update_web_monitors_domain():
    logging.info("开始更新k8s集群的域名列表")
    update_k8s_cluster_domain()
    result = [
        {
            'instancename': "web监控自动更新k8s域名",
            'output': "web监控自动更新k8s域名完成!"
        }
    ]
    return result


def auto_update_web_monitors_status():
    try:
        # 获取需要监控的 URI 列表
        with get_pooled_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT web_uri FROM monitors_web WHERE web_check_enable = TRUE"
            )
            web_monitors_uri = [row[0] for row in cursor.fetchall()]
        
        # 使用线程池处理
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(process_single_uri, web_monitors_uri))
            
        result = [{
            'instancename': "网站监控",
            'output': f"网站监控更新完成! 成功: {results}"
        }]
    except Exception as e:
        logging.error(f"网站监控更新失败: {str(e)}")
        result = [{
            'instancename': "网站监控",
            'output': f"网站监控更新失败! 错误为{e}"
        }]
    
    return result


class WebMonitorsSerializer(CustomModelSerializer):
    """
    服务器管理-序列化器
    """
    class Meta:
        model = WebMonitors
        fields = '__all__'

class WebMonitorsViewSet(CustomModelViewSet):
    queryset = WebMonitors.objects.all()
    serializer_class = WebMonitorsSerializer

    # 排序规则进行配置
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.exclude(web_check_enable=False).order_by('web_uri')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return DetailResponse(data=serializer.data, msg="获取成功")
    
    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def web_unmonitors_list(self, request):
        """
        获取未监控的网站列表，支持搜索功能
        """
        queryset = self.filter_queryset(self.get_queryset())
        # 获取搜索关键词
        search = request.query_params.get('search', '')
        
        # 添加基础过滤条件
        queryset = queryset.filter(web_check_enable=False)
        
        # 如果有搜索关键词，添加搜索条件
        if search:
            queryset = queryset.filter(web_uri__icontains=search)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return DetailResponse(data=serializer.data, msg="获取成功")
    
    @action(methods=['PUT'], detail=False, permission_classes=[IsAuthenticated])
    def update_web_check_enable(self, request, *args, **kwargs):
        """
        更改网站状态：正常与异常状态互相切换
        """
        try:
            data = json.loads(request.body.decode())
            web_id = data.get('id')
            if not web_id:
                return DetailResponse(code=400, msg="缺少必要的id参数")
            
            web_monitor = WebMonitors.objects.filter(id=web_id).first()
            if not web_monitor:
                return DetailResponse(code=404, msg="未找到对应的网站记录")
            
            # 修正状态切换逻辑
            new_web_check_enable = not web_monitor.web_check_enable
            web_monitor.web_check_enable = new_web_check_enable
            web_monitor.save()
            
            return DetailResponse(msg=f"状态已更新为：{new_web_check_enable}")
        except Exception as e:
            return DetailResponse(code=500, msg=f"更新失败：{str(e)}")
    
    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def auto_update_web_monitors(self, request):
        """
        自动更新网站监控
        """
        auto_update_web_monitors_status()
        return DetailResponse(msg="获取成功")

