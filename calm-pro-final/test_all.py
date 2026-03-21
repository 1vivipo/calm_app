"""讯飞Spark X API - 完整测试"""
import websocket
import json
import hmac
import hashlib
import base64
from urllib.parse import urlencode, urlparse, parse_qs
from datetime import datetime, timezone
import threading
import queue

# 从截图的配置
APP_ID = "dd0c806d"
API_KEY = "f4808f28dd32ee67fab04630a60996f6"
API_SECRET = "NWQzZjM1ZDJhZjkzYjl4OWI4YjdjZGQ2"

def create_auth_url_v2(host, path):
    """讯飞标准鉴权 - v2版本"""
    # 生成时间戳
    now = datetime.now(timezone.utc)
    date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # 拼接签名原串
    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    
    # hmac-sha256加密
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    signature_b64 = base64.b64encode(signature).decode()
    
    # 构建authorization
    authorization_origin = f'api_key="{API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_b64}"'
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode()
    
    # 构建URL
    params = {
        "authorization": authorization,
        "date": date,
        "host": host
    }
    
    return f"wss://{host}{path}?{urlencode(params)}"

print("=" * 60)
print("讯飞Spark X API 测试")
print("=" * 60)
print(f"APP_ID:    {APP_ID}")
print(f"API_KEY:   {API_KEY}")
print(f"API_SECRET: {API_SECRET}")
print("=" * 60)

# 测试不同的端点
endpoints = [
    ("spark-api.xf-yun.com", "/x2", "Spark X2"),
    ("spark-api.xf-yun.com", "/v1/x1", "Spark X1.5"),
    ("spark-api.xf-yun.com", "/v3.5/chat", "Spark 3.5"),
    ("spark-api.xf-yun.com", "/v1.1/chat", "Spark Lite"),
]

for host, path, name in endpoints:
    print(f"\n🔍 测试 {name}: {path}")
    
    result = queue.Queue()
    url = create_auth_url_v2(host, path)
    
    def on_msg(ws, msg):
        data = json.loads(msg)
        code = data.get('header', {}).get('code', -1)
        message = data.get('header', {}).get('message', '')
        content = data.get('payload', {}).get('choices', {}).get('text', [{}])[0].get('content', '')
        status = data.get('header', {}).get('status', -1)
        
        if code == 0:
            if status == 2:
                result.put(f"✅ 成功: {content[:100]}")
                ws.close()
            else:
                print(f"  收到片段: {content[:30]}...")
        else:
            result.put(f"❌ 错误: code={code}, {message}")
            ws.close()
    
    def on_err(ws, err):
        result.put(f"❌ 连接失败: {err}")
    
    def on_open(ws):
        # 根据不同版本使用不同的domain
        domain_map = {
            "/x2": "x2",
            "/v1/x1": "x1",
            "/v3.5/chat": "generalv3.5",
            "/v1.1/chat": "general"
        }
        
        data = {
            "header": {"app_id": APP_ID, "uid": "test"},
            "parameter": {"chat": {"domain": domain_map.get(path, "general"), "temperature": 0.7}},
            "payload": {"message": {"text": [{"role": "user", "content": "你好"}]}}
        }
        ws.send(json.dumps(data))
    
    ws = websocket.WebSocketApp(
        url,
        on_message=on_msg,
        on_error=on_err,
        on_open=on_open
    )
    
    t = threading.Thread(target=ws.run_forever)
    t.daemon = True
    t.start()
    t.join(timeout=15)
    
    try:
        r = result.get(timeout=3)
        print(f"  {r}")
        if "✅" in r:
            print(f"\n🎉 找到可用端点！")
            break
    except:
        print(f"  ⏱️ 超时")

print("\n" + "=" * 60)
print("测试完成")
