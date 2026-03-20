# Hugging Face Spaces 部署指南

## 方式1: 通过网页界面部署（推荐）

### 步骤：

1. **创建Hugging Face账号**
   - 访问：https://huggingface.co
   - 或国内镜像：https://hf-mirror.com
   - 免费注册

2. **创建新Space**
   - 点击右上角头像 -> "New Space"
   - 名称：`calm-ai-agent`（或任意名称）
   - SDK选择：`Streamlit`
   - 选择：Public（公开）

3. **上传文件**
   
   方式A - 使用网页上传：
   - 进入你的Space页面
   - 点击"Files"
   - 上传以下文件：
     ```
     app.py
     requirements.txt
     frontend/app_v2.py -> 重命名为 frontend_app_v2.py
     backend/core_v2.py -> 重命名为 backend_core_v2.py
     backend/models.py -> 重命名为 backend_models.py
     backend/session.py -> 重命名为 backend_session.py
     backend/tools.py -> 重命名为 backend_tools.py
     config/config.py -> 重命名为 config_config.py
     config/prompts.py -> 重命名为 config_prompts.py
     ```

   方式B - 使用Git（推荐）：
   ```bash
   # 克隆你的Space
   git clone https://huggingface.co/spaces/YOUR_USERNAME/calm-ai-agent
   cd calm-ai-agent
   
   # 复制文件
   cp /workspace/projects/calm-agent/app.py .
   cp /workspace/projects/calm-agent/requirements.txt .
   cp -r /workspace/projects/calm-agent/frontend .
   cp -r /workspace/projects/calm-agent/backend .
   cp -r /workspace/projects/calm-agent/config .
   
   # 提交并推送
   git add .
   git commit -m "Deploy Calm AI Agent"
   git push
   ```

4. **等待构建**
   - Hugging Face会自动构建和部署
   - 大约2-3分钟

5. **访问应用**
   - 国际线路：`https://YOUR_USERNAME-calm-ai-agent.hf.space`
   - 国内镜像：`https://YOUR_USERNAME-calm-ai-agent.hf-mirror.com`

---

## 方式2: 使用API部署（更简单）

```bash
# 安装Hugging Face Hub
pip install huggingface_hub

# 登录（需要token）
huggingface-cli login

# 创建Space
huggingface-cli repo create calm-ai-agent --type space --space_sdk streamlit

# 上传文件
cd /workspace/projects/calm-agent
git init
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/calm-ai-agent
git add .
git commit -m "Initial deployment"
git push space main
```

---

## 配置API密钥（可选）

如果要使用讯飞API，在Space设置中添加Secrets：

1. 进入Space -> Settings
2. 找到"Repository Secrets"
3. 添加：
   - `XUNFEI_APP_ID` = 你的APP_ID
   - `XUNFEI_API_KEY` = 你的API_KEY
   - `XUNFEI_API_SECRET` = 你的API_SECRET

---

## 国内访问优化

使用镜像站点访问：
- **镜像地址**：`https://YOUR_USERNAME-calm-ai-agent.hf-mirror.com`
- **特点**：
  - 自动使用国内CDN
  - 无需翻墙
  - 速度快

---

## 文件结构（HF Spaces）

```
calm-ai-agent/
├── app.py              # 主入口
├── requirements.txt    # 依赖
├── frontend/
│   └── app_v2.py      # Streamlit应用
├── backend/
│   ├── __init__.py
│   ├── core_v2.py     # 核心引擎
│   ├── models.py      # 数据模型
│   ├── session.py     # 会话管理
│   └── tools.py       # 工具
└── config/
    ├── __init__.py
    ├── config.py      # 配置
    └── prompts.py     # 提示词
```

---

## 注意事项

1. **免费额度**
   - CPU Space免费
   - GPU Space需要付费（不需要，我们的应用用CPU足够）

2. **自动休眠**
   - 免费Space在无访问时会休眠
   - 首次访问需要等待10-30秒唤醒
   - 使用镜像站点可能更快

3. **流量限制**
   - 免费Space有流量限制
   - 对于个人使用完全足够

4. **持久化**
   - Space是无状态的
   - 会话数据会丢失
   - 需要持久化可以添加数据库

---

## 快速开始

### 最简单的方式（3步完成）：

```bash
# 1. 进入项目目录
cd /workspace/projects/calm-agent

# 2. 添加HF远程仓库（替换YOUR_USERNAME）
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/calm-ai-agent

# 3. 推送代码
git push hf main --force
```

完成！访问 `https://YOUR_USERNAME-calm-ai-agent.hf-mirror.com`

---

## 问题排查

### Q: 显示"Application error"？
A: 检查requirements.txt是否完整，查看Space的Logs

### Q: 访问很慢？
A: 使用国内镜像 `hf-mirror.com`

### Q: 想要自定义域名？
A: Space设置中可以绑定自定义域名

---

**建议**：使用国内镜像访问，速度快且稳定！
