import json
import ldap3
import string
import random
import logging
import passlib.hash
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse

from application import dispatch
from dvadmin.system.models import Users

logger = logging.getLogger(__name__)

class LdapClass():
    def __init__(self):
        self.ldap_host = dispatch.get_system_config_values("configldap.LDAP_HOST")
        self.ldap_check_user = dispatch.get_system_config_values("configldap.LDAP_BIND_DN")
        self.ldap_check_password = dispatch.get_system_config_values("configldap.LDAP_BIND_PASSWORD")
        self.ldap_base_dn = dispatch.get_system_config_values("configldap.LDAP_BASE_DN")
        self.ldap_search_base = dispatch.get_system_config_values("configldap.SEARCH_BASE")

    def connect(self):
        """
        ldap链接
        """
        server = ldap3.Server(host=self.ldap_host, get_info=ldap3.ALL)
        # 创建LDAP连接
        conn = ldap3.Connection(server=server, user=self.ldap_check_user, password=self.ldap_check_password,
                                client_strategy='SYNC',
                                auto_bind=True)
        return conn

    def generate_password(self, length=20):
        """
        生成随机密码
        """
        characters = string.ascii_letters + string.digits + '!@#$%^&*'
        return ''.join(random.choice(characters) for _ in range(length))

    def ldap_conn(self, ldap_user, ldap_password):
        """
        检查ldap用户的信息，是否存在或账号密码是否匹配
        """
        ldap_user = ldap_user
        ldap_password = ldap_password
        logger.info(self.ldap_host)
        all_user = f'cn={ldap_user},' + str(self.ldap_search_base)
        server = ldap3.Server(host=self.ldap_host, get_info=ldap3.ALL)
        try:
            conn = ldap3.Connection(server=server, user=all_user,
                                    password=ldap_password, client_strategy='SYNC', auto_bind=True)
            conn.bind()
            return True
        except Exception as e:
            logger.info("检查ldap用户账号密码异常，请检查是否存在该用户或账号密码不匹配")
            return False


    def ldap_search_add_user(self, ldap_user, ldap_password):
        """
        检查ldap用户的信息，是否存在或账号密码是否匹配
        """
        conn = self.connect()
        # 搜索操作
        search_base = self.ldap_search_base
        search_filter = f'(&(objectclass=person)(cn={ldap_user}))'
        search_scope = ldap3.SUBTREE
        ret_attrs = ['mail', 'uid', 'givenname', 'sn']
        size_limit = 0
        time_limit = 0
        types_only = False
        deref_aliases = ldap3.DEREF_ALWAYS
        # 查询条目
        conn.search(search_base=search_base, search_filter=search_filter, search_scope=search_scope,
                    attributes=ret_attrs, size_limit=size_limit, time_limit=time_limit, types_only=types_only,
                    dereference_aliases=deref_aliases)
        if len(conn.entries) == 0:
            logger.info(f'{ldap_user}用户不存在')
        else:
            for entry in conn.entries:
                ldap_username = ldap_user
                ldap_first_name = entry.givenname
                ldap_last_name = entry.sn
                ldap_mail = entry.mail
                ldap_password = make_password(ldap_password)
                ldap_describe = "ldap用户"
                logger.info(f'数据库创建用户 {ldap_user}')
                user = Users(username=ldap_username, password=ldap_password, first_name=ldap_first_name,
                             last_name=ldap_last_name, email=ldap_mail, is_staff=1,
                             name=ldap_username, dept_id=3, description=ldap_describe)
                user.save()
                logger.info('创建完成')
        logger.info('Search operation successful')


    def ldap_addUser(self, first_name, last_name, email):
        """
        增加ldap用户
        """
        common_name = first_name + last_name
        uid_number = random.randint(10000, 99999)
        conn = self.connect()
        conn.bind()
        random_pass = self.generate_password()
        md5_random_pass = passlib.hash.ldap_md5.encrypt(random_pass)
        logging.info(f'正在添加用户{common_name}中')
        conn.add(f'cn={common_name},{self.ldap_search_base}',
                 ['inetOrgPerson', 'posixAccount', 'top'],
                 {'sn': last_name, 'givenName': first_name, 'gidNumber': '500', 'homeDirectory': f'/home/users/{common_name}', 'mail': email,
                  'uid': f'{common_name}', 'uidNumber': uid_number, 'userpassword': md5_random_pass})
        conn.unbind()
        if conn.result['result'] == 0:
            logging.info(f'添加用户{common_name}成功')
            add_user_data = {
                '用户名': f'{common_name}',
                '密码': f'{random_pass}'
            }
            return HttpResponse(json.dumps(add_user_data))
        else:
            error_detail = "用户添加失败，请到ldapadmin查看是否已经存在该用户"
            return error_detail


    def ldap_updateUserPassword(self, uid, password):
        """
        更新ldap用户密码
        """
        username = uid
        new_password = passlib.hash.ldap_md5.encrypt(password)
        conn = self.connect()
        with conn:
            conn.search(f'{self.ldap_search_base}', '(objectclass=person)', ldap3.SUBTREE,
                        attributes=['uid'])
            for entry in conn.entries:
                if entry.uid == username:
                    conn.modify(entry.entry_dn, {'userPassword': [(ldap3.MODIFY_REPLACE, [f'{new_password}'])]})
                    return HttpResponse("ok")

    def ldap_deleteUser(self, uid):
        """
        删除ldap用户信息
        """
        username = uid
        conn = self.connect()
        dn = f'cn={username},{self.ldap_search_base}'
        conn.delete(dn)
        conn.unbind()
        if conn.result['result'] == 0:
            logging.info(f'删除用户{username}成功')
            return HttpResponse(f'删除用户{username}成功')
        else:
            error_detail = "用户删除失败，查看原因"
            return error_detail

    def ldap_user(self):
        """
        获取所有ldap用户信息
        """
        search_base = self.ldap_search_base
        search_filter = f'(&(objectclass=person))'
        search_scope = ldap3.SUBTREE
        ret_attrs = ['mail', 'uid', 'givenname', 'sn', 'userpassword']
        size_limit = 0
        time_limit = 0
        types_only = False
        deref_aliases = ldap3.DEREF_ALWAYS
        # 查询条目
        conn = self.connect()
        conn.search(search_base=search_base, search_filter=search_filter, search_scope=search_scope,
                    attributes=ret_attrs, size_limit=size_limit, time_limit=time_limit, types_only=types_only,
                    dereference_aliases=deref_aliases)
        ldap_list = []
        for entry in conn.entries:
            userpassword_str = str(entry.userpassword)[2:-1]
            entry = {
                'uid': f'{entry.uid}',
                "givenname": f'{entry.givenname}',
                "sn": f'{entry.sn}',
                "mail": f'{entry.mail}',
                "password": f'{userpassword_str}'
            }
            ldap_list.append(entry)
        return ldap_list
