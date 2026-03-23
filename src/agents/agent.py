"""
平静AI助手 - 全能执行型Agent
具备命令执行、代码运行、文件管理、联网搜索、多模态识图等强大能力
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
    search_in_files,
    install_package,
    get_task_result
)
from tools.task_tool import (
    create_task,
    get_task_status,
    list_tasks,
    update_task
)
from tools.storage_tool import (
    upload_file,
    upload_binary_file,
    download_file,
    get_download_url
)
from tools.vision_tool import (
    analyze_image,
    extract_text_from_image,
    analyze_chart,
    compare_images,
    detect_objects,
    analyze_video,
    describe_image_for_blind
)

LLM_CONFIG = "config/agent_llm_config.json"

# 滑动窗口：保留最近30轮对话
MAX_MESSAGES = 60

def _windowed_messages(old, new):
    """滑动窗口: 只保留最近MAX_MESSAGES条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:]


class AgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]


# 收集所有工具
ALL_TOOLS = [
    # 执行工具
    execute_shell,
    execute_python,
    read_file_content,
    write_file_content,
    list_files,
    search_in_files,
    install_package,
    get_task_result,
    # 任务管理工具
    create_task,
    get_task_status,
    list_tasks,
    update_task,
    # 存储工具
    upload_file,
    upload_binary_file,
    download_file,
    get_download_url,
    # 多模态工具
    analyze_image,
    extract_text_from_image,
    analyze_chart,
    compare_images,
    detect_objects,
    analyze_video,
    describe_image_for_blind,
    # 搜索工具
    web_search,
]


def build_agent(ctx=None):
    """构建全能执行型Agent"""
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)

    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    # 使用平台内置的API配置
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")

    # 创建LLM实例
    llm = ChatOpenAI(
        model=cfg['config'].get("model", "doubao-seed-1-6-251015"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 300),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )

    # 创建并返回全能Agent
    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp", "你是平静AI助手，一个强大的执行型AI。"),
        tools=ALL_TOOLS,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
