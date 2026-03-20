"""
平静AI Agent - 工具模块
"""
from typing import Dict, Any, List, Optional, Union
from coze_coding_dev_sdk import (
    SearchClient, 
    ImageGenerationClient, 
    VideoGenerationClient,
    AudioClient,
    DocumentGenerationClient
)
from coze_coding_utils.runtime_ctx.context import new_context
from loguru import logger
import base64
import asyncio


class ToolsManager:
    """工具管理器"""
    
    def __init__(self):
        """初始化工具管理器"""
        self.web_search_client = SearchClient()
        self.image_client = ImageGenerationClient()
        self.video_client = VideoGenerationClient()
        self.audio_client = AudioClient()
        self.doc_client = DocumentGenerationClient()
        logger.info("工具管理器初始化完成")
    
    async def web_search(
        self, 
        query: str, 
        count: int = 10,
        need_summary: bool = True
    ) -> Dict[str, Any]:
        """
        网页搜索工具
        
        Args:
            query: 搜索查询
            count: 结果数量
            need_summary: 是否需要AI摘要
            
        Returns:
            搜索结果
        """
        try:
            logger.info(f"执行网页搜索: {query}")
            ctx = new_context(method="search.web")
            client = SearchClient(ctx=ctx)
            
            response = client.web_search_with_summary(
                query=query,
                count=count
            ) if need_summary else client.web_search(query=query, count=count)
            
            results = []
            if response.web_items:
                for item in response.web_items:
                    results.append({
                        "title": item.title,
                        "url": item.url,
                        "snippet": item.snippet,
                        "site_name": item.site_name,
                        "publish_time": item.publish_time
                    })
            
            return {
                "success": True,
                "summary": response.summary,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"网页搜索失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "2K",
        watermark: bool = False
    ) -> Dict[str, Any]:
        """
        图像生成工具
        
        Args:
            prompt: 图像描述
            size: 图像尺寸 (2K/4K)
            watermark: 是否添加水印
            
        Returns:
            生成结果
        """
        try:
            logger.info(f"生成图像: {prompt[:50]}...")
            ctx = new_context(method="generate")
            client = ImageGenerationClient(ctx=ctx)
            
            response = client.generate(
                prompt=prompt,
                size=size,
                watermark=watermark
            )
            
            if response.success:
                return {
                    "success": True,
                    "image_urls": response.image_urls,
                    "count": len(response.image_urls)
                }
            else:
                return {
                    "success": False,
                    "error": response.error_messages
                }
        except Exception as e:
            logger.error(f"图像生成失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        aspect_ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """
        视频生成工具
        
        Args:
            prompt: 视频描述
            duration: 视频时长（秒）
            aspect_ratio: 宽高比
            
        Returns:
            生成结果
        """
        try:
            logger.info(f"生成视频: {prompt[:50]}...")
            ctx = new_context(method="generate")
            client = VideoGenerationClient(ctx=ctx)
            
            response = await client.generate_async(
                prompt=prompt,
                duration=duration,
                aspect_ratio=aspect_ratio
            )
            
            if response.success:
                return {
                    "success": True,
                    "video_url": response.video_urls[0] if response.video_urls else None,
                    "duration": duration
                }
            else:
                return {
                    "success": False,
                    "error": response.error_messages
                }
        except Exception as e:
            logger.error(f"视频生成失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def text_to_speech(
        self,
        text: str,
        voice: str = "zh_female_shuangkuaisisi_moon_bigtts"
    ) -> Dict[str, Any]:
        """
        语音合成工具
        
        Args:
            text: 要转换的文本
            voice: 声音类型
            
        Returns:
            合成结果
        """
        try:
            logger.info(f"语音合成: {text[:50]}...")
            ctx = new_context(method="tts")
            client = AudioClient(ctx=ctx)
            
            response = client.tts(
                text=text,
                voice=voice
            )
            
            if response.success:
                return {
                    "success": True,
                    "audio_url": response.audio_url,
                    "duration": response.duration
                }
            else:
                return {
                    "success": False,
                    "error": response.error
                }
        except Exception as e:
            logger.error(f"语音合成失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_document(
        self,
        content: str,
        format: str = "pdf",
        filename: str = "document"
    ) -> Dict[str, Any]:
        """
        文档生成工具
        
        Args:
            content: Markdown内容
            format: 文档格式 (pdf/docx/xlsx)
            filename: 文件名
            
        Returns:
            生成结果
        """
        try:
            logger.info(f"生成{format.upper()}文档...")
            ctx = new_context(method="generate")
            client = DocumentGenerationClient(ctx=ctx)
            
            if format == "pdf":
                url = client.create_pdf_from_markdown(content, filename)
            elif format == "docx":
                url = client.create_docx_from_markdown(content, filename)
            elif format == "xlsx":
                # 对于xlsx，需要先解析数据
                url = client.create_xlsx_from_markdown(content, filename)
            else:
                return {
                    "success": False,
                    "error": f"不支持的格式: {format}"
                }
            
            return {
                "success": True,
                "download_url": url,
                "format": format,
                "filename": f"{filename}.{format}"
            }
        except Exception as e:
            logger.error(f"文档生成失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_image(self, image_url: str, question: str = "") -> Dict[str, Any]:
        """
        图像分析工具（使用视觉模型）
        
        Args:
            image_url: 图像URL
            question: 要问的问题
            
        Returns:
            分析结果
        """
        try:
            logger.info(f"分析图像: {image_url}")
            from coze_coding_dev_sdk import LLMClient
            from langchain_core.messages import HumanMessage, SystemMessage
            
            ctx = new_context(method="analyze")
            client = LLMClient(ctx=ctx)
            
            messages = [
                SystemMessage(content="你是一个专业的图像分析助手，能够准确理解和描述图像内容。"),
                HumanMessage(content=[
                    {"type": "text", "text": question or "请详细描述这张图片的内容。"},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ])
            ]
            
            response = client.invoke(
                messages=messages,
                model="doubao-seed-1-6-vision-250815",
                temperature=0.3
            )
            
            # 安全地获取文本内容
            content = response.content
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                # 处理列表格式的内容
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                    elif isinstance(item, str):
                        text_parts.append(item)
                text = " ".join(text_parts)
            else:
                text = str(content)
            
            return {
                "success": True,
                "analysis": text
            }
        except Exception as e:
            logger.error(f"图像分析失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# 全局工具管理器实例
tools_manager = ToolsManager()
