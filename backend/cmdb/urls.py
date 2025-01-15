from django.urls import path
from rest_framework import routers

from cmdb.views.server_instance import ServerInstanceViewSet
from cmdb.views.account_management import AccountManagementViewSet
from cmdb.views.server_platform import ServerPlatformViewSet
from cmdb.views.cloud_cost import CloudCostViewSet
from cmdb.views.server_remote_account import ServerRemoteAccountViewSet
from cmdb.views.server_remote_record import ServerRemoteRecordViewSet
from monitors.views.ssl_monitors import SSLMonitorsViewSet
from cmdb.views.server_group import ServerGroupViewSet

cmdb_url = routers.SimpleRouter()
cmdb_url.register(r'server_instance', ServerInstanceViewSet)
cmdb_url.register(r'account_management', AccountManagementViewSet)
cmdb_url.register(r'server_platform', ServerPlatformViewSet)
cmdb_url.register(r'cloud_cost', CloudCostViewSet)
cmdb_url.register(r'server_remote_account', ServerRemoteAccountViewSet)
cmdb_url.register(r'server_remote_record', ServerRemoteRecordViewSet)
cmdb_url.register(r'ssl_monitors', SSLMonitorsViewSet)
cmdb_url.register(r'server_group', ServerGroupViewSet)


devops_url = routers.SimpleRouter()

urlpatterns = [
    # path('k8s_dep_detail/', K8sDeploymentViewSet.dep_det, name='dep_det'),
    path('update_ser_remote_account/<str:my_id>/', ServerRemoteAccountViewSet.as_view({'post': 'update_ser_remote_account'}), name='update_ser_remote_account'),

]

urlpatterns += cmdb_url.urls



# ###  定时任务  ####
# scheduler = BackgroundScheduler()
# scheduler.add_job(AutoUpdateYunRes, 'cron', hour=18, minute=10, id='test', replace_existing=True,
#                       timezone='Asia/Shanghai')
# scheduler.add_job(AutoUpdateCloudCost, 'cron', day=3, hour=18, minute=10, id='test', replace_existing=True,
#                       timezone='Asia/Shanghai')
# scheduler.start()
