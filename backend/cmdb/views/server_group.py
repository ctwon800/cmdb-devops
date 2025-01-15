from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from cmdb.models import ServersGroup, ServerInstance
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.serializers import CustomModelSerializer
from rest_framework.permissions import IsAuthenticated
from dvadmin.utils.json_response import DetailResponse


class ServerSerializer(serializers.ModelSerializer):
    """服务器序列化器"""
    class Meta:
        model = ServerInstance
        fields = ['id', 'instancename', 'instanceid', 'hostname', 'public_ip', 'primary_ip']


class ServerGroupSerializer(CustomModelSerializer):
    """
    服务器管理-序列化器
    """
    class Meta:
        model = ServersGroup
        fields = "__all__"

class ServerGroupViewSet(CustomModelViewSet):
    queryset = ServersGroup.objects.all()
    serializer_class = ServerGroupSerializer

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def servers_list(self, request, pk=None):
        """获取服务器组下的所有服务器"""
        group = self.get_object()
        servers = group.server_instances.all()
        serializer = ServerSerializer(servers, many=True)
        data = {
            "count": servers.count(),
            "data": serializer.data
        }
        return DetailResponse(
            data=data,
            msg="获取成功"
        )

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def add_servers(self, request):
        """向服务器组添加服务器"""
        group_id = request.data.get('group_id')
        server_ids = request.data.get('server_ids', [])
        
        if not group_id:
            return Response({"error": "请提供服务器组ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not server_ids:
            return Response({"error": "请提供服务器ID列表"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            group = ServersGroup.objects.get(id=group_id)
            servers = ServerInstance.objects.filter(id__in=server_ids)
            
            if not servers.exists():
                return Response({"error": "未找到指定的服务器"}, status=status.HTTP_404_NOT_FOUND)
            
            group.server_instances.add(*servers)
            
            serializer = ServerSerializer(servers, many=True)
            return Response({
                "message": "服务器添加成功",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except ServersGroup.DoesNotExist:
            return Response({"error": "未找到指定的服务器组"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"添加服务器失败：{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def remove_server(self, request):
        """从服务器组移除服务器"""
        group_id = request.data.get('group_id')
        server_id = request.data.get('server_id')
        
        if not group_id:
            return Response({"error": "请提供服务器组ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not server_id:
            return Response({"error": "请提供服务器ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            group = ServersGroup.objects.get(id=group_id)
            server = ServerInstance.objects.get(id=server_id)
            
            group.server_instances.remove(server)
            
            return DetailResponse(
                data={
                    "message": "服务器已成功从组中移除",
                    "group_id": group_id,
                    "server_id": server_id
                },
                msg="移除成功"
            )
        except ServersGroup.DoesNotExist:
            return Response({"error": "未找到指定的服务器组"}, status=status.HTTP_404_NOT_FOUND)
        except ServerInstance.DoesNotExist:
            return Response({"error": "未找到指定的服务器"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"移除服务器失败：{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
