"""讯飞Spark X HTTP API - 正确签名"""
import requests
import hmac
import hashlib
import base64
from datetime import datetime, timezone

# 配置
API_KEY = "f4808f28dd32ee67fab04630a60996f6"
API_SECRET = "NWQzZjM1ZDJhZjkzYjl4OWI4YjdjZGQ2"

def create_auth(path):
    """生成鉴权信息"""
    host = "spark-api-open.xf-yun.com"
    date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # 签名原串
    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    
    # HMAC-SHA256
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature_b64 = base64.b64encode(signature).decode()
    
    # Authorization
    auth_origin = f'api_key="{API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_b64}"'
    authorization = base64.b64encode(auth_origin.encode('utf-8')).decode()
    
    return {
        "Authorization": authorization,
        "Date": date,
        "Host": host,
        "Content-Type": "application/json"
    }

print("=" * 60)
print("讯飞Spark X HTTP API - 正确签名")
print("=" * 60)

# 测试X2
url = "https://spark-api-open.xf-yun.com/x2/chat/completions"
path = "/x2/chat/completions"

headers = create_auth(path)
print(f"\n请求URL: {url}")
print(f"Authorization: {headers['Authorization'][:60]}...")
print(f"Date: {headers['Date']}")

data = {
    "model": "x2",
    "messages": [{"role": "user", "content": "你好"}]
}

try:
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"\n状态码: {resp.status_code}")
    print(f"响应: {resp.text}")
except Exception as e:
    print(f"错误: {e}")

# 测试X1.5
print("\n" + "-" * 60)
url2 = "https://spark-api-open.xf-yun.com/v2/chat/completions"
path2 = "/v2/chat/completions"
headers2 = create_auth(path2)
data2 = {"model": "x1.5", "messages": [{"role": "user", "content": "你好"}]}

print(f"\n请求URL: {url2}")
try:
    resp = requests.post(url2, headers=headers2, json=data2, timeout=30)
    print(f"状态码: {resp.status_code}")
    print(f"响应: {resp.text}")
except Exception as e:
    print(f"错误: {e}")
