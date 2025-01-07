from django.urls import path
from rest_framework import routers

from monitors.views.ssl_monitors import SSLMonitorsViewSet
from monitors.views.domain_monitors import DomainMonitorsViewSet
from monitors.views.web_monitors import WebMonitorsViewSet

monitors_url = routers.SimpleRouter()
monitors_url.register(r'ssl_monitors', SSLMonitorsViewSet)
monitors_url.register(r'domain_monitors', DomainMonitorsViewSet)
monitors_url.register(r'web_monitors', WebMonitorsViewSet, basename='web_monitors')
# devops_url = routers.SimpleRouter()

urlpatterns = [
    # path('get_instance/', GetServerInstance, name='GetServerInstance'),
]

urlpatterns += monitors_url.urls
