"""
平静AI助手 - Telegram Webhook服务
直接使用HTTP调用Telegram API，无需额外依赖
"""
import os
import logging
import requests
import json
import asyncio

from fastapi import Request, Response

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 配置 ====================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8769055112:AAGcvuRfmZqUV4eerSBcgTB96dsKtxjoe10")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
AGENT_API_BASE = os.getenv("COZE_PROJECT_DOMAIN_DEFAULT", "")


def call_telegram_api(method: str, data: dict = None) -> dict:
    """调用Telegram API"""
    url = f"{TELEGRAM_API}/{method}"
    try:
        if data:
            resp = requests.post(url, json=data, timeout=10)
        else:
            resp = requests.get(url, timeout=10)
        return resp.json()
    except Exception as e:
        logger.error(f"Telegram API错误: {e}")
        return {"ok": False, "error": str(e)}


def send_message(chat_id: int, text: str) -> bool:
    """发送消息到Telegram"""
    result = call_telegram_api("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    })
    return result.get("ok", False)


def call_agent(user_id: int, message: str) -> str:
    """调用Agent API"""
    if not AGENT_API_BASE:
        return "❌ Agent API未配置"
    
    session_id = f"telegram_{user_id}"
    run_url = f"{AGENT_API_BASE}/run"
    
    payload = {
        "type": "query",
        "session_id": session_id,
        "message": message
    }
    
    try:
        response = requests.post(run_url, json=payload, timeout=120)
        
        if response.status_code != 200:
            return f"❌ API错误: {response.status_code}"
        
        data = response.json()
        
        if "messages" in data and data["messages"]:
            last_msg = data["messages"][-1]
            content = last_msg.get("content", "")
            
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                    elif isinstance(item, str):
                        text_parts.append(item)
                return " ".join(text_parts)
            
            return str(content)
        
        return str(data)
        
    except Exception as e:
        logger.error(f"Agent API错误: {e}")
        return f"❌ 错误: {str(e)}"


async def handle_update(update: dict):
    """处理Telegram更新"""
    try:
        if "message" not in update:
            return
        
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user_id = message["from"]["id"]
        
        if not text:
            return
        
        logger.info(f"📩 Telegram消息: {user_id} - {text}")
        
        # 处理命令
        if text == "/start":
            welcome = """🌊 <b>平静AI助手</b>

我是你的智能对话伙伴！

• 💬 回答问题
• 📝 内容创作  
• 🔤 翻译润色
• 💻 代码帮助

直接发消息开始对话！"""
            send_message(chat_id, welcome)
            return
        
        # 调用Agent
        reply = call_agent(user_id, text)
        
        # 发送回复（分片处理长消息）
        if len(reply) > 4000:
            for i in range(0, len(reply), 4000):
                send_message(chat_id, reply[i:i+4000])
        else:
            send_message(chat_id, reply)
        
        logger.info(f"✅ 回复已发送到 {chat_id}")
        
    except Exception as e:
        logger.error(f"处理更新错误: {e}")


async def telegram_webhook(request: Request):
    """Telegram Webhook端点"""
    try:
        update_data = await request.json()
        logger.info(f"收到Webhook: {update_data}")
        
        # 异步处理（立即返回200给Telegram）
        import threading
        thread = threading.Thread(target=lambda: asyncio.run(handle_update(update_data)))
        thread.start()
        
        return Response(content="OK", status_code=200)
        
    except Exception as e:
        logger.error(f"Webhook错误: {e}")
        return Response(content="Error", status_code=500)


def setup_webhook_sync(webhook_url: str) -> bool:
    """设置Webhook（同步版本）"""
    result = call_telegram_api("setWebhook", {"url": webhook_url})
    if result.get("ok"):
        logger.info(f"✅ Webhook设置成功: {webhook_url}")
        return True
    else:
        logger.error(f"❌ Webhook设置失败: {result}")
        return False


async def setup_webhook(webhook_url: str):
    """设置Webhook"""
    return setup_webhook_sync(webhook_url)


def get_webhook_info() -> dict:
    """获取Webhook信息"""
    return call_telegram_api("getWebhookInfo")


# 模块级初始化检查
def check_telegram_config():
    """检查Telegram配置"""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("⚠️ TELEGRAM_BOT_TOKEN 未配置")
        return False
    return True


TELEGRAM_ENABLED = check_telegram_config()
