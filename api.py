"""
平静AI - Agent API端点
供移动端App调用
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import build_agent

app = FastAPI(title="平静AI API", version="1.0.0")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储会话
_sessions = {}

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """对话接口"""
    try:
        # 获取或创建会话ID
        conv_id = request.conversation_id or str(uuid.uuid4())
        
        # 构建Agent
        agent = build_agent()
        
        # 调用Agent
        config = {"configurable": {"thread_id": conv_id}}
        result = agent.invoke(
            {"messages": [("user", request.message)]},
            config=config
        )
        
        # 提取响应
        response_text = ""
        if result and "messages" in result:
            for msg in reversed(result["messages"]):
                if hasattr(msg, 'content') and msg.type != "human":
                    response_text = msg.content
                    break
        
        return ChatResponse(
            response=response_text or "抱歉，我没能理解您的问题。",
            conversation_id=conv_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "service": "平静AI"}

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "平静AI API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "health": "/health"
        }
    }
