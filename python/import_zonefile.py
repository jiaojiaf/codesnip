# -*- coding: utf-8 -*-
'''
功能：
从zonefile文件导入域名到Dnspod
requirements:
dnspython==1.10.0
requests==1.0.4
'''

import sys
import dns.zone
import requests


domain = 'weplay.cn'  # 要导入的域名
domain_id = 25100001# 要导入域名的ID，在网页上获取，用Chrome的开发者工具，你懂的
record_line = u'移动'  # 线路名称，一般zonefile里没有线路信息，就写默认
login_email = 'test@dnspod.com'  # DNSPod账户
login_password = 'password'  # DNSPod密码
login_token='10665,8fc6b84d52d705879807ec781a10e2f5'


def parse_zone(zone_file):
    root = dns.zone.from_file(zone_file, origin='.', check_origin=False)

    node = root.nodes
    for rdataset in node:
        for rdata in root.get(rdataset):
            for item in rdata.items:
                sub_domain = rdataset.to_text()
                l = len(sub_domain) - len(domain)
                if sub_domain[l:] == domain:
                    sub_domain = sub_domain[:l]
                if sub_domain == '':
                    sub_domain = '@'
                sub_domain = sub_domain.rstrip('.')

                ttl = rdata.ttl
                rdtype = dns.rdatatype.to_text(rdata.rdtype)
                value = item.to_text()
                mx = 0
                
                # CNAME值没有.结尾，加上域名做后缀
                if rdtype == 'CNAME' and value.find('.') == -1:
                    value = value + '.' + domain
                if rdtype == 'MX':
                    value = value.rstrip('.')
                    value += '.'
                if rdtype not in ['NS', 'SOA']:
                    yield sub_domain, ttl, rdtype, value, mx

total = 0
def create_record(record):
    global total
    data = {'sub_domain': record[0],
            'ttl': record[1],
            'record_type': record[2],
            'value': record[3],
            'mx': record[4],
            #'login_email': login_email,
            #'login_password': login_password,
            'login_token': login_token,
            'record_line': record_line,
            'domain_id': domain_id,
            'domain': domain,
            'format': 'json',
            'error_on_empty': 'no'
            }

    r = requests.post('https://dnsapi.cn/Record.Create', data=data)
    r = r.json()
    total += 1
    print total, record, r['status']['code'], r['status']['message']

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'usage:%s zonefile [debug]' % (sys.argv[0])
        sys.exit()
    zone_file = sys.argv[1]
    debug = len(sys.argv) == 3
    records = parse_zone(zone_file)
    for record in records:
        if debug:
            print record
        else:
            create_record(record)
