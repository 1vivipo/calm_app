"""
平静AI Agent - 数据模型
"""
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    """消息类型"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"


class ToolType(Enum):
    """工具类型"""
    WEB_SEARCH = "web_search"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    TEXT_TO_SPEECH = "text_to_speech"
    DOCUMENT_GENERATION = "document_generation"


class Message(BaseModel):
    """消息模型"""
    role: str = Field(..., description="角色: user/assistant/system")
    content: Union[str, List[Dict[str, Any]]] = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    message_type: MessageType = Field(default=MessageType.TEXT, description="消息类型")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")


class Session(BaseModel):
    """会话模型"""
    session_id: str = Field(..., description="会话ID")
    messages: List[Message] = Field(default_factory=list, description="消息列表")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="会话元数据")


class ToolCall(BaseModel):
    """工具调用模型"""
    tool_type: ToolType = Field(..., description="工具类型")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="调用参数")
    result: Optional[Any] = Field(default=None, description="调用结果")
    error: Optional[str] = Field(default=None, description="错误信息")


class AgentResponse(BaseModel):
    """Agent响应模型"""
    content: str = Field(..., description="响应内容")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="工具调用记录")
    thinking_process: Optional[str] = Field(default=None, description="思考过程")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(default=None, description="会话ID")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")
    enable_thinking: bool = Field(default=False, description="是否启用思考模式")
    files: Optional[List[str]] = Field(default=None, description="文件URL列表")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str = Field(..., description="AI响应")
    session_id: str = Field(..., description="会话ID")
    tool_used: Optional[str] = Field(default=None, description="使用的工具")
    tool_result: Optional[Any] = Field(default=None, description="工具结果")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")
