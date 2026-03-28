# 平静AI - API调用文档

## 基本信息

| 项目 | 值 |
|------|-----|
| **API地址** | `https://66mwfm39tp.coze.site/stream_run` |
| **请求方式** | POST (SSE流式) |
| **项目ID** | `7619192361578463238` |

---

## 认证方式

**Header中添加：**
```
Authorization: Bearer <YOUR_API_TOKEN>
Content-Type: application/json
```

**获取Token：**
1. 打开Coze平台部署页面
2. 点击右上角 "API Token" 按钮
3. 点击 "创建API Token"
4. 复制保存Token（只显示一次）

---

## 请求格式

### 完整请求示例

```bash
curl -X POST "https://66mwfm39tp.coze.site/stream_run" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": {
        "query": {
            "prompt": [
                {
                    "type": "text",
                    "content": {
                        "text": "你好，请介绍一下你自己"
                    }
                }
            ]
        }
    },
    "type": "query",
    "session_id": "your_session_id",
    "project_id": "7619192361578463238"
  }'
```

### Python示例

```python
import httpx

url = "https://66mwfm39tp.coze.site/stream_run"
headers = {
    "Authorization": "Bearer <YOUR_TOKEN>",
    "Content-Type": "application/json"
}
payload = {
    "content": {
        "query": {
            "prompt": [
                {
                    "type": "text",
                    "content": {
                        "text": "你好"
                    }
                }
            ]
        }
    },
    "type": "query",
    "session_id": "test_session",
    "project_id": "7619192361578463238"
}

# 流式请求
with httpx.stream("POST", url, headers=headers, json=payload) as response:
    for line in response.iter_lines():
        if line.startswith("data: "):
            print(line[6:])
```

### JavaScript/Node.js示例

```javascript
const response = await fetch("https://66mwfm39tp.coze.site/stream_run", {
    method: "POST",
    headers: {
        "Authorization": "Bearer <YOUR_TOKEN>",
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        content: {
            query: {
                prompt: [{
                    type: "text",
                    content: { text: "你好" }
                }]
            }
        },
        type: "query",
        session_id: "test_session",
        project_id: "7619192361578463238"
    })
});

// 读取SSE流
const reader = response.body.getReader();
while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    console.log(new TextDecoder().decode(value));
}
```

---

## 参数说明

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | 是 | 固定值 `query` |
| `session_id` | string | 是 | 会话ID，用于保持对话上下文 |
| `project_id` | string | 是 | 项目ID：`7619192361578463238` |
| `content.query.prompt` | array | 是 | 消息内容数组 |
| `content.query.prompt[].type` | string | 是 | 固定值 `text` |
| `content.query.prompt[].content.text` | string | 是 | 用户消息文本 |

---

## 响应格式

### SSE流式响应

```
event: message
data: {"type": "message_start", "session_id": "...", "msg_id": "...", ...}

event: message
data: {"type": "answer", "content": {"answer": "你"}, ...}

event: message
data: {"type": "answer", "content": {"answer": "好"}, ...}

event: message
data: {"type": "message_end", ...}
```

### 响应字段说明

| 字段 | 说明 |
|------|------|
| `type` | 消息类型：`message_start`/`answer`/`tool_request`/`message_end` |
| `content.answer` | AI回复文本（逐字返回） |
| `content.tool_request` | 工具调用请求 |
| `finish` | 是否完成 |

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 401 | Token无效或过期 |
| 400 | 请求参数错误 |
| 500 | 服务器内部错误 |

---

## 功能说明

### 当前模型
- **doubao-seed-1.8** (Agent专家模式)

### 可用工具（11个）
1. **图片生成** - `generate_image`
2. **代码执行** - `execute_python`, `execute_shell`
3. **网络搜索** - `web_search`
4. **图片分析** - `analyze_image`
5. **文件操作** - `read_file`, `write_file`, `list_files`

### 使用示例

**画图：**
```
画一只可爱的猫咪
```

**搜索：**
```
搜索今天北京的天气
```

**代码：**
```
用Python计算斐波那契数列前10项
```

---

## 注意事项

1. **Token安全**：请妥善保管Token，不要在公开代码中暴露
2. **Session管理**：同一session_id会保持对话上下文
3. **超时处理**：建议设置120秒超时（工具调用可能较慢）
4. **流式处理**：响应是SSE格式，需要逐行解析

---

## 联系支持

如有问题，请在GitHub仓库提交Issue。
