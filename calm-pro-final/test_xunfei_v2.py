"""测试讯飞API - 修正版"""
import websocket
import json
import hmac
import hashlib
import base64
from urllib.parse import urlencode
from datetime import datetime, timezone
import threading
import queue

# 讯飞配置 - 使用用户提供的
APP_ID = "dd0c806d"
API_KEY = "f4808f28dd32ee67fab04630a60996f6"
API_SECRET = "NWQzZjM1ZDJhZjkzYjI4OWI4YjdjZGQ2"

def create_url(domain_version="v1.1"):
    """生成讯飞API鉴权URL"""
    host = "spark-api.xf-yun.com"
    path = f"/{domain_version}/chat"
    
    date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    
    signature_sha = hmac.new(
        API_SECRET.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
    
    authorization_origin = f'api_key="{API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    
    params = {"authorization": authorization, "date": date, "host": host}
    return f"wss://{host}{path}?{urlencode(params)}"

result_queue = queue.Queue()

def on_message(ws, message):
    data = json.loads(message)
    header = data.get('header', {})
    code = header.get('code')
    
    print(f"收到响应: code={code}")
    
    if code != 0:
        result_queue.put(f"❌ 错误: code={code}, msg={header.get('message')}")
        ws.close()
        return
    
    content = data.get('payload', {}).get('choices', {}).get('text', [{}])[0].get('content', '')
    status = header.get('status')
    
    print(f"内容片段: {content[:50]}... status={status}")
    
    if status == 2:
        result_queue.put(content)
        ws.close()

def on_error(ws, error):
    result_queue.put(f"❌ 连接错误: {error}")

def on_open(ws, domain):
    data = {
        "header": {"app_id": APP_ID, "uid": "test_user"},
        "parameter": {
            "chat": {
                "domain": domain,  # 不同版本使用不同的domain
                "temperature": 0.7,
                "max_tokens": 100
            }
        },
        "payload": {
            "message": {
                "text": [{"role": "user", "content": "你好"}]
            }
        }
    }
    print(f"发送请求: domain={domain}")
    ws.send(json.dumps(data))

# 测试不同的API版本和domain
test_configs = [
    ("v1.1", "general"),       # Lite版本
    ("v2.1", "generalv2"),     # V2.0版本
    ("v3.1", "generalv3"),     # V3.0版本
    ("v3.5", "generalv3.5"),   # V3.5版本
]

print("=" * 50)
print("测试讯飞星火API")
print(f"APP_ID: {APP_ID}")
print(f"API_KEY: {API_KEY[:10]}...")
print("=" * 50)

for version, domain in test_configs:
    print(f"\n🔍 测试 {version} / {domain}...")
    
    result_queue = queue.Queue()
    
    url = create_url(version)
    
    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=on_error,
        on_open=lambda ws: on_open(ws, domain),
    )
    
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.daemon = True
    ws_thread.start()
    ws_thread.join(timeout=15)
    
    try:
        response = result_queue.get(timeout=3)
        print(f"结果: {response[:100]}")
        if "错误" not in str(response) and "❌" not in str(response):
            print(f"✅ 成功！使用 {version} / {domain}")
            break
    except:
        print("⏱️ 超时")

print("\n" + "=" * 50)
print("测试完成")
