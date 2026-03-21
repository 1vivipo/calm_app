"""测试讯飞Spark X HTTP API"""
import requests
import time
import hmac
import hashlib
import base64
from datetime import datetime, timezone

# 配置
API_KEY = "f4808f28dd32ee67fab04630a60996f6"
API_SECRET = "NWQzZjM1ZDJhZjkzYjl4OWI4YjdjZGQ2"

# HTTP接口地址（从截图）
url_x2 = "https://spark-api-open.xf-yun.com/x2/chat/completions"
url_x15 = "https://spark-api-open.xf-yun.com/v2/chat/completions"

def create_auth_header():
    """生成鉴权头"""
    date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # 签名原串
    signature_origin = f"host: spark-api-open.xf-yun.com\ndate: {date}\nGET /x2/chat/completions HTTP/1.1"
    
    # HMAC-SHA256签名
    signature_sha = hmac.new(
        API_SECRET.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
    
    # Authorization
    authorization_origin = f'api_key="{API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    
    return {
        "Authorization": authorization,
        "Date": date,
        "Host": "spark-api-open.xf-yun.com"
    }

print("=" * 50)
print("测试讯飞Spark X HTTP API")
print("=" * 50)

# 测试X2
headers = create_auth_header()
print(f"\n请求头: Authorization={headers['Authorization'][:50]}...")

payload = {
    "model": "x2",
    "messages": [{"role": "user", "content": "你好"}],
    "stream": False
}

try:
    resp = requests.post(url_x2, headers=headers, json=payload, timeout=30)
    print(f"\n状态码: {resp.status_code}")
    print(f"响应: {resp.text[:500]}")
except Exception as e:
    print(f"❌ 错误: {e}")

# 也试试直接用APIKey作为Bearer Token
print("\n" + "=" * 50)
print("试试Bearer Token方式...")

try:
    resp = requests.post(
        url_x2,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "x2", "messages": [{"role": "user", "content": "你好"}]},
        timeout=30
    )
    print(f"状态码: {resp.status_code}")
    print(f"响应: {resp.text[:500]}")
except Exception as e:
    print(f"错误: {e}")
