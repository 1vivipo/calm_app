#!/bin/bash
# 平静AI Agent - Streamlit Cloud 部署脚本

echo "🌊 准备部署到 Streamlit Cloud..."

# 创建 Streamlit 配置文件
mkdir -p .streamlit

cat > .streamlit/config.toml << 'EOF'
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#4A90E2"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
EOF

cat > .streamlit/credentials.toml << 'EOF'
[general]
email = ""
EOF

echo "✅ Streamlit Cloud 配置完成"
echo ""
echo "部署步骤:"
echo "1. 访问 https://share.streamlit.io"
echo "2. 使用 GitHub 账号登录"
echo "3. 点击 'New app'"
echo "4. 选择仓库: r1se23/ai-agent"
echo "5. 设置主文件路径: frontend/app.py"
echo "6. 点击 'Deploy'"
echo ""
echo "或者直接访问已部署的地址:"
echo "http://115.190.93.94:8501"
