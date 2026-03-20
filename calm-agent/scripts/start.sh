#!/bin/bash
# 平静AI Agent - 启动脚本

echo "🌊 启动平静AI Agent..."

# 设置工作目录
cd "$(dirname "$0")/.."

# 创建日志目录
mkdir -p /app/work/logs/bypass

# 检查依赖
echo "📦 检查依赖..."
if ! command -v streamlit &> /dev/null; then
    echo "安装Streamlit..."
    pip install streamlit
fi

# 启动服务
echo "🚀 启动服务..."
nohup python run.py start --host 0.0.0.0 --port 8501 > /app/work/logs/bypass/calm_agent_console.log 2>&1 &

echo "✅ 平静AI Agent已启动!"
echo "📍 访问地址: http://localhost:8501"
echo "📄 日志文件: /app/work/logs/bypass/calm_agent.log"
echo ""
echo "查看日志: tail -f /app/work/logs/bypass/calm_agent.log"
