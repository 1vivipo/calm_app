// Cloudflare Worker 代码 - 用于转发 Telegram 消息
// 部署到 Cloudflare Workers（免费）

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // 处理 Telegram Webhook
    if (request.method === 'POST' && url.pathname === '/telegram/webhook') {
      const update = await request.json();
      
      // 转发到你的 Agent API
      const agentResponse = await fetch('https://43a018a1-99fd-49f3-a313-a20151d429a3.dev.coze.site/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'query',
          session_id: `telegram_${update.message?.from?.id || 'unknown'}`,
          message: update.message?.text || ''
        })
      });
      
      const agentData = await agentResponse.json();
      
      // 提取回复
      let replyText = '抱歉，无法处理您的请求';
      if (agentData.messages && agentData.messages.length > 0) {
        const lastMsg = agentData.messages[agentData.messages.length - 1];
        if (typeof lastMsg.content === 'string') {
          replyText = lastMsg.content;
        } else if (Array.isArray(lastMsg.content)) {
          replyText = lastMsg.content
            .filter(item => item.type === 'text')
            .map(item => item.text)
            .join(' ');
        }
      }
      
      // 发送回复到 Telegram
      const telegramResponse = await fetch(
        `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            chat_id: update.message?.chat?.id,
            text: replyText,
            parse_mode: 'HTML'
          })
        }
      );
      
      return new Response('OK');
    }
    
    // 设置 Webhook
    if (url.pathname === '/setup') {
      const workerUrl = url.origin + '/telegram/webhook';
      const response = await fetch(
        `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/setWebhook`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: workerUrl })
        }
      );
      const data = await response.json();
      return new Response(JSON.stringify(data), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return new Response('Telegram Bot Worker is running!');
  }
};
