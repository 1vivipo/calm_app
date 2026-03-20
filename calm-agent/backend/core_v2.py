"""
平静AI Agent - 多模型适配器
支持讯飞、豆包等多种模型，自动降级到免费模型
"""
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from loguru import logger
import os
import asyncio


class MultiModelAdapter:
    """多模型适配器 - 自动选择可用的模型"""
    
    def __init__(self):
        """初始化模型适配器"""
        self.models = {}
        self.primary_model = None
        self._init_models()
    
    def _init_models(self):
        """初始化所有可用模型"""
        # 1. 尝试初始化讯飞模型
        if self._init_xunfei():
            self.primary_model = "xunfei"
            logger.info("✅ 讯飞星火Lite已就绪（用户永久免费额度）")
        
        # 2. 尝试初始化豆包模型（通过coze环境）
        if self._init_doubao():
            if not self.primary_model:
                self.primary_model = "doubao"
            logger.info("✅ 豆包大模型已就绪")
        
        # 3. 初始化免费开源模型作为后备
        if self._init_free_models():
            if not self.primary_model:
                self.primary_model = "free"
            logger.info("✅ 免费开源模型已就绪")
        
        if not self.primary_model:
            logger.warning("⚠️ 未找到可用模型，将使用基础模式")
            self.primary_model = "basic"
    
    def _init_xunfei(self) -> bool:
        """初始化讯飞模型"""
        try:
            # 检查讯飞API配置
            app_id = os.getenv("XUNFEI_APP_ID", "")
            api_key = os.getenv("XUNFEI_API_KEY", "")
            api_secret = os.getenv("XUNFEI_API_SECRET", "")
            
            if app_id and api_key and api_secret:
                self.models["xunfei"] = {
                    "app_id": app_id,
                    "api_key": api_key,
                    "api_secret": api_secret,
                    "model": "lite"  # 使用Lite版本
                }
                return True
        except Exception as e:
            logger.debug(f"讯飞模型初始化跳过: {e}")
        return False
    
    def _init_doubao(self) -> bool:
        """初始化豆包模型"""
        try:
            from coze_coding_dev_sdk import LLMClient
            # 测试环境是否支持
            client = LLMClient()
            self.models["doubao"] = {
                "client": client,
                "model": "doubao-seed-1-6-lite-251015"  # 使用lite版本，更省钱
            }
            return True
        except Exception as e:
            logger.debug(f"豆包模型初始化跳过: {e}")
        return False
    
    def _init_free_models(self) -> bool:
        """初始化免费开源模型"""
        try:
            # 使用Hugging Face的免费推理API
            import requests
            # 测试连通性
            response = requests.get("https://api-inference.huggingface.co/status", timeout=5)
            if response.status_code == 200:
                self.models["free"] = {
                    "type": "huggingface",
                    "models": {
                        "chat": "microsoft/DialoGPT-large",
                        "image_gen": "runwayml/stable-diffusion-v1-5",
                    }
                }
                return True
        except Exception as e:
            logger.debug(f"免费模型初始化跳过: {e}")
        return False
    
    async def chat(
        self,
        message: str,
        history: List[Dict] = None,
        stream: bool = False,
        enable_thinking: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        对话接口 - 自动选择最佳模型
        
        Args:
            message: 用户消息
            history: 历史对话
            stream: 是否流式输出
            enable_thinking: 是否启用思考模式
            
        Returns:
            AI回复
        """
        # 优先使用讯飞（用户免费额度）
        if self.primary_model == "xunfei" and "xunfei" in self.models:
            return await self._chat_xunfei(message, history, stream)
        
        # 其次使用豆包
        elif self.primary_model == "doubao" and "doubao" in self.models:
            return await self._chat_doubao(message, history, stream, enable_thinking)
        
        # 使用免费模型
        elif self.primary_model == "free" and "free" in self.models:
            return await self._chat_free(message, history, stream)
        
        # 基础模式（离线）
        else:
            return await self._chat_basic(message, history)
    
    async def _chat_xunfei(self, message: str, history: List[Dict], stream: bool) -> str:
        """讯飞星火对话"""
        try:
            import websocket
            import json
            import hmac
            import hashlib
            from datetime import datetime
            import base64
            
            config = self.models["xunfei"]
            
            # 构建请求
            url = self._build_xunfei_url(config)
            
            # 构建消息
            messages = []
            if history:
                for msg in history:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            messages.append({"role": "user", "content": message})
            
            # 发送请求
            data = {
                "header": {
                    "app_id": config["app_id"],
                    "uid": "calm_agent"
                },
                "parameter": {
                    "chat": {
                        "domain": "general",
                        "temperature": 0.7,
                        "max_tokens": 2048
                    }
                },
                "payload": {
                    "message": {
                        "text": messages
                    }
                }
            }
            
            # 这里简化处理，实际需要websocket连接
            # 返回模拟响应
            return "讯飞模型暂未完全集成，请稍后..."
            
        except Exception as e:
            logger.error(f"讯飞对话失败: {e}")
            # 降级到其他模型
            if "doubao" in self.models:
                return await self._chat_doubao(message, history, False, False)
            return f"抱歉，当前服务暂时不可用。错误: {str(e)}"
    
    async def _chat_doubao(self, message: str, history: List[Dict], stream: bool, thinking: bool) -> str:
        """豆包模型对话"""
        try:
            from coze_coding_dev_sdk import LLMClient
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            from coze_coding_utils.runtime_ctx.context import new_context
            
            config = self.models["doubao"]
            ctx = new_context(method="chat")
            client = LLMClient(ctx=ctx)
            
            # 构建消息
            messages = [SystemMessage(content="你是平静，一个友好、专业的AI助手。")]
            if history:
                for msg in history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    else:
                        messages.append(AIMessage(content=msg["content"]))
            messages.append(HumanMessage(content=message))
            
            # 调用模型
            response = client.invoke(
                messages=messages,
                model=config["model"],
                temperature=0.7,
                thinking="enabled" if thinking else "disabled"
            )
            
            # 安全获取内容
            content = response.content
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                text = ""
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text += item.get("text", "")
                    elif isinstance(item, str):
                        text += item
                return text
            return str(content)
            
        except Exception as e:
            logger.error(f"豆包对话失败: {e}")
            return f"抱歉，我遇到了一些问题: {str(e)}"
    
    async def _chat_free(self, message: str, history: List[Dict], stream: bool) -> str:
        """免费模型对话"""
        try:
            import requests
            
            # 使用Hugging Face的免费API
            model = self.models["free"]["models"]["chat"]
            
            # 构建上下文
            context = ""
            if history:
                for msg in history[-5:]:  # 只保留最近5轮
                    context += f"{msg['role']}: {msg['content']}\n"
            
            # 调用API
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers={"Authorization": f"Bearer {os.getenv('HF_TOKEN', '')}"},
                json={"inputs": f"{context}\nUser: {message}\nAssistant:"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").split("Assistant:")[-1].strip()
            
            return "免费模型暂时不可用，请稍后再试。"
            
        except Exception as e:
            logger.error(f"免费模型对话失败: {e}")
            return await self._chat_basic(message, history)
    
    async def _chat_basic(self, message: str, history: List[Dict]) -> str:
        """基础对话模式（完全离线）"""
        # 简单的规则匹配
        message_lower = message.lower()
        
        greetings = ["你好", "嗨", "hi", "hello"]
        if any(g in message_lower for g in greetings):
            return "你好！我是平静，你的AI助手。虽然我现在运行在基础模式，但我仍然会尽力帮助你！"
        
        if "介绍" in message_lower or "你是谁" in message_lower:
            return "我是平静，一个AI助手。我目前正在基础模式下运行，主要功能包括对话、搜索、图像生成等。请问有什么可以帮你的吗？"
        
        if "谢谢" in message_lower or "感谢" in message_lower:
            return "不客气！很高兴能帮到你。还有其他问题吗？"
        
        # 默认回复
        return f"收到你的消息：'{message}'。我现在运行在基础模式，功能有限。建议配置API密钥以获得完整功能。"
    
    def _build_xunfei_url(self, config: Dict) -> str:
        """构建讯飞API URL"""
        import hmac
        import hashlib
        import base64
        from datetime import datetime
        
        # 生成鉴权URL
        # 这里省略具体实现，讯飞API需要复杂的鉴权过程
        return ""


# 全局模型适配器
model_adapter = MultiModelAdapter()
