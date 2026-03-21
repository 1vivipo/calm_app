"""
🌊 平静 - 超简单版
直接在网页上输入API Key即可使用
"""
import streamlit as st
import websocket
import json
import hmac
import hashlib
import base64
from urllib.parse import urlencode
from datetime import datetime, timezone
import threading
import queue

st.set_page_config(page_title="平静", page_icon="🌊", layout="wide")

# 隐藏菜单
st.markdown("<style>#MainMenu,footer,header{visibility:hidden;}</style>", unsafe_allow_html=True)

# 初始化
if "msgs" not in st.session_state:
    st.session_state.msgs = []

# 侧边栏 - API配置
with st.sidebar:
    st.markdown("### 🌊 平静")
    
    # 模型选择
    model = st.selectbox("模型", ["星火Lite(免费)", "星火X2", "星火X1.5"])
    
    # API Key输入
    st.markdown("---")
    st.markdown("**API配置**")
    appid = st.text_input("APP ID", type="password")
    apikey = st.text_input("API Key", type="password")
    apisecret = st.text_input("API Secret", type="password")
    
    configured = bool(appid and apikey and apisecret)
    
    if configured:
        st.success("✅ 已配置")
    else:
        st.warning("⚠️ 请输入API配置")
    
    st.markdown("---")
    st.markdown("""
    **获取免费API Key：**
    1. 访问 [讯飞控制台](https://console.xfyun.cn/)
    2. 创建应用 → 选择「星火Lite」
    3. 复制 APP ID、API Key、API Secret
    """)
    
    st.markdown("---")
    if st.button("清空对话"):
        st.session_state.msgs = []
        st.rerun()

# 标题
st.markdown("<h1 style='text-align:center;color:#4A90E2'>🌊 平静</h1>", unsafe_allow_html=True)

# 调用API
def chat(msg):
    if not configured:
        return "⚠️ 请先在左侧配置API Key"
    
    # 确定端点
    model_map = {
        "星火Lite(免费)": ("v1.1/chat", "general"),
        "星火X2": ("x2", "x2"),
        "星火X1.5": ("v1/x1", "x1")
    }
    path, domain = model_map.get(model, ("v1.1/chat", "general"))
    
    host = "spark-api.xf-yun.com"
    date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # 生成签名
    sig_origin = f"host: {host}\ndate: {date}\nGET /{path} HTTP/1.1"
    sig = hmac.new(apisecret.encode(), sig_origin.encode(), hashlib.sha256).digest()
    sig_b64 = base64.b64encode(sig).decode()
    
    auth_origin = f'api_key="{apikey}", algorithm="hmac-sha256", headers="host date request-line", signature="{sig_b64}"'
    auth = base64.b64encode(auth_origin.encode()).decode()
    
    url = f"wss://{host}/{path}?{urlencode({'authorization':auth,'date':date,'host':host})}"
    
    result = queue.Queue()
    
    def on_msg(ws, m):
        d = json.loads(m)
        code = d.get('header', {}).get('code', -1)
        if code != 0:
            result.put(f"❌ 错误: {d.get('header', {}).get('message', '未知')}")
            ws.close()
            return
        content = d.get('payload', {}).get('choices', {}).get('text', [{}])[0].get('content', '')
        if d.get('header', {}).get('status') == 2:
            result.put(content)
            ws.close()
    
    def on_err(ws, e):
        result.put(f"❌ 连接失败: {e}")
    
    def on_open(ws):
        data = {
            "header": {"app_id": appid, "uid": "u"},
            "parameter": {"chat": {"domain": domain, "temperature": 0.7}},
            "payload": {"message": {"text": [{"role": "user", "content": msg}]}}
        }
        ws.send(json.dumps(data))
    
    ws = websocket.WebSocketApp(url, on_message=on_msg, on_error=on_err, on_open=on_open)
    t = threading.Thread(target=ws.run_forever)
    t.daemon = True
    t.start()
    t.join(timeout=30)
    
    try:
        return result.get(timeout=5)
    except:
        return "❌ 请求超时"

# 显示历史
for m in st.session_state.msgs:
    with st.chat_message("user" if m["role"]=="user" else "assistant", avatar="👤" if m["role"]=="user" else "🌊"):
        st.markdown(m["content"])

# 输入
if inp := st.chat_input("输入消息..."):
    st.session_state.msgs.append({"role": "user", "content": inp})
    with st.chat_message("user", avatar="👤"):
        st.markdown(inp)
    
    with st.chat_message("assistant", avatar="🌊"):
        with st.spinner("思考中..."):
            reply = chat(inp)
            st.markdown(reply)
    
    st.session_state.msgs.append({"role": "assistant", "content": reply})

st.markdown("---")
st.caption("🌊 平静 | 配置你的API Key即可使用")
