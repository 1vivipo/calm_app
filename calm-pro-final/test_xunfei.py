"""测试讯飞API"""
import websocket
import json
import hmac
import hashlib
import base64
from urllib.parse import urlencode
from datetime import datetime, timezone
import threading
import queue

# 讯飞配置
APP_ID = "dd0c806d"
API_KEY = "f4808f28dd32ee67fab04630a60996f6"
API_SECRET = "NWQzZjM1ZDJhZjkzYjI4OWI4YjdjZGQ2"

def create_url():
    host = "spark-api.xf-yun.com"
    path = "/v1.1/chat"
    
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

result = queue.Queue()

def on_message(ws, message):
    data = json.loads(message)
    code = data.get('header', {}).get('code')
    
    if code != 0:
        result.put(f"ERROR: code={code}, msg={data.get('header', {}).get('message')}")
        ws.close()
        return
    
    content = data.get('payload', {}).get('choices', {}).get('text', [{}])[0].get('content', '')
    status = data.get('header', {}).get('status')
    
    if status == 2:
        result.put(content)
        ws.close()

def on_error(ws, error):
    result.put(f"WS_ERROR: {error}")

def on_open(ws):
    data = {
        "header": {"app_id": APP_ID, "uid": "test"},
        "parameter": {"chat": {"domain": "general", "temperature": 0.7, "max_tokens": 100}},
        "payload": {"message": {"text": [{"role": "user", "content": "你好，请说一个笑话"}]}}
    }
    ws.send(json.dumps(data))

url = create_url()
print(f"连接URL: {url[:80]}...")

ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_open=on_open)
ws_thread = threading.Thread(target=ws.run_forever)
ws_thread.daemon = True
ws_thread.start()
ws_thread.join(timeout=30)

try:
    response = result.get(timeout=5)
    print(f"\n讯飞回复: {response}")
    if "ERROR" in str(response) or "WS_ERROR" in str(response):
        print("❌ API调用失败")
    else:
        print("✅ API调用成功！")
except:
    print("❌ 请求超时")
