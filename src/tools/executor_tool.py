"""
执行工具集 - Shell命令、代码执行、文件管理
让Agent具备真实的执行能力
"""
import os
import subprocess
import tempfile
import json
import re
from typing import Optional
from langchain.tools import tool


@tool
def execute_shell(command: str, timeout: int = 60, background: bool = False) -> str:
    """
    执行Shell命令。支持Linux命令、管道、重定向等。
    
    参数:
        command: Shell命令字符串
        timeout: 超时时间(秒)，默认60秒
        background: 是否后台运行，后台运行会立即返回任务ID
    
    示例:
        execute_shell("ls -la")  # 列出文件
        execute_shell("pip install requests")  # 安装包
        execute_shell("python script.py")  # 运行脚本
    """
    try:
        workspace = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        
        if background:
            # 后台运行
            import uuid
            task_id = str(uuid.uuid4())[:8]
            log_file = f"/tmp/task_{task_id}.log"
            
            # 使用nohup后台执行
            full_cmd = f"cd {workspace} && nohup bash -c {repr(command)} > {log_file} 2>&1 &"
            subprocess.run(full_cmd, shell=True, timeout=5)
            
            return json.dumps({
                "status": "started",
                "task_id": task_id,
                "log_file": log_file,
                "message": f"任务已在后台启动，任务ID: {task_id}，使用 get_task_result 查询结果"
            }, ensure_ascii=False)
        
        # 同步执行
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=workspace
        )
        
        output = result.stdout
        if result.stderr and result.returncode != 0:
            output += f"\n[错误] {result.stderr}"
        
        # 截断过长输出
        if len(output) > 8000:
            output = output[:4000] + "\n... (输出过长，已截断) ...\n" + output[-3500:]
        
        return output if output.strip() else "(命令执行成功，无输出)"
        
    except subprocess.TimeoutExpired:
        return f"命令执行超时 ({timeout}秒)，建议使用 background=True 后台运行"
    except Exception as e:
        return f"执行错误: {str(e)}"


@tool
def execute_python(code: str, timeout: int = 60) -> str:
    """
    执行Python代码。支持安装包、文件操作、数据处理等。
    
    参数:
        code: Python代码字符串
        timeout: 超时时间(秒)，默认60秒
    
    示例:
        execute_python("import requests; print(requests.get('https://api.ipify.org').text)")
        execute_python("import pandas as pd; df = pd.DataFrame({'a': [1,2,3]}); print(df)")
    """
    try:
        workspace = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        
        # 创建临时脚本文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=workspace) as f:
            f.write(code)
            script_path = f.name
        
        # 执行
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=workspace,
            env={**os.environ, 'PYTHONPATH': f"{workspace}/src:{os.environ.get('PYTHONPATH', '')}"}
        )
        
        # 清理临时文件
        os.unlink(script_path)
        
        output = result.stdout
        if result.stderr:
            if result.returncode != 0:
                output += f"\n[错误] {result.stderr}"
            elif result.stderr.strip():
                output += f"\n[警告] {result.stderr}"
        
        return output if output.strip() else "(代码执行成功，无输出)"
        
    except subprocess.TimeoutExpired:
        return f"代码执行超时 ({timeout}秒)"
    except Exception as e:
        return f"执行错误: {str(e)}"


@tool
def read_file_content(file_path: str, start_line: int = 1, end_line: int = 200) -> str:
    """
    读取文件内容。支持代码、文本、JSON等文件。
    
    参数:
        file_path: 文件路径（相对于项目根目录或绝对路径）
        start_line: 起始行号，默认1
        end_line: 结束行号，默认200
    
    示例:
        read_file_content("src/main.py")  # 读取文件
        read_file_content("config.json", 1, 50)  # 读取前50行
    """
    try:
        workspace = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        
        # 处理相对路径
        if not os.path.isabs(file_path):
            file_path = os.path.join(workspace, file_path)
        
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 行号转换
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        
        selected_lines = lines[start_idx:end_idx]
        
        result = []
        for i, line in enumerate(selected_lines, start=start_line):
            # 截断过长行
            if len(line) > 500:
                line = line[:500] + "...\n"
            result.append(f"{i:4d} | {line}")
        
        content = "".join(result)
        
        if end_idx < len(lines):
            content += f"\n... (共 {len(lines)} 行，已显示 {start_line}-{end_line} 行)"
        
        return content if content.strip() else "(文件为空)"
        
    except Exception as e:
        return f"读取错误: {str(e)}"


@tool
def write_file_content(file_path: str, content: str, mode: str = "overwrite") -> str:
    """
    写入文件内容。支持创建新文件、覆盖、追加。
    
    参数:
        file_path: 文件路径（相对于项目根目录或绝对路径）
        content: 要写入的内容
        mode: 写入模式 - "overwrite"(覆盖), "append"(追加)
    
    示例:
        write_file_content("test.py", "print('hello')")  # 创建/覆盖文件
        write_file_content("log.txt", "新日志行\\n", "append")  # 追加内容
    """
    try:
        workspace = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        
        # 处理相对路径
        if not os.path.isabs(file_path):
            file_path = os.path.join(workspace, file_path)
        
        # 创建目录
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 写入
        write_mode = 'a' if mode == "append" else 'w'
        with open(file_path, write_mode, encoding='utf-8') as f:
            f.write(content)
        
        action = "追加到" if mode == "append" else "写入"
        return f"✅ 已{action}文件: {file_path} ({len(content)} 字符)"
        
    except Exception as e:
        return f"写入错误: {str(e)}"


@tool
def list_files(directory: str = ".", pattern: str = "*") -> str:
    """
    列出目录下的文件。支持通配符模式匹配。
    
    参数:
        directory: 目录路径，默认为项目根目录
        pattern: 文件匹配模式，如 "*.py", "*.json"
    
    示例:
        list_files()  # 列出根目录所有文件
        list_files("src", "*.py")  # 列出src目录下的Python文件
    """
    import glob
    
    try:
        workspace = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        
        # 处理路径
        if directory == ".":
            directory = workspace
        elif not os.path.isabs(directory):
            directory = os.path.join(workspace, directory)
        
        # 搜索文件
        search_pattern = os.path.join(directory, "**", pattern) if pattern != "*" else os.path.join(directory, "**", "*")
        files = glob.glob(search_pattern, recursive=True)
        
        # 过滤目录
        files = [f for f in files if os.path.isfile(f)]
        
        # 转为相对路径
        rel_files = [os.path.relpath(f, workspace) for f in files]
        
        # 分组显示
        result = [f"📁 {directory} (匹配: {pattern})\n"]
        
        # 按类型分组
        by_ext = {}
        for f in rel_files[:100]:  # 限制100个
            ext = os.path.splitext(f)[1] or "其他"
            if ext not in by_ext:
                by_ext[ext] = []
            by_ext[ext].append(f)
        
        for ext, file_list in sorted(by_ext.items()):
            result.append(f"\n  {ext or '无后缀'} ({len(file_list)} 个):")
            for f in file_list[:10]:
                result.append(f"    - {f}")
            if len(file_list) > 10:
                result.append(f"    ... 还有 {len(file_list) - 10} 个")
        
        result.append(f"\n共找到 {len(rel_files)} 个文件")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"列出文件错误: {str(e)}"


@tool
def search_in_files(query: str, file_pattern: str = "*.py") -> str:
    """
    在文件中搜索文本内容。支持正则表达式。
    
    参数:
        query: 搜索内容或正则表达式
        file_pattern: 文件匹配模式，默认搜索Python文件
    
    示例:
        search_in_files("def hello")  # 搜索函数定义
        search_in_files("import", "*.py")  # 搜索导入语句
    """
    try:
        workspace = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        
        matches = []
        
        for root, dirs, files in os.walk(workspace):
            # 跳过隐藏目录和虚拟环境
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__' and d != 'node_modules']
            
            for file in files:
                if file_pattern == "*" or file.endswith(file_pattern.replace("*", "")):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for i, line in enumerate(f, 1):
                                if query in line:
                                    rel_path = os.path.relpath(file_path, workspace)
                                    matches.append(f"{rel_path}:{i}: {line.strip()[:100]}")
                                    if len(matches) >= 50:
                                        break
                    except:
                        pass
                if len(matches) >= 50:
                    break
            if len(matches) >= 50:
                break
        
        if matches:
            return f"找到 {len(matches)} 处匹配:\n" + "\n".join(matches[:30]) + ("\n..." if len(matches) > 30 else "")
        return f"未找到匹配 '{query}' 的内容"
        
    except Exception as e:
        return f"搜索错误: {str(e)}"


@tool
def install_package(package: str) -> str:
    """
    安装Python包。
    
    参数:
        package: 包名，可指定版本如 "requests==2.28.0"
    
    示例:
        install_package("pandas")
        install_package("requests==2.28.0")
    """
    try:
        result = subprocess.run(
            ['pip', 'install', package],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            return f"✅ 安装成功: {package}\n{result.stdout[-500:]}"
        else:
            return f"❌ 安装失败: {result.stderr[-500:]}"
            
    except Exception as e:
        return f"安装错误: {str(e)}"


@tool
def get_task_result(task_id: str) -> str:
    """
    获取后台任务的执行结果。
    
    参数:
        task_id: 任务ID（执行后台命令时返回的ID）
    
    示例:
        get_task_result("abc12345")
    """
    try:
        log_file = f"/tmp/task_{task_id}.log"
        
        if not os.path.exists(log_file):
            return f"任务 {task_id} 不存在或已过期"
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        # 检查是否还在运行
        check = subprocess.run(
            f"ps aux | grep 'task_{task_id}' | grep -v grep",
            shell=True,
            capture_output=True
        )
        
        if check.stdout:
            status = "⏳ 运行中..."
        else:
            status = "✅ 已完成"
        
        return f"状态: {status}\n\n日志:\n{content[-5000:]}"
        
    except Exception as e:
        return f"查询错误: {str(e)}"


# 导出所有工具
EXECUTOR_TOOLS = [
    execute_shell,
    execute_python,
    read_file_content,
    write_file_content,
    list_files,
    search_in_files,
    install_package,
    get_task_result,
]
