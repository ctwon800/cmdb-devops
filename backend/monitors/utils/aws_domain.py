import boto3

def aws_domain_list(aws_access_key_id, aws_secret_access_key):
    # 创建 Route 53 客户端

    client = boto3.client(
        'route53',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    # 获取所有的 Hosted Zones
    response = client.list_hosted_zones()
    domains_list = []
    # 打印每个 Hosted Zone 的域名
    for hosted_zone in response['HostedZones']:
        # 去掉域名的最后一个点号
        domain = hosted_zone['Name']
        if domain.endswith('.'):
            domain = domain[:-1]
        domains_list.append(domain)
    return domains_list