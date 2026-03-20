"""
平静AI Agent - Hugging Face Spaces 部署主文件
"""
import os
import sys

# 设置环境
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_SERVER_PORT"] = "7860"
os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入并运行Streamlit应用
from frontend.app_v2 import main
import streamlit.web.cli as stcli

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "frontend/app_v2.py", 
                "--server.headless=true",
                "--server.port=7860",
                "--server.address=0.0.0.0",
                "--browser.gatherUsageStats=false"]
    sys.exit(stcli.main())
