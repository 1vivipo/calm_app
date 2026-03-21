"""
🌊 平静 Pro - 多模型支持版
支持：讯飞星火、文心一言、通义千问等
用户可自行配置API Key
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
import requests

# ================== 页面配置 ==================
st.set_page_config(
    page_title="平静 Pro - AI助手",
    page_icon="🌊",
    layout="wide"
)

# ================== 样式 ==================
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.main-title {
    font-size: 2.5rem;
    font-weight: bold;
    color: #4A90E2;
    text-align: center;
}
.config-box {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    margin: 20px 0;
}
@media (max-width: 768px) {
    .main-title { font-size: 1.8rem; }
}
</style>
""", unsafe_allow_html=True)

# ================== 初始化状态 ==================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_configured" not in st.session_state:
    st.session_state.api_configured = False

# ================== 侧边栏配置 ==================
with st.sidebar:
    st.markdown("### 🌊 平静 Pro")
    st.caption("可配置多种AI模型")
    
    st.divider()
    
    # 模型选择
    model_type = st.selectbox(
        "选择模型",
        ["讯飞星火Lite（免费）", "讯飞星火3.5", "文心一言", "通义千问"]
    )
    
    # API配置
    if "讯飞" in model_type:
        st.markdown("#### 讯飞API配置")
        st.caption("从 [讯飞开放平台](https://console.xfyun.cn/) 获取")
        
        xunfei_appid = st.text_input("APP ID", type="password", key="xunfei_appid")
        xunfei_apikey = st.text_input("API Key", type="password", key="xunfei_apikey")
        xunfei_apisecret = st.text_input("API Secret", type="password", key="xunfei_apisecret")
        
        if st.button("保存配置", use_container_width=True):
            if xunfei_appid and xunfei_apikey and xunfei_apisecret:
                st.session_state.xunfei = {
                    "appid": xunfei_appid,
                    "apikey": xunfei_apikey,
                    "apisecret": xunfei_apisecret,
                    "model": "generalv3.5" if "3.5" in model_type else "general"
                }
                st.session_state.api_configured = True
                st.success("✅ 配置已保存！")
            else:
                st.error("请填写完整配置")
    
    elif model_type == "文心一言":
        st.markdown("#### 文心一言配置")
        st.caption("从 [百度智能云](https://console.bce.baidu.com/qianfan/) 获取")
        
        wenxin_ak = st.text_input("API Key", type="password", key="wenxin_ak")
        wenxin_sk = st.text_input("Secret Key", type="password", key="wenxin_sk")
        
        if st.button("保存配置", use_container_width=True):
            if wenxin_ak and wenxin_sk:
                st.session_state.wenxin = {"ak": wenxin_ak, "sk": wenxin_sk}
                st.session_state.api_configured = True
                st.success("✅ 配置已保存！")
            else:
                st.error("请填写完整配置")
    
    elif model_type == "通义千问":
        st.markdown("#### 通义千问配置")
        st.caption("从 [阿里云](https://dashscope.console.aliyun.com/) 获取")
        
        qwen_key = st.text_input("API Key", type="password", key="qwen_key")
        
        if st.button("保存配置", use_container_width=True):
            if qwen_key:
                st.session_state.qwen = {"apikey": qwen_key}
                st.session_state.api_configured = True
                st.success("✅ 配置已保存！")
            else:
                st.error("请填写完整配置")
    
    st.divider()
    
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.session_state.messages:
        history = "\n\n".join([f"{'👤' if m['role']=='user' else '🌊'}: {m['content']}" for m in st.session_state.messages])
        st.download_button("💾 导出", history, file_name="calm_chat.md", use_container_width=True)

# ================== 讯飞API调用 ==================
def call_xunfei(question: str, history: list = None) -> str:
    """调用讯飞星火API"""
    config = st.session_state.get("xunfei", {})
    
    result_queue = queue.Queue()
    
    def create_url():
        host = "spark-api.xf-yun.com"
        # 根据模型选择不同的API版本
        if "v3.5" in config.get("model", ""):
            path = "/v3.5/chat"
        else:
            path = "/v1.1/chat"
        
        date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
        
        signature_sha = hmac.new(
            config["apisecret"].encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
        
        authorization_origin = f'api_key="{config["apikey"]}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        
        params = {"authorization": authorization, "date": date, "host": host}
        return f"wss://{host}{path}?{urlencode(params)}"
    
    def on_message(ws, message):
        data = json.loads(message)
        code = data.get('header', {}).get('code')
        
        if code != 0:
            result_queue.put(f"❌ 错误: {data.get('header', {}).get('message', '未知错误')}")
            ws.close()
            return
        
        content = data.get('payload', {}).get('choices', {}).get('text', [{}])[0].get('content', '')
        status = data.get('header', {}).get('status')
        
        if status == 2:
            result_queue.put(content)
            ws.close()
    
    def on_error(ws, error):
        result_queue.put(f"❌ 连接错误: {str(error)}")
    
    def on_open(ws):
        messages = []
        if history:
            for msg in history[-6:]:  # 保留最近3轮对话
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": question})
        
        data = {
            "header": {"app_id": config["appid"], "uid": "calm_user"},
            "parameter": {"chat": {"domain": config.get("model", "general"), "temperature": 0.7, "max_tokens": 2048}},
            "payload": {"message": {"text": messages}}
        }
        
        ws.send(json.dumps(data))
    
    url = create_url()
    ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_open=on_open)
    
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.daemon = True
    ws_thread.start()
    ws_thread.join(timeout=30)
    
    try:
        return result_queue.get(timeout=5)
    except:
        return "❌ 请求超时，请重试"

# ================== 文心API调用 ==================
def call_wenxin(question: str, history: list = None) -> str:
    """调用文心一言API"""
    config = st.session_state.get("wenxin", {})
    
    # 获取access token
    token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={config['ak']}&client_secret={config['sk']}"
    
    try:
        token_resp = requests.post(token_url)
        token = token_resp.json().get("access_token")
        
        if not token:
            return "❌ 获取Token失败，请检查API Key"
        
        # 调用模型
        messages = []
        if history:
            for msg in history[-6:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": question})
        
        api_url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={token}"
        
        resp = requests.post(api_url, json={"messages": messages})
        return resp.json().get("result", "❌ 调用失败")
    
    except Exception as e:
        return f"❌ 错误: {str(e)}"

# ================== 通义API调用 ==================
def call_qwen(question: str, history: list = None) -> str:
    """调用通义千问API"""
    config = st.session_state.get("qwen", {})
    
    messages = []
    if history:
        for msg in history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": question})
    
    try:
        resp = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            headers={
                "Authorization": f"Bearer {config['apikey']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen-turbo",
                "input": {"messages": messages}
            }
        )
        
        return resp.json().get("output", {}).get("text", "❌ 调用失败")
    
    except Exception as e:
        return f"❌ 错误: {str(e)}"

# ================== 主界面 ==================
st.markdown("<h1 class='main-title'>🌊 平静 Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray'>你的AI助手 | 多模型支持 | 自定义配置</p>", unsafe_allow_html=True)

st.divider()

# 未配置提示
if not st.session_state.api_configured:
    st.warning("""
    ⚠️ **请先配置API Key**
    
    在左侧边栏选择模型并填写API配置，即可开始使用。
    
    **推荐免费方案：**
    - 🔹 **讯飞星火Lite**：永久免费，需要注册讯飞开放平台
    - 🔹 **通义千问**：有免费额度，需要注册阿里云
    
    **获取方式：**
    - 讯飞：https://console.xfyun.cn/ → 创建应用 → 获取API Key
    - 通义：https://dashscope.console.aliyun.com/ → 开通服务 → 获取API Key
    """)

# 聊天历史
for msg in st.session_state.messages:
    is_user = msg["role"] == "user"
    with st.chat_message("user" if is_user else "assistant", avatar="👤" if is_user else "🌊"):
        st.markdown(msg["content"])

# 用户输入
user_input = st.chat_input("输入消息...")

if user_input and st.session_state.api_configured:
    # 用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    # AI回复
    with st.chat_message("assistant", avatar="🌊"):
        with st.spinner("思考中..."):
            history = st.session_state.messages[:-1] if len(st.session_state.messages) > 1 else None
            
            # 根据模型类型调用不同API
            if "讯飞" in model_type:
                response = call_xunfei(user_input, history)
            elif model_type == "文心一言":
                response = call_wenxin(user_input, history)
            else:
                response = call_qwen(user_input, history)
            
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

elif user_input and not st.session_state.api_configured:
    st.error("⚠️ 请先在左侧配置API Key")

# ================== 页脚 ==================
st.divider()
st.caption("🌊 平静 Pro | 多模型支持 | 自定义配置")
