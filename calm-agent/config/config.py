"""
平静AI Agent - 配置文件
"""
import os
from typing import Dict, Any

class Config:
    """系统配置"""
    
    # Agent基本信息
    AGENT_NAME = "平静"
    AGENT_VERSION = "1.0.0"
    AGENT_DESCRIPTION = "具备多模态能力的高级AI助手"
    
    # 模型配置
    DEFAULT_MODEL = "doubao-seed-1-8-251228"  # 默认使用豆包模型
    VISION_MODEL = "doubao-seed-1-6-vision-250815"  # 视觉模型
    THINKING_MODEL = "doubao-seed-2-0-pro-260215"  # 深度思考模型
    
    # 模型参数
    MODEL_CONFIG = {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_completion_tokens": 8192,
        "thinking": "disabled",  # 默认关闭思考模式
    }
    
    # 会话配置
    MAX_HISTORY = 50  # 最多保留50轮对话
    SESSION_TIMEOUT = 3600  # 会话超时时间（秒）
    
    # 工具配置
    TOOLS_CONFIG = {
        "web_search": {
            "enabled": True,
            "default_count": 10,
        },
        "image_generation": {
            "enabled": True,
            "default_size": "2K",
        },
        "video_generation": {
            "enabled": True,
            "default_duration": 5,
        },
        "audio_tts": {
            "enabled": True,
        },
        "document_generation": {
            "enabled": True,
        },
    }
    
    # UI配置
    UI_CONFIG = {
        "page_title": "平静 - AI助手",
        "page_icon": "🌊",
        "layout": "wide",
        "sidebar_state": "expanded",
        "theme": {
            "primaryColor": "#4A90E2",
            "backgroundColor": "#FFFFFF",
            "secondaryBackgroundColor": "#F0F2F6",
            "textColor": "#262730",
            "font": "sans serif"
        }
    }
    
    # 服务配置
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 8501
    API_PORT = 8000
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FILE = "/app/work/logs/bypass/calm_agent.log"
    
    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """获取模型配置"""
        return cls.MODEL_CONFIG.copy()
    
    @classmethod
    def get_ui_config(cls) -> Dict[str, Any]:
        """获取UI配置"""
        return cls.UI_CONFIG.copy()
