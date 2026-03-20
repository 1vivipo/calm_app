#!/bin/bash
# 平静AI Agent - 后台持续运行脚本

echo "🌊 启动平静AI Agent (后台模式)..."

# 设置工作目录
WORK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$WORK_DIR"

# 创建日志目录
mkdir -p /app/work/logs/bypass

# 设置环境变量
export PYTHONPATH="${WORK_DIR}:${PYTHONPATH}"

# 停止已有进程
pkill -f "streamlit run.*app.py" 2>/dev/null

# 启动Streamlit服务（后台运行）
nohup streamlit run frontend/app.py \
    --server.address 0.0.0.0 \
    --server.port 8501 \
    --server.headless true \
    --browser.gatherUsageStats false \
    > /app/work/logs/bypass/streamlit.log 2>&1 &

# 记录PID
echo $! > /app/work/logs/bypass/calm_agent.pid

echo "✅ 平静AI Agent已启动!"
echo "📍 访问地址: http://localhost:8501"
echo "📄 日志文件: /app/work/logs/bypass/streamlit.log"
echo "🆔 进程PID: $(cat /app/work/logs/bypass/calm_agent.pid)"
echo ""
echo "查看日志: tail -f /app/work/logs/bypass/streamlit.log"
echo "停止服务: ./scripts/stop.sh"
