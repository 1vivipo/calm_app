"""
多模态工具 - 图片识别与理解
提供图片识别、OCR、图表分析、视频理解等能力
"""

import json
import base64
import re
from typing import Optional, List
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context
from coze_coding_dev_sdk import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage

# 多模态模型配置
VISION_MODEL = "doubao-seed-1-6-vision-250815"


def _get_text_content(content) -> str:
    """安全地从AIMessage.content提取文本"""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        if content and isinstance(content[0], str):
            return " ".join(content)
        else:
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            return " ".join(text_parts)
    return str(content)


def _is_base64(s: str) -> bool:
    """检查字符串是否为Base64编码"""
    try:
        if re.match(r'^data:image/', s):
            return True
        # 尝试解码一小部分来验证
        base64.b64decode(s[:100])
        return True
    except Exception:
        return False


@tool
def analyze_image(
    image_url: str,
    question: str = "请详细描述这张图片的内容",
    runtime: ToolRuntime = None
) -> str:
    """
    分析图片内容，回答关于图片的问题。
    
    适用场景：
    - 识别图片中的物体、场景、人物
    - 描述图片内容
    - 回答关于图片的具体问题
    - 分析图片细节
    
    Args:
        image_url: 图片URL地址或Base64编码（支持data:image/xxx;base64,...格式）
        question: 关于图片的问题，默认为"请详细描述这张图片的内容"
        runtime: 工具运行时上下文（自动注入）
    
    Returns:
        对图片的分析结果
    """
    ctx = runtime.context if runtime else new_context(method="analyze_image")
    
    try:
        # 构建消息内容
        content = [
            {
                "type": "text",
                "text": question
            }
        ]
        
        # 处理Base64或URL
        if _is_base64(image_url):
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            })
        else:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            })
        
        messages = [
            SystemMessage(content="你是一个专业的图片分析助手，能够准确识别和分析图片内容，回答用户关于图片的问题。请用中文回答。"),
            HumanMessage(content=content)
        ]
        
        client = LLMClient(ctx=ctx)
        response = client.invoke(
            messages=messages,
            model=VISION_MODEL,
            temperature=0.3
        )
        
        return _get_text_content(response.content)
        
    except Exception as e:
        return f"图片分析失败: {str(e)}"


@tool
def extract_text_from_image(
    image_url: str,
    runtime: ToolRuntime = None
) -> str:
    """
    从图片中提取文字（OCR）。
    
    适用场景：
    - 识别文档、证件、截图中的文字
    - 提取图片中的文字内容
    - 读取图片中的文本信息
    
    Args:
        image_url: 图片URL地址或Base64编码
        runtime: 工具运行时上下文（自动注入）
    
    Returns:
        从图片中提取的文字内容
    """
    ctx = runtime.context if runtime else new_context(method="extract_text_from_image")
    
    try:
        content = [
            {
                "type": "text",
                "text": "请仔细识别这张图片中的所有文字，并按原始格式输出。保持原有的换行和段落结构。如果没有文字，请说明。"
            }
        ]
        
        if _is_base64(image_url):
            content.append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
        else:
            content.append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
        
        messages = [
            SystemMessage(content="你是一个专业的OCR助手，擅长从图片中准确提取文字内容。请保持原文格式。"),
            HumanMessage(content=content)
        ]
        
        client = LLMClient(ctx=ctx)
        response = client.invoke(
            messages=messages,
            model=VISION_MODEL,
            temperature=0.1
        )
        
        return _get_text_content(response.content)
        
    except Exception as e:
        return f"文字提取失败: {str(e)}"


@tool
def analyze_chart(
    image_url: str,
    runtime: ToolRuntime = None
) -> str:
    """
    分析图表（柱状图、折线图、饼图等）。
    
    适用场景：
    - 分析数据图表、统计图
    - 读取图表中的数值
    - 总结图表趋势和关键信息
    
    Args:
        image_url: 图表图片URL地址或Base64编码
        runtime: 工具运行时上下文（自动注入）
    
    Returns:
        图表分析结果，包含数据解读和趋势分析
    """
    ctx = runtime.context if runtime else new_context(method="analyze_chart")
    
    try:
        content = [
            {
                "type": "text",
                "text": """请分析这张图表，提供以下信息：
1. 图表类型（柱状图、折线图、饼图等）
2. 图表主题和标题
3. 主要数据点和数值
4. 数据趋势和规律
5. 关键洞察和结论

请用中文详细回答。"""
            }
        ]
        
        if _is_base64(image_url):
            content.append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
        else:
            content.append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
        
        messages = [
            SystemMessage(content="你是一个数据分析专家，擅长解读各类图表和数据可视化内容。"),
            HumanMessage(content=content)
        ]
        
        client = LLMClient(ctx=ctx)
        response = client.invoke(
            messages=messages,
            model=VISION_MODEL,
            temperature=0.3
        )
        
        return _get_text_content(response.content)
        
    except Exception as e:
        return f"图表分析失败: {str(e)}"


@tool
def compare_images(
    image_url1: str,
    image_url2: str,
    question: str = "请比较这两张图片的异同",
    runtime: ToolRuntime = None
) -> str:
    """
    比较两张图片的异同。
    
    适用场景：
    - 比较两张图片的差异
    - 对比产品、设计稿
    - 找出图片间的变化
    
    Args:
        image_url1: 第一张图片URL或Base64编码
        image_url2: 第二张图片URL或Base64编码
        question: 比较的问题，默认为"请比较这两张图片的异同"
        runtime: 工具运行时上下文（自动注入）
    
    Returns:
        图片比较结果
    """
    ctx = runtime.context if runtime else new_context(method="compare_images")
    
    try:
        content = [
            {"type": "text", "text": question}
        ]
        
        # 添加两张图片
        for url in [image_url1, image_url2]:
            if _is_base64(url):
                content.append({
                    "type": "image_url",
                    "image_url": {"url": url}
                })
            else:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": url}
                })
        
        messages = [
            SystemMessage(content="你是一个专业的图片对比分析助手，能够准确找出两张图片之间的异同点。"),
            HumanMessage(content=content)
        ]
        
        client = LLMClient(ctx=ctx)
        response = client.invoke(
            messages=messages,
            model=VISION_MODEL,
            temperature=0.3
        )
        
        return _get_text_content(response.content)
        
    except Exception as e:
        return f"图片比较失败: {str(e)}"


@tool
def detect_objects(
    image_url: str,
    object_type: str = "所有物体",
    runtime: ToolRuntime = None
) -> str:
    """
    检测图片中的特定物体并返回位置坐标。
    
    适用场景：
    - 检测图片中的人、车、动物等物体
    - 获取物体的边界框坐标
    - 统计图片中物体的数量
    
    Args:
        image_url: 图片URL地址或Base64编码
        object_type: 要检测的物体类型，如"人"、"车"、"猫"等，默认检测所有物体
        runtime: 工具运行时上下文（自动注入）
    
    Returns:
        检测到的物体列表及其位置坐标（JSON格式）
    """
    ctx = runtime.context if runtime else new_context(method="detect_objects")
    
    try:
        prompt = f"""请检测这张图片中的"{object_type}"，并输出它们的边界框坐标。

输出格式（JSON）：
{{
  "detected": true,
  "count": 数量,
  "objects": [
    {{
      "label": "物体名称",
      "confidence": 置信度(0-1),
      "bbox": {{
        "topLeftX": x_min,
        "topLeftY": y_min,
        "bottomRightX": x_max,
        "bottomRightY": y_max
      }}
    }}
  ]
}}

注意：坐标是相对值(0-1000)，(0,0)是左上角。
如果检测不到指定物体，请返回{{"detected": false, "count": 0, "objects": []}}"""
        
        content = [
            {"type": "text", "text": prompt}
        ]
        
        if _is_base64(image_url):
            content.append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
        else:
            content.append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
        
        messages = [
            SystemMessage(content="你是一个专业的物体检测助手，能够准确识别图片中的物体并输出其位置坐标。"),
            HumanMessage(content=content)
        ]
        
        client = LLMClient(ctx=ctx)
        response = client.invoke(
            messages=messages,
            model=VISION_MODEL,
            temperature=0.1
        )
        
        return _get_text_content(response.content)
        
    except Exception as e:
        return f"物体检测失败: {str(e)}"


@tool
def analyze_video(
    video_url: str,
    question: str = "请分析这个视频的主要内容",
    runtime: ToolRuntime = None
) -> str:
    """
    分析视频内容。
    
    适用场景：
    - 理解视频的主要内容
    - 分析视频中的场景和动作
    - 总结视频信息
    
    Args:
        video_url: 视频URL地址
        question: 关于视频的问题，默认为"请分析这个视频的主要内容"
        runtime: 工具运行时上下文（自动注入）
    
    Returns:
        视频分析结果
    """
    ctx = runtime.context if runtime else new_context(method="analyze_video")
    
    try:
        content = [
            {"type": "text", "text": question},
            {
                "type": "video_url",
                "video_url": {"url": video_url}
            }
        ]
        
        messages = [
            SystemMessage(content="你是一个专业的视频分析助手，能够理解视频内容并回答相关问题。请用中文回答。"),
            HumanMessage(content=content)
        ]
        
        client = LLMClient(ctx=ctx)
        response = client.invoke(
            messages=messages,
            model=VISION_MODEL,
            temperature=0.3
        )
        
        return _get_text_content(response.content)
        
    except Exception as e:
        return f"视频分析失败: {str(e)}"


@tool
def describe_image_for_blind(
    image_url: str,
    runtime: ToolRuntime = None
) -> str:
    """
    为视障用户描述图片内容（无障碍描述）。
    
    适用场景：
    - 为视障人士提供图片描述
    - 生成图片的alt文本
    - 提供详细的图片无障碍说明
    
    Args:
        image_url: 图片URL地址或Base64编码
        runtime: 工具运行时上下文（自动注入）
    
    Returns:
        详细的图片描述，适合视障用户理解
    """
    ctx = runtime.context if runtime else new_context(method="describe_image_for_blind")
    
    try:
        content = [
            {
                "type": "text",
                "text": """请为这张图片提供详细的无障碍描述，帮助视障用户理解图片内容。

描述要求：
1. 首先概括图片的主要内容
2. 描述图片中的主要元素、颜色、布局
3. 说明图片传达的信息或情感
4. 如果有文字，请读出文字内容
5. 如果是场景，描述氛围和环境

请用清晰、详细的语言描述。"""
            }
        ]
        
        if _is_base64(image_url):
            content.append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
        else:
            content.append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
        
        messages = [
            SystemMessage(content="你是一个专业的无障碍描述助手，致力于帮助视障用户理解图片内容。"),
            HumanMessage(content=content)
        ]
        
        client = LLMClient(ctx=ctx)
        response = client.invoke(
            messages=messages,
            model=VISION_MODEL,
            temperature=0.5
        )
        
        return _get_text_content(response.content)
        
    except Exception as e:
        return f"图片描述失败: {str(e)}"


# 导出所有工具
__all__ = [
    'analyze_image',
    'extract_text_from_image',
    'analyze_chart',
    'compare_images',
    'detect_objects',
    'analyze_video',
    'describe_image_for_blind'
]
