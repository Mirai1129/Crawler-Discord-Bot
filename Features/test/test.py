import requests
import re

# 获取代理IP
response = requests.get("https://www.sslproxies.org/")
proxy_ips = re.findall('\d+\.\d+\.\d+\.\d+:\d+', response.text)

# 遍历代理IP列表
for ip in proxy_ips:
    try:
        # 设置代理并访问网页
        result = requests.get('https://www.dcard.tw/f/relationship',
                              proxies={'http': 'http://' + ip, 'https': 'https://' + ip},
                              timeout=10)

        # 检查响应状态码
        if result.status_code == 200:
            print(f"Proxy {ip} works!")
        else:
            print(f"Proxy {ip} failed.")
    except:
        print(f"Proxy {ip} invalid.")
