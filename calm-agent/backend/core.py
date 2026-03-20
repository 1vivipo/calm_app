"""
平静AI Agent - 核心引擎
"""
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from coze_coding_dev_sdk import LLMClient
from coze_coding_utils.runtime_ctx.context import new_context
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from loguru import logger
import re
import json
from backend.models import Message, MessageType
from backend.session import session_manager
from backend.tools import tools_manager
from config.config import Config
from config.prompts import SYSTEM_PROMPT


class CalmAgent:
    """平静AI Agent核心引擎"""
    
    def __init__(self):
        """初始化Agent"""
        self.config = Config
        self.system_prompt = SYSTEM_PROMPT
        logger.info("平静AI Agent初始化完成")
    
    def _should_use_tool(self, user_message: str) -> Optional[Dict[str, Any]]:
        """
        判断是否需要使用工具
        
        Args:
            user_message: 用户消息
            
        Returns:
            工具调用信息，不需要则返回None
        """
        message_lower = user_message.lower()
        
        # 网页搜索触发词
        search_keywords = ["搜索", "查询", "查找", "最新", "新闻", "天气", "股票", "汇率", "搜索一下", "帮我查"]
        if any(keyword in message_lower for keyword in search_keywords):
            return {
                "tool": "web_search",
                "prompt": user_message
            }
        
        # 图像生成触发词
        image_keywords = ["生成图片", "画一张", "创作图片", "生成图像", "画个", "画一幅", "帮我画"]
        if any(keyword in message_lower for keyword in image_keywords):
            return {
                "tool": "image_generation",
                "prompt": user_message
            }
        
        # 视频生成触发词
        video_keywords = ["生成视频", "制作视频", "创作视频", "生成一段视频"]
        if any(keyword in message_lower for keyword in video_keywords):
            return {
                "tool": "video_generation",
                "prompt": user_message
            }
        
        # 语音合成触发词
        tts_keywords = ["转语音", "读出来", "朗读", "语音合成", "转换成语音"]
        if any(keyword in message_lower for keyword in tts_keywords):
            return {
                "tool": "text_to_speech",
                "prompt": user_message
            }
        
        # 文档生成触发词
        doc_keywords = ["生成文档", "生成pdf", "生成word", "生成excel", "导出文档", "制作文档"]
        if any(keyword in message_lower for keyword in doc_keywords):
            # 检测文档格式
            format = "pdf"
            if "word" in message_lower or "docx" in message_lower:
                format = "docx"
            elif "excel" in message_lower or "xlsx" in message_lower:
                format = "xlsx"
            
            return {
                "tool": "document_generation",
                "prompt": user_message,
                "format": format
            }
        
        return None
    
    async def chat(
        self,
        user_message: str,
        session_id: Optional[str] = None,
        files: Optional[List[str]] = None,
        enable_thinking: bool = False,
        stream: bool = False
    ) -> Union[Dict[str, Any], AsyncGenerator[str, None]]:
        """
        与Agent对话
        
        Args:
            user_message: 用户消息
            session_id: 会话ID
            files: 文件URL列表（图片、视频等）
            enable_thinking: 是否启用思考模式
            stream: 是否流式输出
            
        Returns:
            响应结果或流式生成器
        """
        try:
            # 获取或创建会话
            if session_id is None:
                session = session_manager.create_session()
                session_id = session.session_id
            else:
                session = session_manager.get_session(session_id)
                if not session:
                    session = session_manager.create_session(session_id)
                    session_id = session.session_id
            
            logger.info(f"会话 {session_id} - 用户消息: {user_message[:50]}...")
            
            # 添加用户消息到历史
            session_manager.add_message(
                session_id=session_id,
                role="user",
                content=user_message
            )
            
            # 准备消息列表
            messages = [SystemMessage(content=self.system_prompt)]
            
            # 添加历史消息
            history_messages = session_manager.get_messages(session_id)
            for msg in history_messages[:-1]:  # 排除刚添加的用户消息
                if msg.role == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    messages.append(AIMessage(content=msg.content))
            
            # 添加当前用户消息（支持多模态）
            if files:
                # 多模态消息
                content = [{"type": "text", "text": user_message}]
                for file_url in files:
                    if any(ext in file_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        content.append({
                            "type": "image_url",
                            "image_url": {"url": file_url}
                        })
                    elif any(ext in file_url.lower() for ext in ['.mp4', '.avi', '.mov', '.webm']):
                        content.append({
                            "type": "video_url",
                            "video_url": {"url": file_url}
                        })
                messages.append(HumanMessage(content=content))
            else:
                messages.append(HumanMessage(content=user_message))
            
            # 检查是否需要使用工具
            tool_info = self._should_use_tool(user_message)
            tool_result = None
            tool_used = None
            
            # 执行工具调用
            if tool_info:
                tool_used = tool_info["tool"]
                logger.info(f"调用工具: {tool_used}")
                
                if tool_used == "web_search":
                    # 提取搜索关键词
                    search_query = re.sub(r'^(搜索|查询|查找|搜索一下|帮我查)', '', user_message).strip()
                    tool_result = await tools_manager.web_search(search_query)
                    
                    if tool_result["success"]:
                        # 将搜索结果添加到上下文
                        search_context = f"\n\n搜索结果:\n"
                        if tool_result.get("summary"):
                            search_context += f"摘要: {tool_result['summary']}\n\n"
                        search_context += "相关结果:\n"
                        for i, item in enumerate(tool_result["results"][:5], 1):
                            search_context += f"{i}. {item['title']}\n   {item['snippet']}\n   URL: {item['url']}\n\n"
                        
                        messages.append(HumanMessage(content=f"基于以下搜索结果回答问题: {search_context}"))
                
                elif tool_used == "image_generation":
                    # 提取图像描述
                    image_prompt = re.sub(r'^(生成图片|画一张|创作图片|生成图像|画个|画一幅|帮我画)', '', user_message).strip()
                    tool_result = await tools_manager.generate_image(image_prompt)
                    
                    if tool_result["success"]:
                        return {
                            "response": f"已为您生成图片！\n\n图片链接: {tool_result['image_urls'][0]}",
                            "session_id": session_id,
                            "tool_used": tool_used,
                            "tool_result": tool_result,
                            "success": True
                        }
                
                elif tool_used == "video_generation":
                    # 提取视频描述
                    video_prompt = re.sub(r'^(生成视频|制作视频|创作视频|生成一段视频)', '', user_message).strip()
                    tool_result = await tools_manager.generate_video(video_prompt)
                    
                    if tool_result["success"]:
                        return {
                            "response": f"已为您生成视频！\n\n视频链接: {tool_result['video_url']}",
                            "session_id": session_id,
                            "tool_used": tool_used,
                            "tool_result": tool_result,
                            "success": True
                        }
                
                elif tool_used == "text_to_speech":
                    # 提取要转换的文本
                    text_to_convert = re.sub(r'^(转语音|读出来|朗读|语音合成|转换成语音)', '', user_message).strip()
                    tool_result = await tools_manager.text_to_speech(text_to_convert)
                    
                    if tool_result["success"]:
                        return {
                            "response": f"已将文本转换为语音！\n\n音频链接: {tool_result['audio_url']}",
                            "session_id": session_id,
                            "tool_used": tool_used,
                            "tool_result": tool_result,
                            "success": True
                        }
                
                elif tool_used == "document_generation":
                    # 使用AI生成文档内容
                    doc_prompt = f"请根据以下要求生成文档内容（Markdown格式）:\n{user_message}"
                    messages.append(HumanMessage(content=doc_prompt))
            
            # 调用LLM
            ctx = new_context(method="chat")
            client = LLMClient(ctx=ctx)
            
            model = Config.DEFAULT_MODEL
            if enable_thinking:
                model = Config.THINKING_MODEL
            elif files:
                model = Config.VISION_MODEL
            
            logger.info(f"调用模型: {model}")
            
            if stream:
                # 流式输出
                async def stream_response():
                    full_response = ""
                    try:
                        for chunk in client.stream(
                            messages=messages,
                            model=model,
                            temperature=Config.MODEL_CONFIG["temperature"],
                            thinking="enabled" if enable_thinking else "disabled"
                        ):
                            if chunk.content:
                                if isinstance(chunk.content, str):
                                    text = chunk.content
                                elif isinstance(chunk.content, list):
                                    text = ""
                                    for item in chunk.content:
                                        if isinstance(item, dict) and item.get("type") == "text":
                                            text += item.get("text", "")
                                        elif isinstance(item, str):
                                            text += item
                                else:
                                    text = str(chunk.content)
                                
                                full_response += text
                                yield f"data: {text}\n\n"
                        
                        # 保存AI响应
                        session_manager.add_message(
                            session_id=session_id,
                            role="assistant",
                            content=full_response
                        )
                        
                        yield "data: [DONE]\n\n"
                    except Exception as e:
                        logger.error(f"流式响应失败: {str(e)}")
                        yield f"data: [ERROR] {str(e)}\n\n"
                
                return stream_response()
            else:
                # 非流式输出
                response = client.invoke(
                    messages=messages,
                    model=model,
                    temperature=Config.MODEL_CONFIG["temperature"],
                    thinking="enabled" if enable_thinking else "disabled"
                )
                
                # 安全地获取文本内容
                content = response.content
                if isinstance(content, str):
                    ai_response = content
                elif isinstance(content, list):
                    # 处理列表格式的内容
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                        elif isinstance(item, str):
                            text_parts.append(item)
                    ai_response = " ".join(text_parts)
                else:
                    ai_response = str(content)
                
                # 如果使用了文档生成工具
                if tool_used == "document_generation" and tool_info:
                    doc_result = await tools_manager.generate_document(
                        content=ai_response,
                        format=tool_info.get("format", "pdf")
                    )
                    if doc_result["success"]:
                        ai_response += f"\n\n文档已生成！下载链接: {doc_result['download_url']}"
                        tool_result = doc_result
                
                # 保存AI响应
                session_manager.add_message(
                    session_id=session_id,
                    role="assistant",
                    content=ai_response
                )
                
                logger.info(f"会话 {session_id} - AI响应: {ai_response[:50]}...")
                
                return {
                    "response": ai_response,
                    "session_id": session_id,
                    "tool_used": tool_used,
                    "tool_result": tool_result,
                    "success": True
                }
        
        except Exception as e:
            logger.error(f"对话处理失败: {str(e)}")
            return {
                "response": f"抱歉，处理您的请求时出现错误: {str(e)}",
                "session_id": session_id,
                "success": False,
                "error": str(e)
            }
    
    def clear_session(self, session_id: str) -> bool:
        """
        清空会话历史
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功
        """
        return session_manager.clear_session(session_id)


# 全局Agent实例
calm_agent = CalmAgent()
