"""测试API Secret的不同变体"""
import requests
import hmac
import hashlib
import base64
from datetime import datetime, timezone

API_KEY = "f4808f28dd32ee67fab04630a60996f6"

# 原始版本
original = "NWQzZjM1ZDJhZjkzYjl4OWI4YjdjZGQ2"

# 可能的变体（O↔0, I↔1, l↔1）
variants = [
    original,  # 原始
    original.replace('O', '0'),  # O->0
    original.replace('I', '1'),  # I->1
    original.replace('l', '1'),  # l->1
    original.replace('OWI4', '0WI4'),  # O->0 in OWI4
    original.replace('OWI4', 'OW14'),  # I->1 in OWI4
    original.replace('Yjl4', 'Yj14'),  # l->1 in Yjl4
]

url = "https://spark-api-open.xf-yun.com/x2/chat/completions"

def test_secret(secret, name):
    host = "spark-api-open.xf-yun.com"
    path = "/x2/chat/completions"
    date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    sig_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    sig = hmac.new(secret.encode(), sig_origin.encode(), hashlib.sha256).digest()
    sig_b64 = base64.b64encode(sig).decode()
    
    auth_origin = f'api_key="{API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{sig_b64}"'
    auth = base64.b64encode(auth_origin.encode()).decode()
    
    headers = {"Authorization": auth, "Date": date, "Host": host, "Content-Type": "application/json"}
    data = {"model": "x2", "messages": [{"role": "user", "content": "hi"}]}
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        return resp.status_code, resp.text[:100]
    except Exception as e:
        return None, str(e)

print("=" * 60)
print("测试API Secret变体")
print("=" * 60)

for i, secret in enumerate(variants):
    name = f"变体{i+1}" if i > 0 else "原始"
    print(f"\n{name}: {secret}")
    code, resp = test_secret(secret, name)
    print(f"状态码: {code}, 响应: {resp[:80]}...")
    
    if code == 200:
        print(f"\n✅ 找到正确的Secret！")
        print(f"正确的API_SECRET = {secret}")
        break

print("\n" + "=" * 60)
