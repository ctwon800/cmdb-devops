import requests
import xmltodict
import json
from datetime import datetime
import logging

base_url = 'https://api.namecheap.com/xml.response'


def get_namecheap_domain_info(api_user, api_key):
    """
    获取namecheap的域名信息
    """
    params = {
        'ApiUser': api_user,
        'ApiKey': api_key,
        'UserName': api_user,
        'Command': 'namecheap.domains.getList',
        'ClientIp': '220.12.3.12',
        'PageSize': 100
    }

    try:
        # 发送请求
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        # 将 XML 转换为字典
        data_dict = xmltodict.parse(response.text)
        domains = data_dict['ApiResponse']['CommandResponse']['DomainGetListResult']['Domain']
        # print('域名信息:', domains)
        logging.info(f"域名信息：{domains}")
        # 整理域名信息为字典格式
        domain_info_list = []
        for domain in domains:
            name = domain['@Name']
            expires = domain['@Expires']
            # 转换日期格式
            expire_date = datetime.strptime(expires, "%m/%d/%Y").strftime("%Y-%m-%d %H:%M:%S")
            domain_info = {
                "domain": name,
                "expires": expire_date
            }
            domain_info_list.append(domain_info)
        logging.info(f"NAMECHEAP域名信息: {domain_info_list}")
        return domain_info_list

    except requests.exceptions.RequestException as e:
        # print(json.dumps({"error": f"请求错误：{str(e)}"}, ensure_ascii=False))
        logging.info(f"请求错误：{str(e)}")
    except KeyError as e:
        # print(json.dumps({"error": f"数据解析错误：{str(e)}"}, ensure_ascii=False))
        logging.info(f"数据解析错误：{str(e)}")
    except Exception as e:
        # print(json.dumps({"error": f"发生错误：{str(e)}"}, ensure_ascii=False))
        logging.info(f"发生错误：{str(e)}")
