# 国际版Coze配置Telegram Bot指南

## 第一步：打开国际版Coze
访问 https://coze.com 并登录（用Google/Apple账号）

## 第二步：创建Bot
1. 点击「Create Bot」
2. 名称填：`平静AI`
3. 描述随便写

## 第三步：配置工作流
在Bot设置里添加一个 **Workflow**，或者直接在Prompt里配置：

### 配置HTTP插件（如果有的话）
- URL: `https://43a018a1-99fd-49f3-a313-a20151d429a3.dev.coze.site/run`
- Method: `POST`
- Headers: `Content-Type: application/json`
- Body:
```json
{
  "type": "query",
  "session_id": "{{sender_id}}",
  "message": "{{message}}"
}
```

### 或者用简单方式
直接在Bot的Prompt里写：
```
你是一个消息转发助手。
用户发送消息后，你需要调用HTTP API来获取回复：
- URL: https://43a018a1-99fd-49f3-a313-a20151d429a3.dev.coze.site/run
- 请求方式: POST
- 请求体: {"type":"query","session_id":"用户ID","message":"用户消息"}
- 返回的messages数组中最后一条的content就是回复
```

## 第四步：发布到Telegram
1. 点击「Publish」
2. 选择「Telegram」
3. 填入你的Bot Token: `8769055112:AAGcvuRfmZqUV4eerSBcgTB96dsKtxjoe10`
4. 点击确认

## 完成！
现在去Telegram给你的Bot发消息，它就会调用你的Agent回复了！

---

## 重要提示
- 国际版Coze可以访问Telegram API
- 你的Agent API是国内版，但国际版可以调用它
- 这样就不需要任何服务器了！
