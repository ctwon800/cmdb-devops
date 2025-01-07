import logging

import requests
import json
import time
import hmac
import hashlib
import base64


def send_dingtalk_message(content, access_token, secret):
    webhook_url = 'https://oapi.dingtalk.com/robot/send'

    timestamp = str(round(time.time() * 1000))
    sign_str = f"{timestamp}\n{secret}"
    sign = base64.b64encode(hmac.new(secret.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha256).digest()).decode(
        'utf-8')

    headers = {
        'Content-Type': 'application/json',
    }

    params = {
        'access_token': access_token,
        'timestamp': timestamp,
        'sign': sign
    }

    message = {
        "msgtype": "markdown",
        "markdown": {
            "title": "通知",
            "text": f"# {content}"
        }
    }

    response = requests.post(webhook_url, headers=headers, params=params, data=json.dumps(message))

    if response.status_code == 200:
        logging.info("钉钉消息发送成功")
    else:
        logging.info("钉钉消息发送成功")

