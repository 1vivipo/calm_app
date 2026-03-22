"""
平静AI助手 - 单文件版
直接部署到HuggingFace Spaces即可使用
"""
import streamlit as st
import os
import json
from typing import Annotated

# 页面配置
st.set_page_config(
    page_title="平静 - AI助手",
    page_icon="🌊",
    layout="wide"
)

# 隐藏默认菜单
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.main-title {font-size: 2.2rem; font-weight: bold; color: #4A90E2; text-align: center;}
@media (max-width: 768px) {.main-title {font-size: 1.6rem;}}
</style>
""", unsafe_allow_html=True)

# 初始化session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# 缓存Agent实例
@st.cache_resource
def get_agent():
    """构建并返回Agent实例"""
    from langchain.agents import create_agent
    from langchain_openai import ChatOpenAI
    from langgraph.graph import MessagesState
    from langgraph.graph.message import add_messages
    from langchain_core.messages import AnyMessage
    from langgraph.checkpoint.memory import MemorySaver
    
    # 滑动窗口
    MAX_MESSAGES = 40
    
    def _windowed_messages(old, new):
        return add_messages(old, new)[-MAX_MESSAGES:]
    
    class AgentState(MessagesState):
        messages: Annotated[list[AnyMessage], _windowed_messages]
    
    # 获取平台API配置
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY", "")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL", "")
    
    # 如果没有环境变量，使用备用配置（用户可自行配置）
    if not api_key:
        # 尝试从配置文件读取
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                cfg = json.load(f)
                api_key = cfg.get("api_key", "")
                base_url = cfg.get("base_url", "")
    
    # 创建LLM
    llm = ChatOpenAI(
        model="doubao-seed-1-6-251015",
        api_key=api_key,
        base_url=base_url,
        temperature=0.7,
        streaming=True,
        timeout=120,
    )
    
    # 系统提示词
    system_prompt = """你是平静AI助手，一个友好、专业的智能对话伙伴。

你的能力：
- 回答问题和提供信息
- 帮助分析和解决问题
- 进行创意写作和内容生成
- 提供建议和指导

你的特点：
- 回答简洁清晰，直击要点
- 保持耐心和友善
- 承认不确定性，不编造信息
- 保护用户隐私，不询问敏感信息"""
    
    return create_agent(
        model=llm,
        system_prompt=system_prompt,
        tools=[],
        checkpointer=MemorySaver(),
        state_schema=AgentState,
    )

# 侧边栏
with st.sidebar:
    st.markdown("### 🌊 平静")
    st.caption("AI助手 | 永久免费")
    st.divider()
    
    st.markdown("#### ✨ 能力")
    st.markdown("- 💬 智能对话")
    st.markdown("- 📝 内容创作")
    st.markdown("- 🔤 翻译润色")
    st.markdown("- 💻 代码帮助")
    
    st.divider()
    
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.session_state.messages:
        history = "\n\n".join([
            f"{'👤' if m['role']=='user' else '🌊'}: {m['content']}" 
            for m in st.session_state.messages
        ])
        st.download_button(
            "💾 导出对话",
            history,
            file_name="calm_chat.md",
            use_container_width=True
        )

# 主界面
st.markdown("<h1 class='main-title'>🌊 平静</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray'>你的AI助手 | 永久免费 | 随时陪伴</p>", unsafe_allow_html=True)
st.divider()

# 欢迎信息
if not st.session_state.messages:
    st.info("""
    👋 **欢迎使用平静AI助手！**
    
    我是你的智能对话伙伴，可以帮你：
    - 💬 回答问题和提供建议
    - 📝 写作和内容创作
    - 🔤 翻译和润色文字
    - 💻 编程和代码问题
    
    直接输入消息开始对话吧！
    """)

# 显示聊天历史
for msg in st.session_state.messages:
    is_user = msg["role"] == "user"
    with st.chat_message("user" if is_user else "assistant", avatar="👤" if is_user else "🌊"):
        st.markdown(msg["content"])

# 用户输入
user_input = st.chat_input("输入消息...")

if user_input:
    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    # 获取AI回复
    with st.chat_message("assistant", avatar="🌊"):
        with st.spinner("思考中..."):
            try:
                from langchain_core.messages import HumanMessage, AIMessage
                
                agent = get_agent()
                
                # 构建消息历史
                messages = []
                for m in st.session_state.messages[:-1]:
                    if m["role"] == "user":
                        messages.append(HumanMessage(content=m["content"]))
                    else:
                        messages.append(AIMessage(content=m["content"]))
                
                messages.append(HumanMessage(content=user_input))
                
                # 调用Agent
                config = {"configurable": {"thread_id": "calm_user_session"}}
                result = agent.invoke({"messages": messages}, config)
                
                # 提取回复
                if result and "messages" in result:
                    last_msg = result["messages"][-1]
                    response = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
                else:
                    response = "抱歉，我暂时无法回应，请稍后再试。"
                
                # 处理响应内容
                if isinstance(response, list):
                    text_parts = []
                    for item in response:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                        elif isinstance(item, str):
                            text_parts.append(item)
                    response = " ".join(text_parts)
                
                st.markdown(response)
                
            except Exception as e:
                response = f"❌ 抱歉，出现错误：{str(e)}"
                st.error(response)
    
    # 保存AI回复
    st.session_state.messages.append({"role": "assistant", "content": response})

# 页脚
st.divider()
st.caption("🌊 平静 | AI助手 | 永久免费")
