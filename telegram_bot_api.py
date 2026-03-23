"""
平静AI助手 - Telegram Bot (API版)
通过Coze平台API调用Agent
"""
import os
import logging
import requests
import json

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== 配置 ====================
# Telegram Bot Token
TELEGRAM_BOT_TOKEN = "8769055112:AAGcvuRfmZqUV4eerSBcgTB96dsKtxjoe10"

# Agent API地址（从Coze部署获取）
# 这是你的Agent API地址
AGENT_API_BASE = "https://43a018a1-99fd-49f3-a313-a20151d429a3.dev.coze.site"

# API端点
STREAM_RUN_URL = f"{AGENT_API_BASE}/stream_run"
RUN_URL = f"{AGENT_API_BASE}/run"


def call_agent(user_id: int, message: str) -> str:
    """调用Agent API"""
    
    session_id = f"telegram_{user_id}"
    
    # 构建请求（Agent格式）
    payload = {
        "type": "query",
        "session_id": session_id,
        "message": message
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        logger.info(f"调用API: {RUN_URL}")
        response = requests.post(
            RUN_URL,
            json=payload,
            headers=headers,
            timeout=120
        )
        
        if response.status_code != 200:
            logger.error(f"API错误: {response.status_code} - {response.text}")
            return f"❌ API错误: {response.status_code}"
        
        # 解析响应
        data = response.json()
        
        # 提取回复内容
        if "messages" in data:
            # 获取最后一条消息
            messages = data["messages"]
            if messages:
                last_msg = messages[-1]
                content = last_msg.get("content", "")
                
                # 处理内容可能是列表的情况
                if isinstance(content, list):
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                        elif isinstance(item, str):
                            text_parts.append(item)
                    return " ".join(text_parts)
                
                return str(content)
        
        # 其他格式
        return str(data)
        
    except requests.exceptions.Timeout:
        return "⏱️ 请求超时，请稍后再试"
    except Exception as e:
        logger.error(f"API调用错误: {e}")
        return f"❌ 错误: {str(e)}"


# ==================== 命令处理 ====================

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始命令"""
    welcome = """
🌊 *平静AI助手*

我是你的智能对话伙伴！

• 💬 回答问题
• 📝 内容创作  
• 🔤 翻译润色
• 💻 代码帮助

直接发消息开始对话！

`/start` - 帮助
`/clear` - 清空对话
"""
    await update.message.reply_text(welcome, parse_mode='Markdown')


async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """清空对话"""
    await update.message.reply_text("✅ 对话已清空（新会话）")


async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理消息"""
    user_id = update.effective_user.id
    message = update.message.text
    
    logger.info(f"消息: {user_id} - {message}")
    
    # 显示输入中
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    # 调用Agent
    reply = call_agent(user_id, message)
    
    # 发送回复
    if len(reply) > 4000:
        for i in range(0, len(reply), 4000):
            await update.message.reply_text(reply[i:i+4000])
    else:
        await update.message.reply_text(reply)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """错误处理"""
    logger.error(f"Error: {context.error}")


def main():
    """启动Bot"""
    logger.info("🚀 启动平静 Telegram Bot...")
    
    # 创建应用
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # 添加处理器
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("clear", clear_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    app.add_error_handler(error_handler)
    
    logger.info("✅ Bot启动成功！发送消息到 @calm_agent_bot")
    
    # 运行
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
