"""
平静AI Agent Pro - 完整版
支持豆包API，具备工具调用能力
"""
import streamlit as st
import requests
import json
import os
import base64
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import subprocess
import tempfile

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
    "app_id": "cb655659b3814c9d9b48c856d1112",
    "models": {
        "pro": "d4432662ebed421890bf8fe60e40043!",  # doubao-seed-2.0-pro
        "standard": "87f80d930d3e4c478e50f7a121dfbb97",  # 豆包seed1.8
        "lite": "651c9b454b58458f9b604e67c03ab73"  # 豆包seed1.6
    }
}

# ================== CSS样式 ==================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');

:root {
    --primary: #4A90E2;
    --success: #10B981;
    --warning: #F59E0B;
    --danger: #EF4444;
    --bg: #FFFFFF;
    --secondary-bg: #F0F2F6;
}

* { font-family: 'Noto Sans SC', sans-serif; }

#MainMenu, footer, header { visibility: hidden; }

.main-title {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #4A90E2, #10B981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin: 1rem 0;
}

.sub-title {
    color: #6B7280;
    text-align: center;
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
}

.chat-message {
    padding: 1rem;
    border-radius: 12px;
    margin: 0.5rem 0;
    line-height: 1.6;
}

.user-message {
    background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
    border-left: 4px solid var(--primary);
}

.assistant-message {
    background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
    border-left: 4px solid var(--success);
}

.tool-badge {
    display: inline-block;
    background: #FEF3C7;
    color: #92400E;
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 0.85rem;
    margin: 0.25rem 0;
}

.code-block {
    background: #1E1E1E;
    color: #D4D4D4;
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
    font-family: 'Consolas', monospace;
}

@media (max-width: 768px) {
    .main-title { font-size: 1.8rem; }
    .stButton > button { width: 100%; }
}
</style>
""", unsafe_allow_html=True)

# ================== 会话状态 ==================
def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "token_count" not in st.session_state:
        st.session_state.token_count = 0
    if "current_model" not in st.session_state:
        st.session_state.current_model = "pro"

init_state()

# ================== API调用 ==================
def call_doubao_api(messages: List[Dict], model: str = "pro", temperature: float = 0.7) -> str:
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
            "temperature": temperature,
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
            
            # 更新token计数
            usage = result.get("usage", {})
            st.session_state.token_count += usage.get("total_tokens", 0)
            
            return content
        else:
            return f"API调用失败: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"错误: {str(e)}"

# ================== 工具函数 ==================
def create_file(filename: str, content: str) -> str:
    """创建文件"""
    try:
        # 使用临时目录
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"✅ 文件已创建: {filename}\n路径: {filepath}\n大小: {len(content)} 字符"
    except Exception as e:
        return f"❌ 创建文件失败: {str(e)}"

def read_file(filename: str) -> str:
    """读取文件"""
    try:
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        
        if not os.path.exists(filepath):
            return f"❌ 文件不存在: {filename}"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"📄 文件内容:\n```\n{content}\n```"
    except Exception as e:
        return f"❌ 读取文件失败: {str(e)}"

def run_code(code: str, language: str = "python") -> str:
    """执行代码"""
    try:
        if language.lower() == "python":
            result = subprocess.run(
                ["python", "-c", code],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return f"✅ 执行成功:\n```\n{result.stdout}\n```"
            else:
                return f"❌ 执行失败:\n```\n{result.stderr}\n```"
        else:
            return f"⚠️ 暂不支持 {language} 语言"
    except subprocess.TimeoutExpired:
        return "❌ 执行超时（10秒限制）"
    except Exception as e:
        return f"❌ 执行错误: {str(e)}"

def analyze_request(user_input: str) -> Dict[str, Any]:
    """分析用户请求，判断是否需要使用工具"""
    result = {
        "need_tool": False,
        "tool_name": None,
        "tool_params": {},
        "response": None
    }
    
    # 检测文件创建
    create_match = re.search(r'(?:创建|新建|生成).*?文件[：:]\s*(\S+).*?内容[：:](.+)', user_input, re.DOTALL)
    if create_match:
        result["need_tool"] = True
        result["tool_name"] = "create_file"
        result["tool_params"] = {
            "filename": create_match.group(1),
            "content": create_match.group(2).strip()
        }
        return result
    
    # 检测代码执行
    if "```python" in user_input and "执行" in user_input:
        code_match = re.search(r'```python\n(.*?)\n```', user_input, re.DOTALL)
        if code_match:
            result["need_tool"] = True
            result["tool_name"] = "run_code"
            result["tool_params"] = {
                "code": code_match.group(1),
                "language": "python"
            }
        return result
    
    return result

# ================== 主界面 ==================
def render_sidebar():
    with st.sidebar:
        st.markdown("### 🌊 平静 Pro")
        st.caption("基于豆包API | 强力版")
        
        st.divider()
        
        # 模型选择
        st.markdown("#### 🤖 模型选择")
        model = st.radio(
            "选择模型",
            ["pro", "standard", "lite"],
            format_func=lambda x: {
                "pro": "🚀 Pro (最强)",
                "standard": "⚡ 标准版",
                "lite": "💨 轻量版"
            }[x],
            key="model_select"
        )
        st.session_state.current_model = model
        
        st.divider()
        
        # Token统计
        st.markdown("#### 📊 Token统计")
        st.metric("已使用", f"{st.session_state.token_count:,}", "tokens")
        
        st.divider()
        
        # 功能列表
        st.markdown("#### 🎯 能力")
        capabilities = [
            ("💬", "智能对话", True),
            ("📝", "代码编写", True),
            ("🔧", "文件操作", True),
            ("⚡", "代码执行", True),
            ("🔍", "数据分析", True),
        ]
        
        for icon, name, available in capabilities:
            st.markdown(f"{icon} {name} {'✅' if available else '❌'}")
        
        st.divider()
        
        # 操作按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ 清空对话", use_container_width=True):
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
                    file_name=f"calm_pro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

def render_main():
    # 标题
    st.markdown("<div class='main-title'>🌊 平静 Pro</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>你的智能AI助手 · 基于豆包API · 永久可用</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # 聊天历史
    for msg in st.session_state.messages:
        is_user = msg["role"] == "user"
        
        with st.chat_message("user" if is_user else "assistant", avatar="👤" if is_user else "🌊"):
            if msg.get("tool"):
                st.markdown(f"<span class='tool-badge'>{msg['tool']}</span>", unsafe_allow_html=True)
            
            # 处理代码高亮
            content = msg["content"]
            if "```" in content:
                parts = content.split("```")
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        st.markdown(part)
                    else:
                        language = part.split("\n")[0] if "\n" in part else ""
                        code = "\n".join(part.split("\n")[1:]) if "\n" in part else part
                        st.code(code, language=language if language else "text")
            else:
                st.markdown(content)
    
    # 用户输入
    user_input = st.chat_input("输入消息...")
    
    if user_input:
        # 添加用户消息
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        
        # 分析请求
        analysis = analyze_request(user_input)
        
        # 处理工具调用
        if analysis["need_tool"]:
            tool_name = analysis["tool_name"]
            tool_params = analysis["tool_params"]
            
            if tool_name == "create_file":
                tool_result = create_file(**tool_params)
            elif tool_name == "run_code":
                tool_result = run_code(**tool_params)
            else:
                tool_result = "未知工具"
            
            # 添加AI响应
            with st.chat_message("assistant", avatar="🌊"):
                st.markdown(f"<span class='tool-badge'>🔧 {tool_name}</span>", unsafe_allow_html=True)
                st.markdown(tool_result)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": tool_result,
                "tool": tool_name
            })
        else:
            # 普通对话
            with st.chat_message("assistant", avatar="🌊"):
                with st.spinner("思考中..."):
                    # 构建消息历史
                    api_messages = [
                        {"role": "system", "content": "你是平静，一个专业、友好、能力强大的AI助手。你精通编程、数据分析、文档写作等各类任务。请用简洁清晰的方式回答问题，涉及代码时使用markdown代码块格式。"}
                    ]
                    
                    for msg in st.session_state.messages[:-1]:
                        api_messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                    
                    api_messages.append({
                        "role": "user",
                        "content": user_input
                    })
                    
                    # 调用API
                    response = call_doubao_api(
                        api_messages,
                        model=st.session_state.current_model
                    )
                    
                    # 处理代码高亮显示
                    if "```" in response:
                        parts = response.split("```")
                        for i, part in enumerate(parts):
                            if i % 2 == 0:
                                st.markdown(part)
                            else:
                                language = part.split("\n")[0] if "\n" in part else ""
                                code = "\n".join(part.split("\n")[1:]) if "\n" in part else part
                                st.code(code, language=language if language else "text")
                    else:
                        st.markdown(response)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

# ================== 主函数 ==================
def main():
    render_sidebar()
    render_main()

if __name__ == "__main__":
    main()
