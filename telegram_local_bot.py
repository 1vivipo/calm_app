#!/usr/bin/env python3
"""
Telegram Bot 本地代理
在你的电脑上运行，转发消息到 Agent API

使用方法:
1. 安装依赖: pip install requests
2. 运行: python telegram_local_bot.py
"""

import requests
import time
import json

# 配置
BOT_TOKEN = "8769055112:AAGcvuRfmZqUV4eerSBcgTB96dsKtxjoe10"
AGENT_API = "https://43a018a1-99fd-49f3-a313-a20151d429a3.dev.coze.site/run"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# 记录已处理的消息ID
processed_messages = set()

def get_updates(offset=None):
    """获取新消息"""
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    
    try:
        resp = requests.get(f"{TELEGRAM_API}/getUpdates", params=params, timeout=35)
        return resp.json().get("result", [])
    except Exception as e:
        print(f"❌ 获取消息失败: {e}")
        return []

def send_message(chat_id, text):
    """发送消息"""
    try:
        # 分片发送长消息
        if len(text) > 4000:
            for i in range(0, len(text), 4000):
                requests.post(f"{TELEGRAM_API}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": text[i:i+4000],
                    "parse_mode": "HTML"
                })
        else:
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            })
    except Exception as e:
        print(f"❌ 发送消息失败: {e}")

def call_agent(user_id, message):
    """调用 Agent API"""
    try:
        resp = requests.post(AGENT_API, json={
            "type": "query",
            "session_id": f"telegram_{user_id}",
            "message": message
        }, timeout=120)
        
        data = resp.json()
        
        if "messages" in data and data["messages"]:
            last_msg = data["messages"][-1]
            content = last_msg.get("content", "")
            
            if isinstance(content, list):
                return " ".join(
                    item.get("text", "") 
                    for item in content 
                    if isinstance(item, dict) and item.get("type") == "text"
                )
            return str(content)
        
        return "抱歉，处理失败"
    except Exception as e:
        return f"❌ 错误: {e}"

def main():
    print("🌊 平静AI Bot 本地代理启动中...")
    print("按 Ctrl+C 停止")
    print("-" * 40)
    
    # 删除 Webhook（使用轮询模式）
    requests.get(f"{TELEGRAM_API}/deleteWebhook")
    print("✅ 已切换到轮询模式")
    
    offset = None
    
    while True:
        try:
            updates = get_updates(offset)
            
            for update in updates:
                offset = update["update_id"] + 1
                
                if "message" not in update:
                    continue
                
                message = update["message"]
                chat_id = message["chat"]["id"]
                user_id = message["from"]["id"]
                text = message.get("text", "")
                
                # 跳过已处理的消息
                msg_id = message.get("message_id")
                if msg_id in processed_messages:
                    continue
                processed_messages.add(msg_id)
                
                print(f"📩 [{user_id}] {text}")
                
                if not text:
                    continue
                
                # 处理命令
                if text == "/start":
                    send_message(chat_id, """🌊 <b>平静AI助手</b>

我是你的智能对话伙伴！

• 💬 回答问题
• 📝 内容创作  
• 🔤 翻译润色
• 💻 代码帮助

直接发消息开始对话！""")
                    continue
                
                # 调用 Agent
                print("⏳ 处理中...")
                reply = call_agent(user_id, text)
                
                # 发送回复
                send_message(chat_id, reply)
                print(f"✅ 已回复")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
