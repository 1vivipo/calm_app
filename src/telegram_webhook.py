"""
平静AI助手 - Telegram Webhook服务
Telegram主动推送消息到API，无需持续轮询
"""
import os
import logging
import requests
import json
import asyncio

from fastapi import Request, Response
from telegram import Update, Bot
from telegram.ext import Application

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 配置 ====================
TELEGRAM_BOT_TOKEN = "8769055112:AAGcvuRfmZqUV4eerSBcgTB96dsKtxjoe10"
AGENT_API_BASE = os.getenv("COZE_PROJECT_DOMAIN_DEFAULT", "https://43a018a1-99fd-49f3-a313-a20151d429a3.dev.coze.site")
RUN_URL = f"{AGENT_API_BASE}/run"

# Bot实例
bot = Bot(token=TELEGRAM_BOT_TOKEN)


def call_agent(user_id: int, message: str) -> str:
    """调用Agent API"""
    session_id = f"telegram_{user_id}"
    
    payload = {
        "type": "query",
        "session_id": session_id,
        "message": message
    }
    
    try:
        response = requests.post(RUN_URL, json=payload, timeout=120)
        
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
        logger.error(f"API错误: {e}")
        return f"❌ 错误: {str(e)}"


async def handle_update(update: dict):
    """处理Telegram更新"""
    try:
        # 解析更新
        if "message" not in update:
            return
        
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user_id = message["from"]["id"]
        
        # 忽略空消息或命令以外的内容
        if not text:
            return
        
        logger.info(f"📩 Telegram消息: {user_id} - {text}")
        
        # 处理命令
        if text == "/start":
            welcome = """🌊 平静AI助手

我是你的智能对话伙伴！

• 💬 回答问题
• 📝 内容创作  
• 🔤 翻译润色
• 💻 代码帮助

直接发消息开始对话！"""
            await bot.send_message(chat_id=chat_id, text=welcome)
            return
        
        # 调用Agent
        reply = call_agent(user_id, text)
        
        # 发送回复
        if len(reply) > 4000:
            for i in range(0, len(reply), 4000):
                await bot.send_message(chat_id=chat_id, text=reply[i:i+4000])
        else:
            await bot.send_message(chat_id=chat_id, text=reply)
        
        logger.info(f"✅ 回复已发送")
        
    except Exception as e:
        logger.error(f"处理更新错误: {e}")


async def telegram_webhook(request: Request):
    """Telegram Webhook端点"""
    try:
        update_data = await request.json()
        logger.info(f"收到Webhook: {update_data}")
        
        # 异步处理
        asyncio.create_task(handle_update(update_data))
        
        return Response(content="OK", status_code=200)
        
    except Exception as e:
        logger.error(f"Webhook错误: {e}")
        return Response(content="Error", status_code=500)


async def setup_webhook(webhook_url: str):
    """设置Webhook"""
    try:
        result = await bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook设置: {result} - {webhook_url}")
        return result
    except Exception as e:
        logger.error(f"设置Webhook失败: {e}")
        return False


def get_webhook_info():
    """获取Webhook信息"""
    import asyncio
    return asyncio.run(bot.get_webhook_info())
