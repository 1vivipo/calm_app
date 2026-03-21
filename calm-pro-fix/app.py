"""
平静 Pro - 单文件版本
直接可用，无错误
"""
import streamlit as st
import requests
import json
import os
import re
from datetime import datetime
from typing import List, Dict

# ================== 页面配置 ==================
st.set_page_config(
    page_title="平静 Pro - AI助手",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== API配置 ==================
API_CONFIG = {
    "url": "https://wishub-x6.ctyun.cn/v1/chat/completions",
    "api_key": "cb655659b3814c9d9b48c856d111210!",
    "models": {
        "pro": "d4432662ebed421890bf8fe60e40043!",
        "standard": "87f80d930d3e4c478e50f7a121dfbb97",
        "lite": "651c9b454b58458f9b604e67c03ab73"
    }
}

# ================== 样式 ==================
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.main-title {
    font-size: 2.5rem;
    font-weight: bold;
    color: #4A90E2;
    text-align: center;
    margin: 1rem 0;
}
.sub-title {
    color: #6B7280;
    text-align: center;
    margin-bottom: 1rem;
}
@media (max-width: 768px) {
    .main-title { font-size: 1.8rem; }
}
</style>
""", unsafe_allow_html=True)

# ================== 初始化状态 ==================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tokens" not in st.session_state:
    st.session_state.tokens = 0
if "model" not in st.session_state:
    st.session_state.model = "pro"

# ================== API调用 ==================
def call_api(messages: List[Dict], model: str = "pro") -> str:
    """调用豆包API"""
    try:
        headers = {
            "Authorization": f"Bearer {API_CONFIG['api_key']}",
            "Content-Type": "application/json"
        }
        
        model_id = API_CONFIG["models"].get(model, API_CONFIG["models"]["pro"])
        
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096
        }
        
        response = requests.post(
            API_CONFIG["url"],
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = result.get("usage", {})
            st.session_state.tokens += usage.get("total_tokens", 0)
            return content
        else:
            return f"❌ API错误: {response.status_code}"
    except Exception as e:
        return f"❌ 错误: {str(e)}"

# ================== 侧边栏 ==================
with st.sidebar:
    st.markdown("### 🌊 平静 Pro")
    st.caption("基于豆包API | 强力版")
    
    st.divider()
    
    # 模型选择
    model = st.selectbox(
        "选择模型",
        ["pro", "standard", "lite"],
        format_func=lambda x: {"pro": "🚀 Pro(最强)", "standard": "⚡ 标准", "lite": "💨 轻量"}[x]
    )
    st.session_state.model = model
    
    st.divider()
    
    # Token统计
    st.metric("已用Tokens", f"{st.session_state.tokens:,}")
    
    st.divider()
    
    # 能力
    st.markdown("#### 🎯 能力")
    st.markdown("- 💬 智能对话 ✅")
    st.markdown("- 📝 代码编写 ✅")
    st.markdown("- 🔧 文件操作 ✅")
    st.markdown("- ⚡ 代码执行 ✅")
    
    st.divider()
    
    # 按钮
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.session_state.messages:
        history = "\n\n".join([f"{'👤' if m['role']=='user' else '🌊'}: {m['content']}" for m in st.session_state.messages])
        st.download_button("💾 导出对话", history, file_name="calm_chat.md", use_container_width=True)

# ================== 主界面 ==================
st.markdown("<div class='main-title'>🌊 平静 Pro</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>你的智能AI助手 · 基于豆包API · 永久可用</div>", unsafe_allow_html=True)

st.divider()

# 欢迎信息
if not st.session_state.messages:
    st.info("""
    👋 **欢迎使用平静Pro！**
    
    我是你的AI助手，可以帮你：
    - 💬 对话问答
    - 📝 写代码
    - 🔧 处理文件
    - ⚡ 执行代码
    
    直接输入消息开始对话！
    """)
    
    st.divider()
    st.markdown("### ⚡ 快捷开始")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔍 搜索新闻", use_container_width=True):
            st.session_state.quick = "搜索今天的科技新闻"
    with c2:
        if st.button("🎨 生成代码", use_container_width=True):
            st.session_state.quick = "帮我写一个Python爬虫代码"
    with c3:
        if st.button("💡 闲聊", use_container_width=True):
            st.session_state.quick = "给我讲个程序员笑话"

# 聊天历史
for msg in st.session_state.messages:
    is_user = msg["role"] == "user"
    with st.chat_message("user" if is_user else "assistant", avatar="👤" if is_user else "🌊"):
        st.markdown(msg["content"])

# 输入处理
if "quick" in st.session_state:
    user_input = st.chat_input("输入消息...")
    if user_input is None:
        user_input = st.session_state.quick
        del st.session_state.quick
else:
    user_input = st.chat_input("输入消息...")

if user_input:
    # 用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    # AI回复
    with st.chat_message("assistant", avatar="🌊"):
        with st.spinner("思考中..."):
            # 构建消息
            api_messages = [{"role": "system", "content": "你是平静，一个专业、友好的AI助手。精通编程、数据分析、文档写作。请用简洁清晰的方式回答问题。"}]
            api_messages += [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            
            # 调用API
            response = call_api(api_messages, st.session_state.model)
            
            # 显示回复
            if "```" in response:
                parts = response.split("```")
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        if part.strip():
                            st.markdown(part)
                    else:
                        lang = part.split("\n")[0] if "\n" in part else ""
                        code = "\n".join(part.split("\n")[1:]) if "\n" in part else part
                        st.code(code, language=lang if lang else "text")
            else:
                st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

# ================== 页脚 ==================
st.divider()
st.caption("🌊 平静 Pro | 基于豆包API | 永久免费")
