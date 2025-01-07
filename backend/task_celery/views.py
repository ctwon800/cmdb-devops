import ast
import json
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from rest_framework.response import Response
from rest_framework import serializers, viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError

from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from django_celery_results.models import TaskResult
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models.functions import Lower
from celery import current_app
from task_celery.tasks import *

class CrontabScheduleSerializer(serializers.ModelSerializer):
    # 优化返回的 crontab 信息
    crontab_string = serializers.SerializerMethodField()

    class Meta:
        model = CrontabSchedule
        fields = ['minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year']

    # def get_crontab_string(self, obj):
    #     return f"{obj.minute} {obj.hour} {obj.day_of_week} {obj.day_of_month} {obj.month_of_year}"

class PeriodicTaskSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    # task_type = serializers.CharField(source='task')
    task_type = serializers.SerializerMethodField()
    # args = serializers.JSONField()
    command = serializers.SerializerMethodField()  # 定制化 args 的输出
    command_type = serializers.SerializerMethodField()
    # kwargs = serializers.JSONField()
    select_instance = serializers.SerializerMethodField()
    crontab = serializers.SerializerMethodField()

    class Meta:
        model = PeriodicTask
        fields = ['id', 'name', 'task', 'task_type', 'command', 'command_type', 'select_instance', 'crontab', 'enabled', 'description', 'last_run_at', 'total_run_count']
        extra_kwargs = {
            'task': {'required': False}  # 将task字段设置为非必填
        }
    # 将 args 转换为换行字符串
    def get_command(self, obj):
        if obj.args:
            # 假设 args 是 JSON 序列化的列表字符串，解析为 Python 列表后再处理
            args_list = eval(obj.args)
            return '\n'.join(map(str, args_list))
        return ""


    def get_command_type(self, obj):
        if not obj.kwargs:
            return ""
        if obj.kwargs == '{}':
            return ""
        if isinstance(obj.kwargs, str):
            # 将字符串转换为字典
            instance_data_trans = ast.literal_eval(obj.kwargs)
            # instance_data_trans = json.dumps(obj.kwargs)
            instance_data = instance_data_trans.get('command_type')
        else:
            instance_data = obj.kwargs
        # 遍历 kwargs 中的所有键值对，收集所有 'instance_name' 的值
        # instance_names = []
        # for item in instance_data:
        #     instance_names.append(item['instance_name'])
        return instance_data
    def get_select_instance(self, obj):
        if not obj.kwargs:
            return []
        if obj.kwargs == '{}':
            return []
        if isinstance(obj.kwargs, str):
            # 将字符串转换为字典
            instance_data_trans = ast.literal_eval(obj.kwargs)
            # instance_data_trans = json.dumps(obj.kwargs)
            instance_data = instance_data_trans.get('instance_name')
        else:
            instance_data = obj.kwargs
        # 遍历 kwargs 中的所有键值对，收集所有 'instance_name' 的值
        # instance_names = []
        # for item in instance_data:
        #     instance_names.append(item['instance_name'])
        return instance_data
    def get_task_type(self, obj):
        if obj.task:
            # 假设 args 是 JSON 序列化的列表字符串，解析为 Python 列表后再处理
            if obj.task == "task_celery.tasks.local_job_task":
                return "本地任务"
            elif obj.task == "task_celery.tasks.remote_job_task":
                return "远程任务"
            else:
                return "系统任务"
        return ""

    def get_task(self, obj):
        if obj.task:
            return obj.task
        return ""

    def get_or_create_crontab(self, crontab_str):
        # 分解 crontab 字符串
        minute, hour, day_of_week, day_of_month, month_of_year = crontab_str.split()

        # 查询是否已存在
        crontab, created = CrontabSchedule.objects.get_or_create(
            minute=minute,
            hour=hour,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
        )

        return crontab

    def get_crontab(self, obj):
        if obj.crontab:
            crontab = obj.crontab
            return f"{crontab.minute} {crontab.hour} {crontab.day_of_week} {crontab.day_of_month} {crontab.month_of_year}"
        return None

    def to_representation(self, instance):
        # 使用父类的 to_representation 方法序列化对象
        representation = super().to_representation(instance)
        # # 进一步优化 crontab 字段的输出
        # if representation['crontab'] is None:
        #     representation.pop('crontab', None)
        return representation


    def to_internal_value(self, data):
        # Handle the select_instance logic during deserialization
        select_instance = data.get('select_instance', [])
        kwargs = data.get('kwargs', {})

        if isinstance(select_instance, list) and select_instance:
            kwargs['instance_name'] = select_instance
        elif isinstance(select_instance, str):
            kwargs['instance_name'] = [select_instance]

        data['kwargs'] = kwargs
        return super().to_internal_value(data)


    # 在接收数据时将 command 字段解析为 args 字段
    def validate_command(self, value):
        if isinstance(value, str):
            # 处理 POST/PUT 请求时的 command 字段
            # print("command is a string")
            value_list = value.splitlines()
            value_list = json.dumps(value_list)
            return value_list
            # return str(value_list)  # 将列表转换回 JSON 字符串形式存储到 args
        # print("command is not a string")
        return value


    def validate_select_instance(self, value):
        if isinstance(value, list):
            # 处理 POST/PUT 请求时的 command 字段
            if not value:
                return {}
            # print(value)
            # instance_name_list = [{'instance_name': name} for name in value]
            # instance_name_list = {'instance_name': value}
            # instance_name_list = json.dumps(instance_name_list)
            # return instance_name_list  # 返回转换后的字典
            return value
        return value

    def validate_command_type(self, value):
        if isinstance(value, str):
            # 处理 POST/PUT 请求时的 command 字段
            if not value:
                return {}
            # print(value)
            # instance_name_list = {'command_type': value}
            # instance_name_list = json.dumps(instance_name_list)
            return value  # 返回转换后的字典
        return value

    def validate_task_type(self, value):
        if isinstance(value, str):
            if value == "本地任务":
                return "task_celery.tasks.local_job_task"
            elif value == "远程任务":
                return "task_celery.tasks.remote_job_task"
            elif value == "系统任务":
                # 对于系统任务，使用原始的 task 值
                original_task = self.context['request'].data.get('task', '')
                return original_task
            else:
                return None

    def create(self, validated_data):
        validated_data['command'] = self.context['request'].data.get('command', '')
        validated_data['command_type'] = self.context['request'].data.get('command_type', '')
        validated_data['task_type'] = self.context['request'].data.get('task_type', '')
        validated_data['crontab'] = self.context['request'].data.get('crontab', '')
        validated_data['select_instance'] = self.context['request'].data.get('select_instance', '')
        crontab_str = validated_data.pop('crontab', None)
        # if validated_data['task_type'] == "系统任务":
        #     raise ValidationError("系统任务不可创建")
        if crontab_str:
            validated_data['crontab'] = self.get_or_create_crontab(crontab_str)
        validated_data['args'] = self.validate_command(validated_data.pop('command', ""))
        # validated_data['kwargs'] = self.validate_select_instance(validated_data.pop('select_instance', ""))
        default_kwargs = {
            'instance_name': self.validate_select_instance(validated_data.pop('select_instance', "")),
            'command_type': self.validate_command_type(validated_data.pop('command_type', "")),
        }
        validated_data['kwargs'] = json.dumps(default_kwargs)
        validated_data['task'] = self.validate_task_type(validated_data.pop('task_type', ""))

        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['command'] = self.context['request'].data.get('command', '')
        validated_data['task_type'] = self.context['request'].data.get('task_type', '')
        validated_data['command_type'] = self.context['request'].data.get('command_type', '')
        validated_data['crontab'] = self.context['request'].data.get('crontab', '')
        validated_data['select_instance'] = self.context['request'].data.get('select_instance', '')
        validated_data['task'] = self.context['request'].data.get('task', '')
        crontab_str = validated_data.pop('crontab', None)
        # if validated_data['task_type'] == "系统任务":
        #     raise ValidationError("系统任务不可修改")
        if crontab_str:
            validated_data['crontab'] = self.get_or_create_crontab(crontab_str)
        validated_data['args'] = self.validate_command(validated_data.pop('command', ""))
        default_kwargs = {
            'instance_name': self.validate_select_instance(validated_data.pop('select_instance', "")),
            'command_type': self.validate_command_type(validated_data.pop('command_type', "")),
        }
        validated_data['kwargs'] = json.dumps(default_kwargs)
        # validated_data['kwargs'] = {
        #     'instance_name': self.validate_select_instance(validated_data.pop('select_instance', "")),
        #     'command_type': self.validate_command_type(validated_data.pop('command_type', "")),
        # }
        # validated_data['kwargs'] = self.validate_select_instance(validated_data.pop('select_instance', ""))
        validated_data['task'] = self.validate_task_type(validated_data.pop('task_type', ""))
        if not validated_data['task']:
            validated_data.pop('task')
        return super().update(instance, validated_data)

class PeriodicTaskListViewSet(viewsets.ModelViewSet):
    queryset = PeriodicTask.objects.all()
    serializer_class = PeriodicTaskSerializer

    # 添加搜索功能
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]

    # 过滤字段
    filterset_fields = ['enabled']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.enabled:
            raise ValidationError("启用的任务不可删除")
        instance.delete()
        message = {"code": 2000, "data": [], "msg": "删除成功"}
        return JsonResponse(message, safe=False)


    def get_queryset(self):
        # 可根据需求自定义查询集过滤逻辑
        # return super().get_queryset()
        queryset = super().get_queryset()


        # 获取查询参数中的 name 值
        name = self.request.query_params.get('name', None)
        if name:
            # 使用 __icontains 进行模糊匹配
            queryset = queryset.filter(name__icontains=name)

        # 获取查询参数中的 task_type 值
        task_type = self.request.query_params.get('task_type', None)
        if task_type:
            if task_type == "本地任务":
                queryset = queryset.filter(task="task_celery.tasks.local_job_task")
            elif task_type == "远程任务":
                queryset = queryset.filter(task="task_celery.tasks.remote_job_task")
            elif task_type == "系统任务":
                queryset = queryset.exclude(
                    Q(task="task_celery.tasks.local_job_task") |
                    Q(task="task_celery.tasks.remote_job_task")
                )
            else:
                queryset = queryset.filter(task="unknown_task_type")

        return queryset

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def get_task_type(self, request):
        task_type = [
            {
                "task_type": "远程任务"
            },
            {
                "task_type": "本地任务"
            },
            {
                "task_type": "系统任务"
            }
        ]
        return DetailResponse(data={"data": task_type}, msg="获取成功")

    @action(methods=['PUT'], detail=False, permission_classes=[IsAuthenticated])
    def run_tasks(self, request):
        pk = request.data.get("id")
        try:
            periodic_task = PeriodicTask.objects.get(id=pk)
            task_name = periodic_task.task
            task_args = periodic_task.args
            task_kwargs = periodic_task.kwargs
            # 将字符串转换为相应的 Python 数据结构
            task_args_list = ast.literal_eval(task_args) if task_args else []
            task_kwargs_dict = ast.literal_eval(task_kwargs) if task_kwargs else {}
            task_func = current_app.tasks[task_name]
            # 执行任务
            task_func.apply_async(args=task_args_list, kwargs=task_kwargs_dict)
            return HttpResponse("执行完成")
        except Exception as e:
            return JsonResponse({"error": "任务执行出错: {}".format(str(e))}, status=500)


# class IntervalSerializer(CustomModelSerializer):
#     """
#     间隔任务-序列化器
#     """
#     class Meta:
#         model = IntervalSchedule
#         fields = "__all__"
#
#
# class IntervalViewSet(CustomModelViewSet):
#     queryset = IntervalSchedule.objects.all()
#     serializer_class = IntervalSerializer
#
#

# class CrontabSerializer(CustomModelSerializer):
#     """
#     crontab任务-序列化器
#     """
#     class Meta:
#         model = CrontabSchedule
#         exclude = ["timezone"]
#
#
# class CrontabViewSet(CustomModelViewSet):
#     queryset = CrontabSchedule.objects.all()
#     serializer_class = CrontabSerializer
#



class TaskResultsSerializer(CustomModelSerializer):
    """
    任务结果-序列化器
    """
    result = serializers.SerializerMethodField(read_only=True)
    task_name = serializers.SerializerMethodField()
    def get_result(self, obj):
        if obj.result:
            result = json.loads(obj.result)
            return result
        return None

    def get_task_name(self, obj):
        if obj.task_name:
            # 假设 args 是 JSON 序列化的列表字符串，解析为 Python 列表后再处理
            if obj.task_name == "task_celery.tasks.local_job_task":
                return "本地任务"
            elif obj.task_name == "task_celery.tasks.remote_job_task":
                return "远程任务"
            else:
                return "系统任务"
        return ""

    class Meta:
        model = TaskResult
        read_only_fields = ["id"]
        fields = ["id", "task_id", "periodic_task_name", "result", "task_name", "status", "date_done"]


class TaskResultsViewSet(CustomModelViewSet):
    queryset = TaskResult.objects.all()
    serializer_class = TaskResultsSerializer


    # 添加搜索功能
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]

    # 过滤字段
    filterset_fields = ['periodic_task_name']
    def get_queryset(self):
        # 可根据需求自定义查询集过滤逻辑
        # return super().get_queryset()
        queryset = super().get_queryset()

        # 获取查询参数中的 task_name 值
        task_name = self.request.query_params.get('task_name', None)
        if task_name:
            if task_name == "本地任务":
                queryset = queryset.filter(task_name="task_celery.tasks.local_job_task")
            elif task_name == "远程任务":
                queryset = queryset.filter(task_name="task_celery.tasks.remote_job_task")
            elif task_name == "系统任务":
                queryset = queryset.exclude(
                    Q(task_name="task_celery.tasks.local_job_task") |
                    Q(task_name="task_celery.tasks.remote_job_task")
                )
            else:
                queryset = queryset.filter(task_name="unknown_task_type")
        return queryset

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def get_task_status(self, request):
        # results = TaskResult.objects.values_list('status', flat=True).distinct()
        results = TaskResult.objects.values('status').distinct().order_by('status')
        data = []
        for item in results:
            data.append(item)
        return DetailResponse(data={"data": data}, msg="获取成功")

