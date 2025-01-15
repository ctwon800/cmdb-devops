from django.urls import path
from rest_framework import routers

from .views import  TaskResultsViewSet, PeriodicTaskListViewSet, BatchCommandRecordViewSet

task_url = routers.SimpleRouter()
task_url.register(r'task_results', TaskResultsViewSet)
task_url.register(r'task', PeriodicTaskListViewSet)
task_url.register(r'batch_command_record', BatchCommandRecordViewSet)

urlpatterns = [

]

urlpatterns += task_url.urls
