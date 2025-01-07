from django.urls import path
from rest_framework import routers

from container.views.k8s_nodes import K8sNodeViewSet
from container.views.k8s_deployment import K8sDeploymentViewSet
from container.views.k8s_service import K8sServiceViewSet
from container.views.k8s_ingress import K8sIngressViewSet
from container.views.k8s_namespace import K8sNamespaceViewSet
from container.views.k8s_cluster import K8sClusterViewSet
from container.views.k8s_secret import K8sSecretViewSet
from container.views.k8s_configmap import K8sConfigMapViewSet
from container.views.k8s_pvc import K8sPVCViewSet
from container.views.k8s_workload import K8sWorkloadViewSet

container_url = routers.SimpleRouter()
container_url.register(r'cluster', K8sClusterViewSet)
container_url.register(r'deployment', K8sDeploymentViewSet, basename='k8s_deployment')
container_url.register(r'node', K8sNodeViewSet, basename='k8s_node')
container_url.register(r'service', K8sServiceViewSet, basename='k8s_service')
container_url.register(r'ingress', K8sIngressViewSet, basename='k8s_ingress')
container_url.register(r'secret', K8sSecretViewSet, basename='k8s_secret')
container_url.register(r'configmap', K8sConfigMapViewSet, basename='k8s_configmap')
container_url.register(r'pvc', K8sPVCViewSet, basename='k8s_pvc')
container_url.register(r'workload', K8sWorkloadViewSet, basename='k8s_workload')

urlpatterns = [
    # path('node/', K8sNodeViewSet.as_view(), name='k8s_node'),
    # path('service/', K8sServiceViewSet.as_view(), name='k8s_service'),
    # path('ingress/', K8sIngressViewSet.as_view(), name='k8s_ingress'),
    path('namespace/', K8sNamespaceViewSet.as_view(), name='k8s_namespace'),

]

urlpatterns += container_url.urls