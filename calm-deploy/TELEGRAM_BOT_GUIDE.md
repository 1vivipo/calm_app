# 🌊 平静AI助手 - Telegram Bot 部署指南

## 一、快速开始（在你自己的电脑运行）

### 1. 安装依赖
```bash
pip install python-telegram-bot langchain langchain-openai langgraph
```

### 2. 运行Bot
```bash
python telegram_bot.py
```

### 3. 使用Bot
在Telegram搜索 `@calm_agent_bot`，发送消息开始对话！

---

## 二、命令列表

| 命令 | 说明 |
|------|------|
| `/start` | 显示欢迎信息 |
| `/help` | 显示帮助 |
| `/clear` | 清空对话历史 |

---

## 三、如果需要代理

在中国大陆可能需要代理才能连接Telegram：

### 方法1：设置环境变量
```bash
export https_proxy=http://127.0.0.1:7890
python telegram_bot.py
```

### 方法2：修改代码添加代理
在 `telegram_bot.py` 中找到 `Application.builder()` 部分：

```python
from telegram.request import HTTPXRequest

# 创建代理请求
proxy_request = HTTPXRequest(
    proxy="http://127.0.0.1:7890"  # 你的代理地址
)

application = Application.builder() \
    .token(TELEGRAM_BOT_TOKEN) \
    .request(proxy_request) \
    .build()
```

---

## 四、部署到服务器（24小时运行）

### 方法1：使用 nohup
```bash
nohup python telegram_bot.py > bot.log 2>&1 &
```

### 方法2：使用 systemd（推荐）
创建服务文件 `/etc/systemd/system/calm-bot.service`：

```ini
[Unit]
Description=Calm AI Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/bot
ExecStart=/usr/bin/python3 telegram_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl start calm-bot
sudo systemctl enable calm-bot  # 开机自启
```

---

## 五、文件说明

| 文件 | 说明 |
|------|------|
| `telegram_bot.py` | Telegram Bot主程序 |
| `app.py` | Streamlit网页版 |
| `requirements.txt` | 依赖列表 |

---

**你的Bot信息：**
- Bot名称：agent_calm pro
- 用户名：@calm_agent_bot
- 链接：https://t.me/calm_agent_bot
