#!/usr/bin/env python3
"""
平静AI Agent - 主运行文件
"""
import os
import sys
import subprocess
import argparse
from loguru import logger

# 配置日志
logger.add(
    "/app/work/logs/bypass/calm_agent.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO"
)


def start_streamlit(host: str = "0.0.0.0", port: int = 8501):
    """
    启动Streamlit前端服务
    
    Args:
        host: 主机地址
        port: 端口号
    """
    logger.info(f"启动平静AI Agent服务 - {host}:{port}")
    
    # 获取前端应用路径
    app_path = os.path.join(os.path.dirname(__file__), "frontend", "app.py")
    
    # 启动Streamlit
    cmd = [
        "streamlit", "run", app_path,
        "--server.address", host,
        "--server.port", str(port),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    logger.info(f"执行命令: {' '.join(cmd)}")
    subprocess.run(cmd)


def start_api(host: str = "0.0.0.0", port: int = 8000):
    """
    启动API服务
    
    Args:
        host: 主机地址
        port: 端口号
    """
    logger.info(f"启动平静AI Agent API服务 - {host}:{port}")
    
    # 启动FastAPI
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from backend import calm_agent, ChatRequest, ChatResponse
    from pydantic import BaseModel
    
    app = FastAPI(
        title="平静AI Agent API",
        description="具备多模态能力的高级AI助手API",
        version="1.0.0"
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "name": "平静AI Agent",
            "version": "1.0.0",
            "status": "running"
        }
    
    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        """聊天接口"""
        response = await calm_agent.chat(
            user_message=request.message,
            session_id=request.session_id,
            files=request.files,
            enable_thinking=request.enable_thinking
        )
        return ChatResponse(**response)
    
    @app.delete("/session/{session_id}")
    async def clear_session(session_id: str):
        """清空会话"""
        success = calm_agent.clear_session(session_id)
        return {"success": success}
    
    uvicorn.run(app, host=host, port=port)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="平静AI Agent")
    parser.add_argument(
        "command",
        choices=["start", "api", "all"],
        help="运行命令: start(前端), api(API服务), all(全部)"
    )
    parser.add_argument("--host", default="0.0.0.0", help="主机地址")
    parser.add_argument("--port", type=int, default=8501, help="端口号")
    parser.add_argument("--api-port", type=int, default=8000, help="API端口号")
    
    args = parser.parse_args()
    
    if args.command == "start":
        start_streamlit(args.host, args.port)
    elif args.command == "api":
        start_api(args.host, args.api_port)
    elif args.command == "all":
        # 同时启动前端和API服务
        import threading
        
        # API服务在后台运行
        api_thread = threading.Thread(
            target=start_api,
            args=(args.host, args.api_port),
            daemon=True
        )
        api_thread.start()
        
        # 主线程运行Streamlit
        start_streamlit(args.host, args.port)


if __name__ == "__main__":
    main()
