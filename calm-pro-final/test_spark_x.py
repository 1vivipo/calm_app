"""测试讯飞Spark X API - 正确配置"""
import websocket
import json
import hmac
import hashlib
import base64
from urllib.parse import urlencode
from datetime import datetime, timezone
import threading
import queue

# 从截图获取的正确配置
APP_ID = "dd0c806d"
API_KEY = "f4808f28dd32ee67fab04630a60996f6"
API_SECRET = "NWQzZjM1ZDJhZjkzYjl4OWI4YjdjZGQ2"  # 修正：中间是yjl4

result_queue = queue.Queue()

def create_url(version="x2"):
    """生成Spark X API鉴权URL"""
    host = "spark-api.xf-yun.com"
    path = f"/{version}"  # x2 或 v1/x1
    
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

def on_message(ws, message):
    data = json.loads(message)
    header = data.get('header', {})
    code = header.get('code')
    
    print(f"响应: code={code}")
    
    if code != 0:
        result_queue.put(f"❌ 错误: {header.get('message')}")
        ws.close()
        return
    
    content = data.get('payload', {}).get('choices', {}).get('text', [{}])[0].get('content', '')
    status = header.get('status')
    
    print(f"内容: {content}")
    
    if status == 2:
        result_queue.put(content)
        ws.close()

def on_error(ws, error):
    result_queue.put(f"❌ 连接错误: {error}")

def on_open(ws):
    data = {
        "header": {"app_id": APP_ID, "uid": "test"},
        "parameter": {"chat": {"domain": "x2", "temperature": 0.7}},
        "payload": {"message": {"text": [{"role": "user", "content": "你好，请说一个笑话"}]}}
    }
    ws.send(json.dumps(data))

print("=" * 50)
print("测试讯飞Spark X API")
print(f"APP_ID: {APP_ID}")
print(f"API_KEY: {API_KEY[:10]}...")
print(f"API_SECRET: {API_SECRET[:15]}...")
print("=" * 50)

url = create_url("x2")
print(f"\n连接: {url[:80]}...")

ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_open=on_open)
ws_thread = threading.Thread(target=ws.run_forever)
ws_thread.daemon = True
ws_thread.start()
ws_thread.join(timeout=30)

try:
    response = result_queue.get(timeout=5)
    print(f"\n✅ 成功！回复: {response}")
except:
    print("\n❌ 超时")
