import hashlib
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone

from dvadmin.system.views import user
from dvadmin.utils.validator import CustomValidationError

from dvadmin.system.views.ldap import LdapClass
from application import dispatch


logger = logging.getLogger(__name__)
UserModel = get_user_model()



class CustomBackend(ModelBackend, LdapClass):
    """
    Django原生认证方式
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        msg = '%s 正在登录...' % username
        logger.info(msg)

        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            logger.info(f'{username}用户在本地不存在')
            if dispatch.get_system_config_values("configldap.ldap_enable"):
                if self.ldap_conn(username, password):
                    # ldap用户登录成功后，同时创建本地的账号
                    logger.info(f'{username}用户存在于ldap中，准备开始cmdb数据库中创建用户')
                    self.ldap_search_add_user(username, password)
                    logger.info(f'本地创建用户 {username} 成功')
                else:
                    raise CustomValidationError("无LDAP账号或者LDAP账号密码不正确，请核实后再重新登陆!")
                logger.info(f'{username} 用户准备重新进行登录')
                user = UserModel._default_manager.get_by_natural_key(username)
                if self.check_password_new(username, password):
                    return user
            else:
                UserModel().set_password(password)
        else:
            if username == "superadmin":
                if self.check_password_new(username, password):
                    return user
            else:
                if dispatch.get_system_config_values("configldap.ldap_enable"):
                    if self.ldap_conn(username, password):
                        if self.check_password_new(username, password):
                            return user
                    else:
                        raise CustomValidationError("无LDAP账号或者LDAP账号密码不正确，请核实后再重新登陆!!!")
                else:
                    if self.check_password_new(username, password):
                        return user

    def check_password_new(self, username, password):
        user = UserModel._default_manager.get_by_natural_key(username)
        verify_password = check_password(password, user.password)
        if not verify_password:
            password = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()
            verify_password = check_password(password, user.password)
        if verify_password:
            if self.user_can_authenticate(user):
                user.last_login = timezone.now()
                user.save()
                return True
            raise CustomValidationError("当前用户已被禁用，请联系管理员!")


    # def authenticate(self, request, username=None, password=None, **kwargs):
    #     print(request)
    #     print(**kwargs)
    #     if dispatch.get_system_config_values("base.single_login"):
    #         print("开启成功")
    #     else:
    #         print("开启失败")
    #     msg = '%s 正在使用本地登录...' % username
    #     logger.info(msg)
    #     logger.info("777")
    #     if username is None:
    #         username = kwargs.get(UserModel.USERNAME_FIELD)
    #     try:
    #         user = UserModel._default_manager.get_by_natural_key(username)
    #         print(user)
    #     except UserModel.DoesNotExist:
    #         UserModel().set_password(password)
    #         # default_error_messages = {"no_active_account": _("账号/密码错误")}
    #     else:
    #         print("同步ldap用户")
    #         ldap_search()
    #         print(user.password)
    #         verify_password = check_password(password, user.password)
    #         print(verify_password)
    #         if not verify_password:
    #             password = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()
    #             print('当前用户的密码: ', password)
    #             print(user.password)
    #             verify_password = check_password(password, user.password)
    #         if verify_password:
    #             if self.user_can_authenticate(user):
    #                 user.last_login = timezone.now()
    #                 user.save()
    #                 return user
    #             raise CustomValidationError("当前用户已被禁用，请联系管理员!")
