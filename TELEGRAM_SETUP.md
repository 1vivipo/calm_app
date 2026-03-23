# Telegram Bot 设置指南

## 第一步：设置 Webhook

在浏览器中打开这个链接（或用curl执行）：

```
https://api.telegram.org/bot8769055112:AAGcvuRfmZqUV4eerSBcgTB96dsKtxjoe10/setWebhook?url=https://43a018a1-99fd-49f3-a313-a20151d429a3.dev.coze.site/telegram/webhook
```

或者在终端执行：
```bash
curl "https://api.telegram.org/bot8769055112:AAGcvuRfmZqUV4eerSBcgTB96dsKtxjoe10/setWebhook?url=https://43a018a1-99fd-49f3-a313-a20151d429a3.dev.coze.site/telegram/webhook"
```

成功的话会返回：`{"ok":true,"result":true,"description":"Webhook was set"}`

## 第二步：验证 Webhook

```bash
curl "https://api.telegram.org/bot8769055112:AAGcvuRfmZqUV4eerSBcgTB96dsKtxjoe10/getWebhookInfo"
```

## 第三步：测试 Bot

在 Telegram 中搜索你的 Bot，发送 `/start` 开始对话！

---

## Bot 信息
- Token: `8769055112:AAGcvuRfmZqUV4eerSBcgTB96dsKtxjoe10`
- Webhook URL: `https://43a018a1-99fd-49f3-a313-a20151d429a3.dev.coze.site/telegram/webhook`
