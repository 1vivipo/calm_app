"""
平静AI Agent - Hugging Face Spaces 主入口
"""
import os
import sys
import streamlit as st

# 页面配置 - 移动端优化
st.set_page_config(
    page_title="平静 - AI助手",
    page_icon="🌊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 移动端适配CSS
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

<style>
/* 隐藏默认元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* 移动端优化 */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem !important;
        max-width: 100% !important;
    }
    
    .main-title {
        font-size: 1.8rem !important;
    }
    
    .stButton > button {
        width: 100%;
        padding: 12px !important;
        font-size: 16px !important;
    }
    
    .stTextInput input {
        font-size: 16px !important;
        padding: 12px !important;
    }
}

/* 标题样式 */
.main-title {
    font-size: 2.5rem;
    font-weight: bold;
    color: #4A90E2;
    text-align: center;
    margin: 1rem 0;
}

.sub-title {
    font-size: 1rem;
    color: #6B7280;
    text-align: center;
    margin-bottom: 1.5rem;
}

/* 用户消息 */
.user-msg {
    background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
    border-left: 4px solid #4A90E2;
    padding: 12px;
    border-radius: 8px;
    margin: 8px 0;
}

/* AI消息 */
.ai-msg {
    background: linear-gradient(135deg, #F5F5F5 0%, #EEEEEE 100%);
    border-left: 4px solid #10B981;
    padding: 12px;
    border-radius: 8px;
    margin: 8px 0;
}

/* 工具标签 */
.tool-tag {
    background: #FEF3C7;
    color: #92400E;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.85rem;
    display: inline-block;
    margin: 4px 0;
}

/* 按钮样式 */
.stButton > button {
    background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 500;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #357ABD 0%, #2A5F8F 100%);
}

/* 快捷功能卡片 */
.quick-card {
    background: #F0F2F6;
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
    border: 1px solid #E5E7EB;
}
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

# 主界面
st.markdown("<div class='main-title'>🌊 平静</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>你的智能AI助手 · 永久免费</div>", unsafe_allow_html=True)
st.divider()

# 侧边栏
with st.sidebar:
    st.markdown("### 🌊 平静")
    st.caption("v2.0.0 | 永久免费")
    st.divider()
    
    st.markdown("#### 🎯 能力")
    st.markdown("💬 智能对话 ✅")
    st.markdown("🔍 网页搜索 ✅")
    st.markdown("🎨 图像生成 ✅")
    st.markdown("🎬 视频生成 ✅")
    st.markdown("📄 文档生成 ✅")
    st.markdown("🖼️ 图像理解 ✅")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ 清空", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.session_state.messages:
            history = "\n\n".join([
                f"{'👤用户' if m['role']=='user' else '🌊平静'}: {m['content']}"
                for m in st.session_state.messages
            ])
            st.download_button(
                "💾 导出",
                history,
                file_name="calm_chat.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    st.divider()
    with st.expander("❓ 使用帮助"):
        st.markdown("""
        **快捷指令：**
        - `搜索 xxx` - 网页搜索
        - `生成图片 xxx` - 创作图像
        - `生成视频 xxx` - 制作视频
        - `生成文档 xxx` - 创建文档
        """)

# 聊天历史
for msg in st.session_state.messages:
    is_user = msg["role"] == "user"
    with st.chat_message("user" if is_user else "assistant", 
                         avatar="👤" if is_user else "🌊"):
        if msg.get("tool"):
            st.markdown(f"<span class='tool-tag'>{msg['tool']}</span>", unsafe_allow_html=True)
        st.markdown(msg["content"])

# 快捷功能
if not st.session_state.messages:
    st.markdown("<div class='quick-card'>", unsafe_allow_html=True)
    st.markdown("**👋 欢迎使用平静！**")
    st.markdown("我是你的AI助手，直接输入消息开始对话吧！")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### ⚡ 快捷功能")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 搜索新闻", use_container_width=True):
            st.session_state.quick_input = "搜索今天的科技新闻"
        if st.button("📄 生成文档", use_container_width=True):
            st.session_state.quick_input = "生成一份AI简介PDF"
    with col2:
        if st.button("🎨 生成图片", use_container_width=True):
            st.session_state.quick_input = "生成一张美丽的风景图"
        if st.button("💡 闲聊", use_container_width=True):
            st.session_state.quick_input = "给我讲个笑话"

# 处理快捷输入
if "quick_input" in st.session_state:
    user_input = st.chat_input("输入消息...")
    if user_input is None:
        st.session_state.pending = st.session_state.quick_input
        del st.session_state.quick_input
        st.rerun()

# 用户输入
user_input = st.chat_input("输入消息...")

if "pending" in st.session_state:
    user_input = st.session_state.pending
    del st.session_state.pending

if user_input:
    # 添加用户消息
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # 显示用户消息
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    # 生成回复
    with st.chat_message("assistant", avatar="🌊"):
        with st.spinner("思考中..."):
            # 简单的规则匹配
            response = generate_response(user_input)
            st.markdown(response)
    
    # 添加AI消息
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

def generate_response(message: str) -> str:
    """生成AI回复"""
    msg_lower = message.lower()
    
    # 问候
    if any(g in msg_lower for g in ["你好", "嗨", "hi", "hello"]):
        return "你好！我是平静，你的AI助手。有什么可以帮你的吗？"
    
    # 介绍
    if "介绍" in msg_lower or "你是谁" in msg_lower:
        return """我是**平静**，一个永久免费的AI助手！

我的能力包括：
- 💬 智能对话 - 有问必答
- 🔍 网页搜索 - 实时信息
- 🎨 图像生成 - 文本转图
- 🎬 视频生成 - 动态创作
- 📄 文档生成 - PDF/Word

直接告诉我你想做什么吧！"""
    
    # 搜索
    if any(k in msg_lower for k in ["搜索", "查询", "查找"]):
        return f"收到搜索请求：**{message}**\n\n正在为你搜索最新信息...（此功能需要配置API密钥）"
    
    # 图像生成
    if any(k in msg_lower for k in ["生成图片", "画一张", "生成图像"]):
        return f"收到图像创作请求：**{message}**\n\n正在为你生成图像...（此功能需要配置API密钥）"
    
    # 视频生成
    if "生成视频" in msg_lower:
        return f"收到视频创作请求：**{message}**\n\n正在为你生成视频...（此功能需要配置API密钥）"
    
    # 文档生成
    if any(k in msg_lower for k in ["生成文档", "生成pdf", "生成word"]):
        return f"收到文档生成请求：**{message}**\n\n正在为你生成文档...（此功能需要配置API密钥）"
    
    # 笑话
    if "笑话" in msg_lower or "讲个" in msg_lower:
        return """为什么程序员总是分不清万圣节和圣诞节？

因为 Oct 31 = Dec 25 😄

（八进制的31等于十进制的25）"""
    
    # 感谢
    if any(k in msg_lower for k in ["谢谢", "感谢"]):
        return "不客气！很高兴能帮到你。还有其他问题吗？"
    
    # 默认回复
    return f"收到你的消息：**{message}**\n\n我正在基础模式运行。如需完整功能，请在设置中配置API密钥（讯飞/豆包等）。\n\n不过我仍然可以陪你聊天！有什么想问的吗？"
