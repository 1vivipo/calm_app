"""讯飞Spark X - 尝试多种签名方式"""
import requests
import hmac
import hashlib
import base64
from datetime import datetime, timezone
import hashlib as md5_hash

API_KEY = "f4808f28dd32ee67fab04630a60996f6"
API_SECRET = "NWQzZjM1ZDJhZjkzYjl4OWI4YjdjZGQ2"

def test_method_1():
    """方式1：标准签名"""
    host = "spark-api-open.xf-yun.com"
    path = "/x2/chat/completions"
    date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    sig_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    sig = hmac.new(API_SECRET.encode(), sig_origin.encode(), hashlib.sha256).digest()
    sig_b64 = base64.b64encode(sig).decode()
    
    auth_origin = f'api_key="{API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{sig_b64}"'
    auth = base64.b64encode(auth_origin.encode()).decode()
    
    return {"Authorization": auth, "Date": date, "Host": host}

def test_method_2():
    """方式2：简化签名（只有host和date）"""
    host = "spark-api-open.xf-yun.com"
    date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    sig_origin = f"host: {host}\ndate: {date}"
    sig = hmac.new(API_SECRET.encode(), sig_origin.encode(), hashlib.sha256).digest()
    sig_b64 = base64.b64encode(sig).decode()
    
    auth_origin = f'api_key="{API_KEY}", algorithm="hmac-sha256", headers="host date", signature="{sig_b64}"'
    auth = base64.b64encode(auth_origin.encode()).decode()
    
    return {"Authorization": auth, "Date": date, "Host": host}

def test_method_3():
    """方式3：使用MD5"""
    host = "spark-api-open.xf-yun.com"
    date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    path = "/x2/chat/completions"
    
    sig_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    sig = hmac.new(API_SECRET.encode(), sig_origin.encode(), hashlib.sha256).hexdigest()
    
    return {"Authorization": f"hmac username=\"{API_KEY}\", algorithm=\"hmac-sha256\", signature=\"{sig}\"", "Date": date, "Host": host}

def test_method_4():
    """方式4：直接API Key + 时间戳签名"""
    host = "spark-api-open.xf-yun.com"
    timestamp = str(int(datetime.now().timestamp()))
    
    sig = hmac.new(API_SECRET.encode(), f"{API_KEY}{timestamp}".encode(), hashlib.sha256).hexdigest()
    
    return {"X-API-Key": API_KEY, "X-Timestamp": timestamp, "X-Signature": sig}

url = "https://spark-api-open.xf-yun.com/x2/chat/completions"
data = {"model": "x2", "messages": [{"role": "user", "content": "hi"}]}

print("=" * 60)
print("尝试多种签名方式")
print("=" * 60)

for i, method in enumerate([test_method_1, test_method_2, test_method_3, test_method_4], 1):
    print(f"\n方式 {i}: {method.__doc__.strip()}")
    headers = method()
    headers["Content-Type"] = "application/json"
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"状态码: {resp.status_code}")
        if resp.status_code == 200:
            print(f"✅ 成功！响应: {resp.json()}")
            break
        else:
            print(f"响应: {resp.text[:200]}")
    except Exception as e:
        print(f"错误: {e}")

print("\n" + "=" * 60)
