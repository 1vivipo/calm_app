"""
平静AI助手 - Telegram Bot服务
部署在Coze平台，24小时运行
"""
import os
import asyncio
import logging
import requests
import json
import signal
import sys

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ==================== 配置 ====================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8769055112:AAGcvuRfmZqUV4eerSBcgTB96dsKtxjoe10")

# Agent API地址
AGENT_API_BASE = os.getenv("COZE_PROJECT_DOMAIN_DEFAULT", "https://43a018a1-99fd-49f3-a313-a20151d429a3.dev.coze.site")
RUN_URL = f"{AGENT_API_BASE}/run"

logger.info(f"Agent API: {RUN_URL}")


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


# ==================== 命令处理 ====================

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = """
🌊 *平静AI助手*

我是你的智能对话伙伴！

• 💬 回答问题
• 📝 内容创作  
• 🔤 翻译润色
• 💻 代码帮助

直接发消息开始对话！
"""
    await update.message.reply_text(welcome, parse_mode='Markdown')


async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text
    
    logger.info(f"📩 消息: {user_id} - {message}")
    
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    reply = call_agent(user_id, message)
    
    if len(reply) > 4000:
        for i in range(0, len(reply), 4000):
            await update.message.reply_text(reply[i:i+4000])
    else:
        await update.message.reply_text(reply)


def run_telegram_bot():
    """运行Telegram Bot"""
    logger.info("🚀 启动Telegram Bot...")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    
    logger.info("✅ Bot已启动！@calm_agent_bot")
    
    # 运行Bot（阻塞）
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    run_telegram_bot()
