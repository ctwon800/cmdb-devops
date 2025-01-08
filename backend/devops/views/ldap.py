import json

from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from dvadmin.system.views.ldap import LdapClass
from django.core.paginator import Paginator
from application import dispatch

class LdapViewSet(LdapClass, APIView):

    def __init__(self):
        super().__init__()

    def get(self, request, *args, **kwargs):
        try:
            my_data = self.ldap_user()
            if not my_data:  # 如果没有数据返回空列表
                return JsonResponse({
                    "code": 2000,
                    "data": {
                        "page": int(request.GET.get('page', 1)),
                        "total": 0,
                        "is_next": False,
                        "is_previous": False,
                        "limit": int(request.GET.get('limit', 20)),
                        "data": []
                    },
                    "msg": "success"
                })

            # 从数据中移除 password 字段
            my_data = [{k: v for k, v in item.items() if k != 'password'} for item in my_data]
            
            # 判断是否存在查询用户名
            if request.GET.get('uid'):
                username = request.GET.get('uid')
                my_data = [item for item in my_data if username in item['uid']]

            total = len(my_data)
            # 获取前端传来的limit参数，默认为2
            page_size = int(request.GET.get('limit', 20))
            page_number = int(request.GET.get('page'))
            paginator = Paginator(my_data, page_size)
            page_obj = paginator.get_page(page_number)
            is_next = page_obj.has_next()
            is_previous = page_obj.has_previous()
            data_list = list(page_obj)

            message = {
                "code": 2000,
                "data": {
                    "page": page_number,
                    "total": total,
                    "is_next": is_next,
                    "is_previous": is_previous,
                    "limit": page_size,
                    "data": data_list
                },
                "msg": "success"
            }
            return JsonResponse(message, safe=False)

        except Exception as e:
            # LDAP连接错误或其他异常时的处理
            return JsonResponse({
                "code": 5000,
                "msg": f"LDAP查询失败: {str(e)}",
                "data": None
            }, status=500)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        givenname = data['givenname']
        sn = data['sn']
        mail = data['mail']
        return self.ldap_addUser(givenname, sn, mail)

    def put(self, request, *args, **kwargs):
        data = json.loads(request.body)
        uid = data['uid']
        password = data['password']
        print(password)
        return self.ldap_updateUserPassword(uid, password)

    def delete(self, request, *args, **kwargs):
        username = request.body.decode()
        # data = json.loads(request.body.decode())
        # print(data)
        # username = data['uid']
        print(username)
        return self.ldap_deleteUser(username)
