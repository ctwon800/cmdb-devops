import requests
import time
from datetime import datetime
import logging

def check_web_status(url, web_http_enable, web_https_enable, timeout=5):
    """
    检查URL的可访问性并返回状态，根据HTTP和HTTPS的启用状态进行检测
    """
    # 确保URL不包含协议前缀
    if url.startswith(('http://', 'https://')):
        base_url = url.split('://', 1)[1]
    else:
        base_url = url
    logging.info(f"开始检查网站状态{base_url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    results = []

    # 检查 HTTP 是否启用
    if web_http_enable:
        http_url = f"http://{base_url}"
        retry_count = 0
        max_retries = 2
        
        while retry_count < max_retries:
            try:
                http_response = requests.get(http_url, timeout=timeout, headers=headers)
                logging.info(f"\nHTTP 响应状态码: {http_response.status_code}")
                logging.info(f"HTTP 响应内容: {http_response.text[:50]}...")

                if http_response.status_code < 400:
                    results.append({
                        'protocol': 'http',
                        'status_code': http_response.status_code,
                        'response_time': http_response.elapsed.total_seconds(),
                        'http_status': True
                    })
                    logging.info(f"URL: {http_url} - 状态正常 (状态码: {http_response.status_code})")
                    break
                else:
                    logging.warning(f"URL: {http_url} - 状态异常 (状态码: {http_response.status_code})，进行第{retry_count + 1}次重试")
                    retry_count += 1
                    if retry_count >= max_retries:
                        logging.error(f"URL: {http_url} - 状态异常 (状态码: {http_response.status_code})，重试{max_retries}次后仍然失败")
                        results.append({
                            'protocol': 'http',
                            'status_code': http_response.status_code,
                            'response_time': http_response.elapsed.total_seconds(),
                            'http_status': False
                        })
                    else:
                        time.sleep(0.5)
            except requests.RequestException as e:
                logging.warning(f"HTTP访问失败: {str(e)}，进行第{retry_count + 1}次重试")
                retry_count += 1
                if retry_count >= max_retries:
                    logging.warning(f"HTTP访问失败: {str(e)}，重试{max_retries}次后仍然失败")
                    results.append({
                        'protocol': 'http',
                        'status_code': 0,
                        'response_time': 0,
                        'http_status': False
                    })
                else:
                    time.sleep(0.5)

    # 检查 HTTPS 是否启用
    if web_https_enable:
        https_url = f"https://{base_url}"
        retry_count = 0
        max_retries = 2
        
        while retry_count < max_retries:
            try:
                https_response = requests.get(https_url, timeout=timeout, headers=headers)
                logging.info(f"\nHTTPS 响应状态码: {https_response.status_code}")
                logging.info(f"HTTPS 响应内容: {https_response.text[:50]}...")

                if https_response.status_code < 400:
                    results.append({
                        'protocol': 'https',
                        'status_code': https_response.status_code,
                        'response_time': https_response.elapsed.total_seconds(),
                        'https_status': True
                    })
                    logging.info(f"URL: {https_url} - 状态正常 (状态码: {https_response.status_code})")
                    break
                else:
                    logging.warning(f"URL: {https_url} - 状态异常 (状态码: {https_response.status_code})，进行第{retry_count + 1}次重试")
                    retry_count += 1
                    if retry_count >= max_retries:
                        logging.error(f"URL: {https_url} - 状态异常 (状态码: {https_response.status_code})，重试{max_retries}次后仍然失败")
                        results.append({
                            'protocol': 'https',
                            'status_code': https_response.status_code,
                            'response_time': https_response.elapsed.total_seconds(),
                            'https_status': False
                        })
                    else:
                        time.sleep(0.5)
            except requests.RequestException as e:
                logging.warning(f"HTTPS访问失败: {str(e)}，进行第{retry_count + 1}次重试")
                retry_count += 1
                if retry_count >= max_retries:
                    logging.warning(f"HTTPS访问失败: {str(e)}，重试{max_retries}次后仍然失败")
                    results.append({
                        'protocol': 'https',
                        'status_code': 0,
                        'response_time': 0,
                        'https_status': False
                    })
                else:
                    time.sleep(0.5)

    return results
