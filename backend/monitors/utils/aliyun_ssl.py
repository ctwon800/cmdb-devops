import json

from alibabacloud_cas20200407 import models as cas_20200407_models
from alibabacloud_cas20200407.client import Client as cas20200407Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


class AliyunSSL:
    def __init__(self):
        pass

    @staticmethod
    def create_client(accesskey_id, accesskey_secret) -> cas20200407Client:
        """
        使用AK&SK初始化账号Client
        @return: Client
        @throws Exception
        """
        # 工程代码泄露可能会导致 AccessKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考。
        # 建议使用更安全的 STS 方式，更多鉴权访问方式请参见：https://help.aliyun.com/document_detail/378659.html。
        config = open_api_models.Config(
            # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID。,
            # access_key_id=os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],
            access_key_id=accesskey_id,
            # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_SECRET。,
            # access_key_secret=os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET']
            access_key_secret=accesskey_secret
        )
        # Endpoint 请参考 https://api.aliyun.com/product/cas
        config.endpoint = f'cas.aliyuncs.com'
        return cas20200407Client(config)

    @staticmethod
    def main(accesskey_id, accesskey_secret):
        client = AliyunSSL.create_client(accesskey_id, accesskey_secret)
        list_user_certificate_order_request = cas_20200407_models.ListUserCertificateOrderRequest(
            show_size=100
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            res = client.list_user_certificate_order_with_options(list_user_certificate_order_request, runtime).body
            # 对该api返回值转换成json
            # print(res.body.code)
            tran_data = UtilClient.to_jsonstring(res)

            json_data = json.loads(tran_data)
            return json_data['CertificateOrderList']

        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)


