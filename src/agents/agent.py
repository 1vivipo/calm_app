"""
平静AI助手 - 完整版Agent
基于 doubao-seed-1-8-251228 模型，具备完整工具调用能力
"""
import os
import json
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from coze_coding_utils.runtime_ctx.context import default_headers
from storage.memory.memory_saver import get_memory_saver

# 导入所有工具
from tools.search_tool import web_search
from tools.executor_tool import (
    execute_shell,
    execute_python,
    read_file_content,
    write_file_content,
    list_files,
)
from tools.vision_tool import (
    analyze_image,
    extract_text_from_image,
    compare_images,
)
from tools.image_gen_tool import (
    generate_image,
    generate_multiple_images,
)

LLM_CONFIG = "config/agent_llm_config.json"

# 滑动窗口：保留最近30轮对话
MAX_MESSAGES = 60

def _windowed_messages(old, new):
    """滑动窗口: 只保留最近MAX_MESSAGES条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:]


class AgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]


# 所有可用工具
ALL_TOOLS = [
    # 图片生成
    generate_image,
    generate_multiple_images,
    # 代码执行
    execute_python,
    execute_shell,
    # 搜索
    web_search,
    # 图片分析
    analyze_image,
    extract_text_from_image,
    compare_images,
    # 文件操作
    read_file_content,
    write_file_content,
    list_files,
]


def build_agent(ctx=None):
    """构建完整版Agent - 使用 doubao-seed-1-8-251228"""
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)

    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    # 使用平台内置的API配置
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")

    # 创建LLM实例 - 使用 doubao-seed-1-8-251228
    llm = ChatOpenAI(
        model=cfg['config'].get("model", "doubao-seed-1-8-251228"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 180),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )

    # 创建并返回Agent
    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp", "你是平静AI助手，请帮助用户解决问题。"),
        tools=ALL_TOOLS,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
