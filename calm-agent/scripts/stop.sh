#!/bin/bash
# 平静AI Agent - 停止脚本

echo "🛑 停止平静AI Agent..."

# 查找并停止进程
pkill -f "streamlit run.*app.py"
pkill -f "python run.py"

echo "✅ 平静AI Agent已停止"
