# 🌊 平静 AI Agent

> 一个具备多模态能力的高级AI助手，永久免费，功能强大

## ✨ 核心特性

- 🤖 **智能对话**：自然流畅的多轮对话，理解上下文
- 🔍 **网页搜索**：实时获取最新信息，AI智能摘要
- 🎨 **图像生成**：文本转图像，支持2K/4K高清
- 🎬 **视频生成**：文本转视频，创作动态内容
- 🔊 **语音合成**：文本转语音，多种声音可选
- 📄 **文档生成**：PDF/Word/Excel一键生成
- 🖼️ **图像理解**：识别分析图片内容
- 🤔 **深度思考**：复杂推理，逻辑分析

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip 或 uv 包管理器

### 安装依赖

```bash
# 使用pip
pip install -r requirements.txt

# 或使用uv
uv pip install -r requirements.txt
```

### 启动服务

```bash
# 方式1: 使用Python脚本
python run.py start

# 方式2: 使用启动脚本
bash scripts/start.sh

# 方式3: 后台运行
bash scripts/start_background.sh
```

访问地址: http://localhost:8501

### 停止服务

```bash
bash scripts/stop.sh
```

## 📖 使用指南

### 对话功能

直接输入消息即可与AI对话：

```
你好，请介绍一下自己
```

### 网页搜索

在消息中包含"搜索"、"查询"等关键词：

```
搜索最新的AI技术发展
查询今天北京的天气
```

### 图像生成

在消息中包含"生成图片"、"画一张"等关键词：

```
生成一张美丽的山水风景图
画一张科技感的未来城市
```

### 视频生成

在消息中包含"生成视频"、"制作视频"等关键词：

```
生成一段夕阳下的海滩视频
制作一个产品展示视频
```

### 文档生成

在消息中包含"生成文档"、"生成PDF"等关键词：

```
生成一份AI发展报告PDF文档
生成一个项目计划Word文档
```

### 图像理解

发送图片URL，AI会自动识别并分析：

```
这张图片里有什么？https://example.com/image.jpg
```

### 深度思考模式

在侧边栏勾选"启用深度思考模式"，适用于复杂推理、数学计算等场景。

## 🛠️ 技术架构

```
calm-agent/
├── backend/          # 后端核心
│   ├── core.py       # Agent引擎
│   ├── tools.py      # 工具模块
│   ├── models.py     # 数据模型
│   └── session.py    # 会话管理
├── frontend/         # 前端界面
│   └── app.py        # Streamlit应用
├── config/           # 配置文件
│   ├── config.py     # 系统配置
│   └── prompts.py    # 提示词配置
├── scripts/          # 脚本工具
│   ├── start.sh      # 启动脚本
│   ├── stop.sh       # 停止脚本
│   └── start_background.sh  # 后台启动
├── requirements.txt  # 依赖列表
├── run.py           # 主运行文件
└── README.md        # 文档
```

## 🎯 能力对比

| 能力 | 平静AI | 传统AI助手 |
|------|--------|-----------|
| 多轮对话 | ✅ | ✅ |
| 实时搜索 | ✅ | ❌ |
| 图像生成 | ✅ | ❌ |
| 视频生成 | ✅ | ❌ |
| 语音合成 | ✅ | ❌ |
| 文档生成 | ✅ | ❌ |
| 图像理解 | ✅ | 部分 |
| 深度思考 | ✅ | 部分 |
| 永久免费 | ✅ | ❌ |

## ⚙️ 配置说明

### 模型配置

在 `config/config.py` 中修改模型配置：

```python
DEFAULT_MODEL = "doubao-seed-1-8-251228"  # 默认模型
VISION_MODEL = "doubao-seed-1-6-vision-250815"  # 视觉模型
THINKING_MODEL = "doubao-seed-2-0-pro-260215"  # 思考模型
```

### 会话配置

```python
MAX_HISTORY = 50  # 最多保留50轮对话
SESSION_TIMEOUT = 3600  # 会话超时时间（秒）
```

## 📊 API接口

### 聊天接口

```bash
POST /chat
Content-Type: application/json

{
  "message": "你好",
  "session_id": "optional-session-id",
  "enable_thinking": false
}
```

响应：

```json
{
  "response": "你好！我是平静，你的AI助手...",
  "session_id": "session-uuid",
  "tool_used": null,
  "tool_result": null,
  "success": true
}
```

## 🔧 开发指南

### 添加新工具

1. 在 `backend/tools.py` 中添加工具方法
2. 在 `backend/core.py` 的 `_should_use_tool` 方法中添加触发词
3. 在 `config/prompts.py` 中添加工具说明

### 自定义提示词

修改 `config/prompts.py` 中的 `SYSTEM_PROMPT` 即可。

## 📝 日志查看

```bash
# 查看实时日志
tail -f /app/work/logs/bypass/calm_agent.log

# 查看Streamlit日志
tail -f /app/work/logs/bypass/streamlit.log
```

## 🐛 常见问题

### Q: 启动失败？

检查依赖是否安装完整：
```bash
pip install -r requirements.txt
```

### Q: 模型调用失败？

确保环境变量正确设置，或检查网络连接。

### Q: 端口被占用？

修改启动命令中的端口：
```bash
python run.py start --port 8502
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📮 联系方式

- 项目地址: [GitHub](https://github.com/your-repo/calm-agent)
- 问题反馈: [Issues](https://github.com/your-repo/calm-agent/issues)

---

**🌊 平静 - 让AI触手可及，让创造不再受限**
