"""
平静AI助手 - 完整版Agent
支持动态模型选择：Mini(快速)/Pro(思考)/Agent(专家)
"""
import os
import json
from typing import Annotated, Optional, Dict, Any
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

# 模型配置
MODEL_CONFIGS = {
    "mini": {
        "model_id": "doubao-seed-1-6-lite-251015",
        "label": "Mini快速",
        "description": "快速响应，适合简单对话",
        "temperature": 0.7,
        "timeout": 30,
        "tools_enabled": False,  # Mini模型不启用工具
    },
    "pro": {
        "model_id": "doubao-seed-1-6-251015",
        "label": "Pro思考",
        "description": "平衡性能，适合复杂问题",
        "temperature": 0.7,
        "timeout": 60,
        "tools_enabled": False,  # Pro模型不启用工具
    },
    "agent": {
        "model_id": "doubao-seed-1-8-251228",
        "label": "Agent专家",
        "description": "工具调用，画图/搜索/代码",
        "temperature": 0.7,
        "timeout": 180,
        "tools_enabled": True,  # Agent模型启用工具
    },
    # 兼容直接传入模型ID
    "doubao-seed-1-6-lite-251015": {
        "model_id": "doubao-seed-1-6-lite-251015",
        "label": "Mini快速",
        "temperature": 0.7,
        "timeout": 30,
        "tools_enabled": False,
    },
    "doubao-seed-1-6-251015": {
        "model_id": "doubao-seed-1-6-251015",
        "label": "Pro思考",
        "temperature": 0.7,
        "timeout": 60,
        "tools_enabled": False,
    },
    "doubao-seed-1-8-251228": {
        "model_id": "doubao-seed-1-8-251228",
        "label": "Agent专家",
        "temperature": 0.7,
        "timeout": 180,
        "tools_enabled": True,
    },
}

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


def get_model_config(model_key: str) -> Dict[str, Any]:
    """根据模型key获取模型配置"""
    # 先尝试小写匹配
    key_lower = model_key.lower()
    if key_lower in MODEL_CONFIGS:
        return MODEL_CONFIGS[key_lower]
    
    # 尝试直接匹配
    if model_key in MODEL_CONFIGS:
        return MODEL_CONFIGS[model_key]
    
    # 默认返回agent配置
    return MODEL_CONFIGS["agent"]


def build_agent(ctx=None, model: Optional[str] = None):
    """
    构建Agent实例
    
    Args:
        ctx: 运行上下文
        model: 模型选择，支持 "mini"/"pro"/"agent" 或具体模型ID
               如果为None，从配置文件读取默认模型
    """
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)

    # 读取基础配置
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    # 确定要使用的模型
    if model:
        model_config = get_model_config(model)
        model_id = model_config["model_id"]
        temperature = model_config.get("temperature", 0.7)
        timeout = model_config.get("timeout", 180)
        tools_enabled = model_config.get("tools_enabled", True)
    else:
        # 从配置文件读取
        model_id = cfg['config'].get("model", "doubao-seed-1-8-251228")
        temperature = cfg['config'].get('temperature', 0.7)
        timeout = cfg['config'].get('timeout', 180)
        tools_enabled = True  # 默认启用工具

    # 使用平台内置的API配置
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")

    # 创建LLM实例
    llm = ChatOpenAI(
        model=model_id,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        streaming=True,
        timeout=timeout,
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )

    # 根据模型配置决定是否启用工具
    tools = ALL_TOOLS if tools_enabled else []

    # 系统提示词
    system_prompt = cfg.get("sp", "你是平静AI助手，请帮助用户解决问题。")
    
    # 根据模型能力调整提示词
    if not tools_enabled:
        # Mini/Pro模型：不使用工具，但可以告诉用户如何请求
        system_prompt += "\n\n注意：当前使用轻量模型，如需画图、搜索、运行代码等功能，请切换到Agent专家模式。"

    # 创建并返回Agent
    return create_agent(
        model=llm,
        system_prompt=system_prompt,
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )


# 缓存不同模型的Agent实例
_agent_cache: Dict[str, Any] = {}


def get_cached_agent(model: Optional[str] = None, ctx=None):
    """
    获取缓存的Agent实例（避免重复创建）
    
    注意：不同模型使用不同的缓存key
    """
    cache_key = model or "default"
    
    if cache_key not in _agent_cache:
        _agent_cache[cache_key] = build_agent(ctx=ctx, model=model)
    
    return _agent_cache[cache_key]
