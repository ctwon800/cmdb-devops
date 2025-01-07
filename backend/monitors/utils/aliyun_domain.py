# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os
import sys
import json
from typing import List

from alibabacloud_domain20180129.client import Client as Domain20180129Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_domain20180129 import models as domain_20180129_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


class AliyunDomain:
    def __init__(self):
        pass

    @staticmethod
    def create_client(accesskey_id, accesskey_secret) -> Domain20180129Client:
        """
        使用AK&SK初始化账号Client
        @return: Client
        @throws Exception
        """
        # 工程代码泄露可能会导致 AccessKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考。
        # 建议使用更安全的 STS 方式，更多鉴权访问方式请参见：https://help.aliyun.com/document_detail/378659.html。
        config = open_api_models.Config(
            # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID。,
            access_key_id=accesskey_id,
            # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_SECRET。,
            access_key_secret=accesskey_secret

        )
        # Endpoint 请参考 https://api.aliyun.com/product/Domain
        config.endpoint = f'domain.aliyuncs.com'
        return Domain20180129Client(config)

    @staticmethod
    def main(accesskey_id, accesskey_secret):
        client = AliyunDomain.create_client(accesskey_id, accesskey_secret)
        query_domain_list_request = domain_20180129_models.QueryDomainListRequest(
            page_num=1,
            page_size=1000
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = client.query_domain_list_with_options(query_domain_list_request, runtime).body
            res_data = UtilClient.to_jsonstring(resp)
            return res_data

        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)



if __name__ == '__main__':
    AliyunDomain.main(sys.argv[1:])
