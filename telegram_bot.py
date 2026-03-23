"""
平静AI助手 - Telegram Bot
直接连接Agent，无需额外配置
"""
import os
import sys
import asyncio
import json
import logging
from typing import Optional

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_core.messages import HumanMessage, AIMessage

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram Bot Token（从环境变量或直接设置）
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8769055112:AAGcvuRfmZqUV4eerSBcgTB96dsKtxjoe10")

# 用户会话存储（简单的内存存储）
user_sessions: dict = {}

# Agent实例缓存
_agent = None


def get_agent():
    """获取Agent实例"""
    global _agent
    if _agent is None:
        from agents.agent import build_agent
        _agent = build_agent()
    return _agent


async def chat_with_agent(user_id: int, message: str) -> str:
    """与Agent对话"""
    try:
        agent = get_agent()
        
        # 获取用户会话历史
        session_key = f"telegram_{user_id}"
        if session_key not in user_sessions:
            user_sessions[session_key] = []
        
        # 构建消息
        messages = []
        for msg in user_sessions[session_key][-10:]:  # 保留最近5轮对话
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=message))
        
        # 调用Agent
        config = {"configurable": {"thread_id": session_key}}
        result = agent.invoke({"messages": messages}, config)
        
        # 提取回复
        if result and "messages" in result:
            last_msg = result["messages"][-1]
            response = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
        else:
            response = "抱歉，我暂时无法回应，请稍后再试。"
        
        # 处理响应内容
        if isinstance(response, list):
            text_parts = []
            for item in response:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif isinstance(item, str):
                    text_parts.append(item)
            response = " ".join(text_parts)
        
        # 保存对话历史
        user_sessions[session_key].append({"role": "user", "content": message})
        user_sessions[session_key].append({"role": "assistant", "content": response})
        
        return response
        
    except Exception as e:
        logger.error(f"Agent error: {e}")
        return f"抱歉，出现错误：{str(e)}"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    welcome_message = """
🌊 *欢迎来到平静AI助手！*

我是你的智能对话伙伴，可以帮你：
• 💬 回答问题和提供建议
• 📝 写作和内容创作
• 🔤 翻译和润色文字
• 💻 编程和代码问题

直接发送消息开始对话吧！

命令列表：
/start - 显示帮助
/clear - 清空对话历史
/help - 显示帮助信息
"""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    await start_command(update, context)


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /clear 命令"""
    user_id = update.effective_user.id
    session_key = f"telegram_{user_id}"
    
    if session_key in user_sessions:
        user_sessions[session_key] = []
    
    await update.message.reply_text("✅ 对话历史已清空，开始新的对话吧！")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理用户消息"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "用户"
    message = update.message.text
    
    logger.info(f"收到消息 - 用户: {user_name}({user_id}), 内容: {message}")
    
    # 显示"正在输入"状态
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # 调用Agent获取回复
    response = await chat_with_agent(user_id, message)
    
    # 发送回复（Telegram消息长度限制为4096字符）
    if len(response) > 4000:
        # 分段发送
        for i in range(0, len(response), 4000):
            await update.message.reply_text(response[i:i+4000])
    else:
        await update.message.reply_text(response)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """错误处理"""
    logger.error(f"Error: {context.error}")
    
    if update and update.message:
        await update.message.reply_text("抱歉，出现了一些问题，请稍后再试。")


def main():
    """启动Bot"""
    logger.info("🚀 启动平静AI助手 Telegram Bot...")
    
    # 创建应用
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # 添加处理器
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # 添加错误处理器
    application.add_error_handler(error_handler)
    
    # 启动Bot
    logger.info("✅ Bot已启动，发送消息到 @calm_agent_bot 开始对话")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
