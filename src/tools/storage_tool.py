"""
存储工具 - 使用S3对象存储
支持文件上传、下载、管理
"""
import os
import json
from typing import Optional
from langchain.tools import tool
from coze_coding_dev_sdk.s3 import S3SyncStorage


def _get_storage():
    """获取存储客户端"""
    return S3SyncStorage(
        endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
        access_key="",
        secret_key="",
        bucket_name=os.getenv("COZE_BUCKET_NAME"),
        region="cn-beijing",
    )


@tool
def upload_file(
    content: str,
    file_name: str,
    content_type: str = "text/plain"
) -> str:
    """
    上传文件到对象存储。支持文本、JSON、代码等。
    
    参数:
        content: 文件内容（字符串）
        file_name: 文件名，如 "result.txt", "data.json"
        content_type: 内容类型，默认 "text/plain"
            - 文本: "text/plain"
            - JSON: "application/json"
            - CSV: "text/csv"
            - HTML: "text/html"
    
    返回:
        文件的下载链接（有效期24小时）
    
    示例:
        upload_file("Hello World", "hello.txt")
        upload_file('{"name": "test"}', "data.json", "application/json")
    """
    try:
        storage = _get_storage()
        
        # 上传文件
        key = storage.upload_file(
            file_content=content.encode('utf-8'),
            file_name=file_name,
            content_type=content_type,
        )
        
        # 生成下载链接（24小时有效）
        url = storage.generate_presigned_url(key=key, expire_time=86400)
        
        return json.dumps({
            'success': True,
            'file_key': key,
            'download_url': url,
            'expires_in': '24小时'
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False)


@tool
def upload_binary_file(
    file_path: str,
    content_type: str = "application/octet-stream"
) -> str:
    """
    上传本地二进制文件到对象存储。用于上传图片、压缩包等。
    
    参数:
        file_path: 本地文件路径
        content_type: 内容类型
            - 图片: "image/png", "image/jpeg"
            - ZIP: "application/zip"
            - PDF: "application/pdf"
    
    示例:
        upload_binary_file("/tmp/screenshot.png", "image/png")
        upload_binary_file("/tmp/data.zip", "application/zip")
    """
    try:
        storage = _get_storage()
        
        if not os.path.exists(file_path):
            return json.dumps({'success': False, 'error': f'文件不存在: {file_path}'}, ensure_ascii=False)
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        file_name = os.path.basename(file_path)
        
        key = storage.upload_file(
            file_content=content,
            file_name=file_name,
            content_type=content_type,
        )
        
        url = storage.generate_presigned_url(key=key, expire_time=86400)
        
        return json.dumps({
            'success': True,
            'file_key': key,
            'download_url': url,
            'file_size': len(content)
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False)


@tool
def download_file(file_key: str) -> str:
    """
    从对象存储下载文件内容。仅适用于文本文件。
    
    参数:
        file_key: 文件的key（上传时返回的）
    
    返回:
        文件内容
    """
    try:
        storage = _get_storage()
        
        content = storage.read_file(file_key=file_key)
        
        # 尝试解码为文本
        try:
            text = content.decode('utf-8')
            if len(text) > 5000:
                text = text[:5000] + "\n... (内容过长，已截断)"
            return text
        except UnicodeDecodeError:
            return f"二进制文件，大小: {len(content)} 字节。请使用 download_url 获取。"
        
    except Exception as e:
        return f"下载错误: {str(e)}"


@tool
def get_download_url(file_key: str, expire_hours: int = 24) -> str:
    """
    获取文件的下载链接。
    
    参数:
        file_key: 文件的key
        expire_hours: 链接有效期（小时），默认24小时
    
    返回:
        下载链接
    """
    try:
        storage = _get_storage()
        
        url = storage.generate_presigned_url(
            key=file_key,
            expire_time=expire_hours * 3600
        )
        
        return json.dumps({
            'success': True,
            'download_url': url,
            'expires_in': f'{expire_hours}小时'
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False)


@tool
def list_uploaded_files(prefix: str = "", limit: int = 20) -> str:
    """
    列出对象存储中的文件。
    
    参数:
        prefix: 文件前缀筛选，如 "result/"
        limit: 返回数量限制
    """
    try:
        storage = _get_storage()
        
        result = storage.list_files(prefix=prefix, max_keys=limit)
        
        files = result.get('keys', [])
        
        if not files:
            return "没有找到文件"
        
        output = [f"📁 存储文件列表 (共 {len(files)} 个):\n"]
        
        for key in files[:limit]:
            output.append(f"  - {key}")
        
        if len(files) > limit:
            output.append(f"\n  ... 还有 {len(files) - limit} 个文件")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"查询错误: {str(e)}"


@tool
def delete_file(file_key: str) -> str:
    """
    删除对象存储中的文件。
    
    参数:
        file_key: 文件的key
    """
    try:
        storage = _get_storage()
        
        success = storage.delete_file(file_key=file_key)
        
        if success:
            return json.dumps({
                'success': True,
                'message': f'文件 {file_key} 已删除'
            }, ensure_ascii=False)
        else:
            return json.dumps({'success': False, 'error': '删除失败'}, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False)


@tool
def upload_from_url(url: str) -> str:
    """
    从URL下载文件并上传到对象存储。
    
    参数:
        url: 文件的URL地址
    
    示例:
        upload_from_url("https://example.com/image.png")
    """
    try:
        storage = _get_storage()
        
        key = storage.upload_from_url(url=url, timeout=60)
        
        download_url = storage.generate_presigned_url(key=key, expire_time=86400)
        
        return json.dumps({
            'success': True,
            'file_key': key,
            'download_url': download_url
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False)


# 导出所有工具
STORAGE_TOOLS = [
    upload_file,
    upload_binary_file,
    download_file,
    get_download_url,
    list_uploaded_files,
    delete_file,
    upload_from_url,
]
