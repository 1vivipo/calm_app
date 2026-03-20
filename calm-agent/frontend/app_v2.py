"""
平静AI Agent - 移动端优化的Streamlit前端
完美适配手机、平板、PC
"""
import streamlit as st
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from datetime import datetime
from typing import List, Dict, Any
import re


# ================== 移动端检测 ==================
def is_mobile():
    """检测是否为移动设备"""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        if ctx and ctx.request:
            user_agent = ctx.request.headers.get("User-Agent", "")
            mobile_keywords = ['Mobile', 'Android', 'iPhone', 'iPad', 'Windows Phone']
            return any(keyword in user_agent for keyword in mobile_keywords)
    except:
        pass
    return False


# ================== 页面配置 ==================
def setup_page():
    """配置页面 - 移动端优先"""
    st.set_page_config(
        page_title="平静 - AI助手",
        page_icon="🌊",
        layout="centered",  # 移动端使用centered布局
        initial_sidebar_state="collapsed" if is_mobile() else "expanded"
    )
    
    # 移动端优化的CSS
    st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    
    <style>
    /* ========== 全局样式 ========== */
    :root {
        --primary-color: #4A90E2;
        --bg-color: #FFFFFF;
        --secondary-bg: #F0F2F6;
        --text-color: #262730;
        --success-color: #10B981;
        --warning-color: #F59E0B;
    }
    
    /* ========== 隐藏Streamlit默认元素 ========== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ========== 移动端优化 ========== */
    @media (max-width: 768px) {
        /* 主容器 */
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
            max-width: 100% !important;
        }
        
        /* 标题 */
        .main-title {
            font-size: 1.8rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        .sub-title {
            font-size: 0.9rem !important;
            margin-bottom: 1rem !important;
        }
        
        /* 侧边栏 */
        section[data-testid="stSidebar"] {
            width: 280px !important;
        }
        
        section[data-testid="stSidebar"] > div {
            padding: 1rem !important;
        }
        
        /* 按钮 */
        .stButton > button {
            width: 100%;
            padding: 12px !important;
            font-size: 16px !important;
        }
        
        /* 输入框 */
        .stTextInput input {
            font-size: 16px !important;
            padding: 12px !important;
        }
        
        /* 聊天消息 */
        .stChatMessage {
            padding: 10px !important;
        }
        
        .stChatMessage [data-testid="stMarkdownContainer"] {
            font-size: 15px !important;
            line-height: 1.6 !important;
        }
        
        /* 快捷按钮 */
        .quick-btn {
            width: 100% !important;
            margin: 5px 0 !important;
        }
        
        /* 图片 */
        .stImage img {
            max-width: 100% !important;
            height: auto !important;
        }
        
        /* 视频 */
        video {
            max-width: 100% !important;
        }
        
        /* 工具标签 */
        .tool-tag {
            font-size: 0.75rem !important;
            padding: 3px 8px !important;
        }
    }
    
    /* ========== 桌面端样式 ========== */
    @media (min-width: 769px) {
        .main .block-container {
            max-width: 800px !important;
            margin: 0 auto !important;
        }
    }
    
    /* ========== 通用样式 ========== */
    
    /* 主标题 */
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4A90E2;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
    }
    
    /* 副标题 */
    .sub-title {
        font-size: 1rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* 用户消息 */
    .user-message {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-left: 4px solid #4A90E2;
        padding: 12px 15px;
        border-radius: 8px;
        margin: 8px 0;
        font-size: 15px;
        line-height: 1.6;
    }
    
    /* AI消息 */
    .assistant-message {
        background: linear-gradient(135deg, #F5F5F5 0%, #EEEEEE 100%);
        border-left: 4px solid #10B981;
        padding: 12px 15px;
        border-radius: 8px;
        margin: 8px 0;
        font-size: 15px;
        line-height: 1.6;
    }
    
    /* 工具标签 */
    .tool-tag {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        color: #92400E;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 4px 0;
        font-weight: 500;
    }
    
    /* 状态指示器 */
    .status-online {
        color: #10B981;
        font-weight: bold;
    }
    
    .status-offline {
        color: #EF4444;
        font-weight: bold;
    }
    
    /* 输入区域 */
    .stChatInput {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 10px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        z-index: 100;
    }
    
    /* 聊天容器 - 留出输入框空间 */
    .chat-container {
        padding-bottom: 80px;
    }
    
    /* 功能卡片 */
    .feature-card {
        background: var(--secondary-bg);
        border-radius: 12px;
        padding: 15px;
        margin: 8px 0;
        border: 1px solid #E5E7EB;
    }
    
    .feature-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: var(--primary-color);
        margin-bottom: 8px;
    }
    
    /* 按钮样式优化 */
    .stButton > button {
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #357ABD 0%, #2A5F8F 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* 加载动画 */
    .loading-dots {
        display: inline-block;
    }
    
    .loading-dots::after {
        content: '...';
        animation: dots 1.5s steps(4, end) infinite;
    }
    
    @keyframes dots {
        0%, 20% { content: '.'; }
        40% { content: '..'; }
        60%, 100% { content: '...'; }
    }
    
    /* 滚动条美化 */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
    """, unsafe_allow_html=True)


# ================== 会话状态 ==================
def init_session_state():
    """初始化会话状态"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "model_status" not in st.session_state:
        st.session_state.model_status = "检测中..."


# ================== 侧边栏 ==================
def render_sidebar():
    """渲染侧边栏 - 移动端友好"""
    with st.sidebar:
        # 标题
        st.markdown(f"### 🌊 平静")
        st.caption(f"v1.0.0 | 永久免费")
        
        st.divider()
        
        # 模型状态
        status_color = "🟢" if "在线" in st.session_state.model_status else "🔴"
        st.markdown(f"**{status_color} {st.session_state.model_status}**")
        
        st.divider()
        
        # 功能列表 - 移动端简化
        st.markdown("#### 🎯 能力")
        
        features = [
            ("💬", "智能对话", True),
            ("🔍", "网页搜索", True),
            ("🎨", "图像生成", True),
            ("🎬", "视频生成", True),
            ("📄", "文档生成", True),
            ("🖼️", "图像理解", True),
        ]
        
        for icon, name, available in features:
            status = "✅" if available else "❌"
            st.markdown(f"{icon} {name} {status}")
        
        st.divider()
        
        # 操作按钮
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ 清空", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        with col2:
            if st.button("💾 导出", use_container_width=True):
                export_chat()
        
        st.divider()
        
        # 帮助信息
        with st.expander("❓ 使用帮助"):
            st.markdown("""
            **快捷指令：**
            - `搜索 xxx` - 网页搜索
            - `生成图片 xxx` - 创作图像
            - `生成视频 xxx` - 制作视频
            - `生成文档 xxx` - 创建文档
            
            **提示：**
            - 发送图片URL可识别图片
            - 对话会自动保存历史
            """)
        
        # 关于
        st.caption("基于豆包/讯飞大模型")


# ================== 导出功能 ==================
def export_chat():
    """导出对话"""
    if not st.session_state.messages:
        st.warning("暂无对话记录")
        return
    
    history = f"# 平静 - 对话记录\n\n"
    history += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n"
    
    for msg in st.session_state.messages:
        role = "👤 用户" if msg["role"] == "user" else "🌊 平静"
        history += f"**{role}** ({msg['time']})\n\n{msg['content']}\n\n---\n\n"
    
    st.download_button(
        label="📥 下载记录",
        data=history,
        file_name=f"calm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown",
        use_container_width=True
    )


# ================== 消息渲染 ==================
def render_message(message: Dict[str, Any]):
    """渲染消息 - 移动端优化"""
    is_user = message["role"] == "user"
    
    with st.chat_message("user" if is_user else "assistant", 
                         avatar="👤" if is_user else "🌊"):
        # 工具标签
        if not is_user and message.get("tool_used"):
            tool_name = {
                "web_search": "🔍 网页搜索",
                "image_generation": "🎨 图像生成",
                "video_generation": "🎬 视频生成",
                "text_to_speech": "🔊 语音合成",
                "document_generation": "📄 文档生成"
            }.get(message["tool_used"], "🔧 工具")
            st.markdown(f"<span class='tool-tag'>{tool_name}</span>", unsafe_allow_html=True)
        
        # 消息内容
        st.markdown(message["content"])
        
        # 工具结果展示
        if message.get("tool_result") and isinstance(message["tool_result"], dict):
            result = message["tool_result"]
            
            # 图像
            if "image_urls" in result and result["image_urls"]:
                st.image(result["image_urls"][0], use_container_width=True)
            
            # 视频
            if "video_url" in result and result["video_url"]:
                st.video(result["video_url"])
            
            # 音频
            if "audio_url" in result and result["audio_url"]:
                st.audio(result["audio_url"])
            
            # 文档
            if "download_url" in result and result["download_url"]:
                st.markdown(f"📥 [下载文档]({result['download_url']})")


# ================== 快捷功能 ==================
def render_quick_actions():
    """渲染快捷功能按钮 - 移动端优化"""
    st.markdown("### ⚡ 快捷功能")
    
    # 移动端使用2列，桌面端使用4列
    cols = 2 if is_mobile() else 4
    
    col1, col2 = st.columns(cols)
    
    actions = [
        ("🔍 搜索新闻", "搜索今天的科技新闻"),
        ("🎨 生成图片", "生成一张美丽的风景图"),
        ("📄 生成文档", "生成一份AI简介PDF"),
        ("💡 闲聊", "给我讲个笑话"),
    ]
    
    for i, (btn_text, prompt) in enumerate(actions):
        col = [col1, col2, col1, col2][i]
        with col:
            if st.button(btn_text, key=f"quick_{i}", use_container_width=True):
                return prompt
    
    return None


# ================== 主界面 ==================
def render_main():
    """渲染主界面"""
    # 标题
    st.markdown("<div class='main-title'>🌊 平静</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>你的智能AI助手 · 永久免费</div>", unsafe_allow_html=True)
    
    # 分隔线
    st.divider()
    
    # 聊天历史
    chat_container = st.container()
    with chat_container:
        if st.session_state.messages:
            for msg in st.session_state.messages:
                render_message(msg)
        else:
            # 欢迎界面
            st.markdown("""
            <div class='feature-card'>
                <div class='feature-title'>👋 欢迎使用平静</div>
                <p>我是你的AI助手，具备以下能力：</p>
                <ul>
                    <li>💬 智能对话 - 有问必答</li>
                    <li>🔍 网页搜索 - 实时信息</li>
                    <li>🎨 图像生成 - 文本转图</li>
                    <li>🎬 视频生成 - 创作动态内容</li>
                    <li>📄 文档生成 - PDF/Word</li>
                </ul>
                <p><strong>直接输入消息开始对话吧！</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            # 快捷功能
            st.divider()
            quick_prompt = render_quick_actions()
            if quick_prompt:
                st.session_state.pending_input = quick_prompt
    
    # 输入区域
    st.divider()
    
    # 处理快捷输入
    if "pending_input" in st.session_state:
        user_input = st.chat_input("输入消息...", key="chat_input")
        if user_input is None:
            # 自动填入快捷输入
            process_input(st.session_state.pending_input)
            del st.session_state.pending_input
            st.rerun()
    else:
        user_input = st.chat_input("输入消息...")
        if user_input:
            process_input(user_input)


# ================== 处理输入 ==================
def process_input(user_input: str):
    """处理用户输入"""
    # 添加用户消息
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "time": datetime.now().strftime("%H:%M")
    })
    
    # 显示加载状态
    with st.spinner("思考中..."):
        try:
            # 调用后端
            from backend.core_v2 import model_adapter
            
            # 准备历史
            history = []
            for msg in st.session_state.messages[:-1]:
                history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # 异步调用
            response = asyncio.run(model_adapter.chat(
                message=user_input,
                history=history
            ))
            
            # 添加AI回复
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "time": datetime.now().strftime("%H:%M"),
                "tool_used": None,
                "tool_result": None
            })
            
        except Exception as e:
            # 错误处理
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"抱歉，处理时出现错误: {str(e)}",
                "time": datetime.now().strftime("%H:%M")
            })


# ================== 主函数 ==================
def main():
    """主函数"""
    setup_page()
    init_session_state()
    
    # 检测模型状态
    if st.session_state.model_status == "检测中...":
        try:
            from backend.core_v2 import model_adapter
            if model_adapter.primary_model:
                st.session_state.model_status = f"在线 ({model_adapter.primary_model})"
            else:
                st.session_state.model_status = "离线模式"
        except:
            st.session_state.model_status = "离线模式"
    
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()
