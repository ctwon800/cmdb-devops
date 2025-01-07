from django.urls import path
from rest_framework import routers
# from .views.ldap import ldap_get_user, ldap_add_user, ldap_update_user, ldap_delete_user


from devops.views.ldap import LdapViewSet

devops_url = routers.SimpleRouter()
# devops_url.register(r'ldap', LdapViewSet, basename='ldap')

urlpatterns = [
    path('ldap/', LdapViewSet.as_view(), name='ldap'),
]
urlpatterns += devops_url.urls
