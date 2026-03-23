"""
任务管理工具 - 使用Supabase数据库存储任务状态
支持后台任务、状态查询、结果存储
"""
import os
import json
import uuid
from datetime import datetime
from typing import Optional
from langchain.tools import tool

# 导入Supabase客户端
import sys
sys.path.insert(0, os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects") + "/src")
from storage.database.supabase_client import get_supabase_client


def _get_client():
    """获取Supabase客户端"""
    return get_supabase_client()


@tool
def create_task(
    task_type: str,
    command: str,
    user_id: Optional[str] = None,
    extra_data: Optional[dict] = None
) -> str:
    """
    创建一个后台任务。用于需要异步执行的长时间操作。
    
    参数:
        task_type: 任务类型 - "shell"(命令), "python"(代码), "search"(搜索), "custom"(自定义)
        command: 要执行的命令或代码
        user_id: 可选的用户ID
        extra_data: 额外的元数据
    
    返回:
        任务ID，用于后续查询状态和结果
    
    示例:
        create_task("shell", "pip install pandas && python process_data.py")
        create_task("python", "import time; time.sleep(60); print('done')")
    """
    try:
        client = _get_client()
        task_id = str(uuid.uuid4())
        
        task_data = {
            'id': task_id,
            'user_id': user_id,
            'task_type': task_type,
            'status': 'pending',
            'command': command,
            'extra_data': json.dumps(extra_data) if extra_data else None
        }
        
        response = client.table('agent_tasks').insert(task_data).execute()
        
        return json.dumps({
            'success': True,
            'task_id': task_id,
            'message': f'任务已创建，使用 get_task_status("{task_id}") 查询状态'
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False)


@tool
def get_task_status(task_id: str) -> str:
    """
    查询任务状态和结果。
    
    参数:
        task_id: 任务ID
    
    返回:
        任务状态信息，包括状态、结果、错误等
    
    示例:
        get_task_status("abc12345-...")
    """
    try:
        client = _get_client()
        
        response = client.table('agent_tasks').select('*').eq('id', task_id).execute()
        
        if not response.data:
            return json.dumps({'error': f'任务 {task_id} 不存在'}, ensure_ascii=False)
        
        task = response.data[0]
        
        # 格式化输出
        result = {
            'task_id': task['id'],
            'type': task['task_type'],
            'status': task['status'],
            'created_at': task['created_at'],
        }
        
        if task['started_at']:
            result['started_at'] = task['started_at']
        if task['completed_at']:
            result['completed_at'] = task['completed_at']
        if task['result']:
            result['result'] = task['result'][:2000]  # 截断过长结果
        if task['result_url']:
            result['download_url'] = task['result_url']
        if task['error']:
            result['error'] = task['error']
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({'error': str(e)}, ensure_ascii=False)


@tool
def list_tasks(status: str = "all", limit: int = 10) -> str:
    """
    列出任务列表。
    
    参数:
        status: 筛选状态 - "all"(全部), "pending"(待执行), "running"(运行中), "completed"(已完成), "failed"(失败)
        limit: 返回数量限制，默认10
    
    示例:
        list_tasks()  # 列出所有任务
        list_tasks("completed", 5)  # 列出最近5个完成的任务
    """
    try:
        client = _get_client()
        
        query = client.table('agent_tasks').select('*').order('created_at', desc=True)
        
        if status != "all":
            query = query.eq('status', status)
        
        response = query.limit(limit).execute()
        
        tasks = response.data if response.data else []
        
        if not tasks:
            return "没有找到任务"
        
        result = [f"📋 任务列表 (状态: {status}, 共 {len(tasks)} 个):\n"]
        
        for task in tasks:
            status_icon = {
                'pending': '⏳',
                'running': '🔄',
                'completed': '✅',
                'failed': '❌'
            }.get(task['status'], '❓')
            
            result.append(f"\n{status_icon} [{task['id'][:8]}] {task['task_type']}")
            result.append(f"   状态: {task['status']}")
            result.append(f"   创建: {task['created_at']}")
            if task.get('result_url'):
                result.append(f"   结果: {task['result_url']}")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"查询错误: {str(e)}"


@tool
def update_task(
    task_id: str,
    status: Optional[str] = None,
    result: Optional[str] = None,
    result_url: Optional[str] = None,
    error: Optional[str] = None
) -> str:
    """
    更新任务状态和结果。通常由执行器调用，用户一般不需要直接调用。
    
    参数:
        task_id: 任务ID
        status: 新状态 - "pending", "running", "completed", "failed"
        result: 执行结果文本
        result_url: 结果文件的下载链接
        error: 错误信息
    """
    try:
        client = _get_client()
        
        update_data = {}
        
        if status:
            update_data['status'] = status
            if status == 'running':
                update_data['started_at'] = datetime.utcnow().isoformat()
            elif status in ('completed', 'failed'):
                update_data['completed_at'] = datetime.utcnow().isoformat()
        
        if result is not None:
            update_data['result'] = result[:10000]  # 限制大小
        if result_url is not None:
            update_data['result_url'] = result_url
        if error is not None:
            update_data['error'] = error[:2000]
        
        response = client.table('agent_tasks').update(update_data).eq('id', task_id).execute()
        
        return json.dumps({
            'success': True,
            'task_id': task_id,
            'updated': list(update_data.keys())
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False)


@tool
def delete_task(task_id: str) -> str:
    """
    删除任务记录。
    
    参数:
        task_id: 任务ID
    """
    try:
        client = _get_client()
        
        response = client.table('agent_tasks').delete().eq('id', task_id).execute()
        
        return json.dumps({
            'success': True,
            'message': f'任务 {task_id} 已删除'
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False)


# 导出所有工具
TASK_TOOLS = [
    create_task,
    get_task_status,
    list_tasks,
    update_task,
    delete_task,
]
