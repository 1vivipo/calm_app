"""
图片生成工具 - AI绘画
支持文生图、图生图、多图并行生成
"""
import os
import base64
import requests
from typing import Optional, List
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context
from coze_coding_dev_sdk import ImageGenerationClient


@tool
def generate_image(
    prompt: str,
    size: str = "2K",
    reference_image: Optional[str] = None,
    watermark: bool = False,
    runtime: ToolRuntime = None
) -> str:
    """
    根据文字描述生成图片。支持各种风格的图片创作。
    
    适用场景：
    - 生成插画、海报、壁纸
    - 产品图、概念图
    - 风景、人物、动物等
    - 图生图（基于参考图生成）
    
    Args:
        prompt: 图片描述，越详细效果越好。如："一片金黄色的油菜花田，蓝天白云，阳光明媚"
        size: 图片尺寸，可选 "2K"(默认)、"4K" 或 "宽x高"（如1920x1080）
        reference_image: 参考图片URL（可选），用于图生图
        watermark: 是否添加水印，默认False
        runtime: 工具运行时上下文（自动注入）
    
    Returns:
        生成的图片URL，或错误信息
    
    示例:
        generate_image("一只可爱的猫咪在阳光下打盹")
        generate_image("未来城市，赛博朋克风格", size="4K")
        generate_image("转为动漫风格", reference_image="https://example.com/photo.jpg")
    """
    ctx = runtime.context if runtime else new_context(method="generate_image")
    
    try:
        client = ImageGenerationClient(ctx=ctx)
        
        # 调用生成API
        response = client.generate(
            prompt=prompt,
            size=size,
            image=reference_image,
            watermark=watermark
        )
        
        if response.success and response.image_urls:
            url = response.image_urls[0]
            return f"✅ 图片生成成功！\n\n📷 图片链接：{url}\n\n提示词：{prompt}\n尺寸：{size}"
        else:
            errors = response.error_messages if hasattr(response, 'error_messages') else ["未知错误"]
            return f"❌ 图片生成失败: {', '.join(errors)}"
            
    except Exception as e:
        return f"❌ 图片生成出错: {str(e)}"


@tool
def generate_multiple_images(
    prompts: List[str],
    size: str = "2K",
    watermark: bool = False,
    runtime: ToolRuntime = None
) -> str:
    """
    批量生成多张图片。适合需要生成多个不同场景的情况。
    
    适用场景：
    - 批量生成不同风格的图片
    - 连环画/故事插图
    - 多个概念设计稿
    
    Args:
        prompts: 图片描述列表，每个元素是一个描述
        size: 图片尺寸，默认"2K"
        watermark: 是否添加水印，默认False
        runtime: 工具运行时上下文（自动注入）
    
    Returns:
        所有生成的图片URL列表
    
    示例:
        generate_multiple_images([
            "一片油菜花田",
            "向日葵花海",
            "薰衣草庄园"
        ])
    """
    ctx = runtime.context if runtime else new_context(method="generate_multiple_images")
    
    try:
        import asyncio
        
        client = ImageGenerationClient(ctx=ctx)
        
        async def generate_all():
            tasks = [
                client.generate_async(prompt=prompt, size=size, watermark=watermark)
                for prompt in prompts
            ]
            return await asyncio.gather(*tasks)
        
        responses = asyncio.run(generate_all())
        
        results = []
        for i, response in enumerate(responses):
            if response.success and response.image_urls:
                results.append(f"图片{i+1}: {response.image_urls[0]}")
            else:
                results.append(f"图片{i+1}: 生成失败")
        
        return f"✅ 批量生成完成（{len(prompts)}张）:\n\n" + "\n".join(results)
        
    except Exception as e:
        return f"❌ 批量生成出错: {str(e)}"


@tool
def generate_story_images(
    story_prompt: str,
    num_images: int = 4,
    size: str = "2K",
    runtime: ToolRuntime = None
) -> str:
    """
    根据故事描述生成连续的图片序列。适合生成连环画、故事插图。
    
    适用场景：
    - 连环画创作
    - 故事绘本
    - 漫画分镜
    
    Args:
        story_prompt: 故事描述或主题
        num_images: 要生成的图片数量（1-15），默认4
        size: 图片尺寸，默认"2K"
        runtime: 工具运行时上下文（自动注入）
    
    Returns:
        按顺序排列的图片URL列表
    
    示例:
        generate_story_images("一只小猫的冒险旅程", num_images=5)
        generate_story_images("春天来了，万物复苏的故事", num_images=4)
    """
    ctx = runtime.context if runtime else new_context(method="generate_story_images")
    
    try:
        client = ImageGenerationClient(ctx=ctx)
        
        response = client.generate(
            prompt=story_prompt,
            size=size,
            sequential_image_generation="auto",
            sequential_image_generation_max_images=min(num_images, 15)
        )
        
        if response.success and response.image_urls:
            results = []
            for i, url in enumerate(response.image_urls, 1):
                results.append(f"第{i}张: {url}")
            
            return f"✅ 故事图片生成完成（{len(response.image_urls)}张）:\n\n" + "\n".join(results)
        else:
            errors = response.error_messages if hasattr(response, 'error_messages') else ["未知错误"]
            return f"❌ 故事图片生成失败: {', '.join(errors)}"
            
    except Exception as e:
        return f"❌ 故事图片生成出错: {str(e)}"


@tool
def save_image_to_storage(
    image_url: str,
    file_name: str,
    runtime: ToolRuntime = None
) -> str:
    """
    将图片URL保存到对象存储，获取永久下载链接。
    
    适用场景：
    - 保存生成的图片
    - 保存网络图片到云端
    
    Args:
        image_url: 图片URL
        file_name: 保存的文件名，如 "my_image.png"
        runtime: 工具运行时上下文（自动注入）
    
    Returns:
        永久下载链接
    """
    ctx = runtime.context if runtime else new_context(method="save_image_to_storage")
    
    try:
        # 下载图片
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # 上传到对象存储
        from coze_coding_dev_sdk.s3 import S3SyncStorage
        
        storage = S3SyncStorage(
            endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
            access_key="",
            secret_key="",
            bucket_name=os.getenv("COZE_BUCKET_NAME"),
            region="cn-beijing",
        )
        
        key = storage.upload_file(
            file_content=response.content,
            file_name=file_name,
            content_type="image/png",
        )
        
        # 生成下载链接
        download_url = storage.generate_presigned_url(key=key, expire_time=86400)
        
        return f"✅ 图片已保存！\n\n📎 下载链接（24小时有效）：{download_url}"
        
    except Exception as e:
        return f"❌ 保存图片失败: {str(e)}"


# 导出所有工具
__all__ = [
    'generate_image',
    'generate_multiple_images',
    'generate_story_images',
    'save_image_to_storage'
]
