"""
平静AI Agent - Streamlit前端应用
"""
import streamlit as st
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from datetime import datetime
from typing import List, Dict, Any
from backend import calm_agent
from config.config import Config
from config.prompts import SYSTEM_PROMPT


# 页面配置
def setup_page():
    """配置页面"""
    st.set_page_config(
        page_title=Config.UI_CONFIG["page_title"],
        page_icon=Config.UI_CONFIG["page_icon"],
        layout=Config.UI_CONFIG["layout"],
        initial_sidebar_state=Config.UI_CONFIG["sidebar_state"]
    )
    
    # 自定义CSS
    st.markdown("""
    <style>
    /* 主色调 */
    :root {
        --primary-color: #4A90E2;
        --bg-color: #FFFFFF;
        --secondary-bg: #F0F2F6;
        --text-color: #262730;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 聊天容器样式 */
    .stChatMessage {
        background-color: var(--secondary-bg);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* 用户消息样式 */
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #4A90E2;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
    }
    
    /* AI消息样式 */
    .assistant-message {
        background-color: #F5F5F5;
        border-left: 4px solid #10B981;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
    }
    
    /* 标题样式 */
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4A90E2;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* 副标题样式 */
    .sub-title {
        font-size: 1.2rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* 工具标签样式 */
    .tool-tag {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 4px 0;
    }
    
    /* 按钮样式 */
    .stButton>button {
        background-color: #4A90E2;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: #357ABD;
    }
    
    /* 输入框样式 */
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.8rem;
        }
        .sub-title {
            font-size: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    """初始化会话状态"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "enable_thinking" not in st.session_state:
        st.session_state.enable_thinking = False


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown(f"### 🌊 {Config.AGENT_NAME}")
        st.markdown("---")
        
        # 功能说明
        st.markdown("#### 🎯 核心能力")
        capabilities = [
            "💬 多轮对话",
            "🔍 网页搜索",
            "🎨 图像生成",
            "🎬 视频生成",
            "🔊 语音合成",
            "📄 文档生成",
            "🖼️ 图像理解",
            "🤔 深度思考"
        ]
        for cap in capabilities:
            st.markdown(f"- {cap}")
        
        st.markdown("---")
        
        # 设置选项
        st.markdown("#### ⚙️ 设置")
        
        # 思考模式开关
        st.session_state.enable_thinking = st.checkbox(
            "启用深度思考模式",
            value=st.session_state.enable_thinking,
            help="适用于复杂推理、数学计算等场景"
        )
        
        st.markdown("---")
        
        # 清空对话按钮
        if st.button("🗑️ 清空对话", use_container_width=True):
            if st.session_state.session_id:
                calm_agent.clear_session(st.session_state.session_id)
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()
        
        # 导出对话
        if st.session_state.messages:
            if st.button("💾 导出对话", use_container_width=True):
                export_chat_history()
        
        st.markdown("---")
        
        # 关于信息
        st.markdown("#### 📝 关于")
        st.info(f"""
        **{Config.AGENT_NAME}** v{Config.AGENT_VERSION}
        
        {Config.AGENT_DESCRIPTION}
        
        基于豆包大模型构建
        """)


def export_chat_history():
    """导出对话历史"""
    history_text = f"# {Config.AGENT_NAME} - 对话记录\n\n"
    history_text += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    history_text += "---\n\n"
    
    for msg in st.session_state.messages:
        role = "👤 用户" if msg["role"] == "user" else "🤖 平静"
        history_text += f"**{role}** ({msg['time']}):\n\n{msg['content']}\n\n---\n\n"
    
    st.download_button(
        label="下载对话记录",
        data=history_text,
        file_name=f"calm_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )


def render_message(message: Dict[str, Any], is_user: bool = True):
    """
    渲染单条消息
    
    Args:
        message: 消息内容
        is_user: 是否为用户消息
    """
    if is_user:
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
    else:
        with st.chat_message("assistant", avatar="🌊"):
            # 显示工具使用信息
            if message.get("tool_used"):
                tool_name = {
                    "web_search": "🔍 网页搜索",
                    "image_generation": "🎨 图像生成",
                    "video_generation": "🎬 视频生成",
                    "text_to_speech": "🔊 语音合成",
                    "document_generation": "📄 文档生成"
                }.get(message["tool_used"], "🔧 工具")
                
                st.markdown(f"<span class='tool-tag'>{tool_name}</span>", unsafe_allow_html=True)
            
            # 显示AI响应
            st.markdown(message['content'])
            
            # 显示工具结果
            if message.get("tool_result") and isinstance(message["tool_result"], dict):
                tool_result = message["tool_result"]
                
                # 图像
                if "image_urls" in tool_result and tool_result["image_urls"]:
                    st.image(tool_result["image_urls"][0], caption="生成的图像")
                
                # 视频
                if "video_url" in tool_result and tool_result["video_url"]:
                    st.video(tool_result["video_url"])
                
                # 音频
                if "audio_url" in tool_result and tool_result["audio_url"]:
                    st.audio(tool_result["audio_url"])
                
                # 文档
                if "download_url" in tool_result and tool_result["download_url"]:
                    st.markdown(f"📥 [下载文档]({tool_result['download_url']})")


async def process_user_input(user_input: str, files: List[str] = None):
    """
    处理用户输入
    
    Args:
        user_input: 用户输入文本
        files: 文件URL列表
    """
    # 添加用户消息
    user_message = {
        "role": "user",
        "content": user_input,
        "time": datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.messages.append(user_message)
    
    # 调用Agent
    with st.spinner("思考中..."):
        response = await calm_agent.chat(
            user_message=user_input,
            session_id=st.session_state.session_id,
            files=files,
            enable_thinking=st.session_state.enable_thinking
        )
        
        # 更新session_id
        if response.get("session_id"):
            st.session_state.session_id = response["session_id"]
        
        # 添加AI响应
        ai_message = {
            "role": "assistant",
            "content": response.get("response", "抱歉，我遇到了一些问题，请稍后再试。"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "tool_used": response.get("tool_used"),
            "tool_result": response.get("tool_result")
        }
        st.session_state.messages.append(ai_message)


def render_chat_interface():
    """渲染聊天界面"""
    # 标题
    st.markdown("<div class='main-title'>🌊 平静</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>你的智能AI助手 | 多模态 · 强能力 · 永久免费</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 聊天历史
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            render_message(message, is_user=(message["role"] == "user"))
    
    # 输入区域
    st.markdown("---")
    
    # 多模态输入提示
    col1, col2 = st.columns([3, 1])
    with col1:
        user_input = st.chat_input("输入消息... (可以输入图片/视频URL，我会自动识别)")
    with col2:
        st.markdown("""
        <div style='text-align: right; padding-top: 10px;'>
            <small>💡 提示：<br>
            • 说"搜索xxx"获取实时信息<br>
            • 说"生成图片xxx"创作图像<br>
            • 说"生成视频xxx"制作视频<br>
            • 发送图片URL进行理解</small>
        </div>
        """, unsafe_allow_html=True)
    
    if user_input:
        # 检测URL（图片、视频）
        files = []
        import re
        urls = re.findall(r'https?://[^\s]+', user_input)
        for url in urls:
            if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.avi', '.mov']):
                files.append(url)
        
        # 处理输入
        asyncio.run(process_user_input(user_input, files if files else None))
        st.rerun()


def render_quick_actions():
    """渲染快捷操作"""
    st.markdown("### ⚡ 快捷功能")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 搜索最新新闻"):
            asyncio.run(process_user_input("搜索最新的科技新闻"))
            st.rerun()
    
    with col2:
        if st.button("🎨 生成示例图"):
            asyncio.run(process_user_input("生成一张美丽的山水风景图"))
            st.rerun()
    
    with col3:
        if st.button("📄 生成报告"):
            asyncio.run(process_user_input("生成一份AI发展报告PDF文档"))
            st.rerun()
    
    with col4:
        if st.button("💡 创意点子"):
            asyncio.run(process_user_input("给我一些创业项目的创意点子"))
            st.rerun()


def main():
    """主函数"""
    setup_page()
    init_session_state()
    render_sidebar()
    
    # 主内容区
    render_chat_interface()
    
    # 如果是新会话，显示快捷操作
    if not st.session_state.messages:
        render_quick_actions()


if __name__ == "__main__":
    main()
