# 项目名称
<h1 align="center" color="#fff">运维管理后台</h1>

## 📝 项目介绍

主要为cmdb的模块内容，主要是个人爱好开发使用，不涉及商业使用。
* 🧑‍🤝‍🧑 前端采用 D2Admin 、Vue2、ElementUI。
* 👭 后端采用 Python 语言 Django 框架以及强大的 Django REST Framework。
* 👫 权限认证使用 Django REST Framework SimpleJWT，支持多终端认证系统。

## ✨ 主要功能

- 基本的后台管理模块，权限管理、用户管理、角色管理、菜单管理、日志管理、系统配置等，具体的可参考 [文档](https://github.com/liqianglog/django-vue-admin/blob/main/README.zh.md)。
- 资产管理：服务器管理，云账号管理，账号费用管理，远程账号管理，录像回放，服务器远程连接webssh等
- 任务管理：任务管理，任务执行记录等
- 资源监控：站点监控，证书监控，域名监控等
- 容器管理(k8s): 多集群，多节点，应用，服务，ingress等的简单管理
- 支持LDAP登录和LDAP用户的管理

## 🚀 快速开始
开发环境：
* 前端： node 16.x
* 后端： python3.9以上
* 数据库： mysql 推荐8.0以上
* redis: 5版本以上都行(如不使用celery可不使用)

```bash
git clone https://github.com/ctwon800/cmdb-devops.git
cd cmdb-devops
docker-compose up -d
# 进入容器初始化
docker exec -it cmdb-backend /bin/bash
python manage.py makemigrations
python manage.py migrate
python manage.py init
```
* 访问方式： http://127.0.0.1:8001/
* 默认用户名：superadmin 密码：admin123456

## 在线演示
https://cmdb.ctwon800.top
- 用户名：superadmin  
- 密码：admin123456 (请不要修改)


## 功能介绍
#### 资产管理：服务器管理，云账号管理，账号费用管理，远程账号管理，录像回放，服务器远程连接webssh等

主要还是通过云账号的密钥形式来自动获取云服务器等资源，新增一个账号后，可以绑定对应的服务器，可以进行webssh的操作并录像等。

#### 任务管理：任务管理，任务执行记录等
管理运维在服务器上一些定时任务之类的，可以进行批量操作，也可以进行单个操作。

#### 资源监控：站点监控，证书监控，域名监控等
站点监控：目前主要通过调用k8s的集群来获取到ingress里面host信息，对host进行监控，当然也可以进行自定义的添加站点uri等进行监控

证书监控：1. 通过调用k8s的集群来获取到ingress里面tls中的host信息，在对host进行证书的到期监控，钉钉告警方式告警
        2. 通过调用阿里云免费证书服务来获取到证书信息，并监控证书的过期时间等，钉钉告警方式告警

域名监控：自动获取阿里云，aws，namecheap的域名信息，并监控域名的过期时间等，钉钉告警方式告警

#### 容器管理(k8s): 多集群，多节点，应用，服务，ingress等的简单管理
主要通过k8s的集群来获取到集群信息，节点信息，应用信息，服务信息，ingress信息等，可以进行批量操作，也可以进行简易的监控

当然也有一些特殊的地方，例如我们在排空节点时，一般都是强行排水，意味着如没有负载的情况下，导致服务暂时不可能，所以在排空节点时，会根据每一个容器组找到对应deployment信息，如果只有一个副本的情况下会重启deployment，多个副本的情况下，可直接删除该容器组，这样就保证了服务的可持续运行

#### 支持LDAP登录和LDAP用户的管理
cmdb可通过LDAP进行登录，开启对应菜单功能，可简单管理用户信息，多角色组的情况下不适用