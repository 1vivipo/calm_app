# 🚀 极简部署指南 - 3分钟完成

## 当前状态

✅ 代码已准备好  
✅ 移动端已完美适配  
✅ 支持讯飞/豆包/免费模型  

## 部署到Hugging Face（推荐）

### 第一步：创建账号

1. 访问 **https://huggingface.co**（或国内镜像 **https://hf-mirror.com**）
2. 点击右上角 **Sign Up** 免费注册
3. 验证邮箱

### 第二步：创建Space

1. 登录后，点击右上角头像 → **New Space**
2. 填写信息：
   - **Space name**: `calm-ai-agent`（或任意名称）
   - **License**: MIT
   - **SDK**: 选择 **Streamlit**
   - **Visibility**: **Public**
3. 点击 **Create Space**

### 第三步：上传文件

在Space页面，点击 **Files** 标签，然后：

#### 方式A：网页上传（最简单）

1. 点击 **Add file** → **Upload files**
2. 上传以下3个文件：
   ```
   README.md（覆盖默认的）
   app.py
   requirements.txt
   ```
3. 点击 **Commit changes**

#### 方式B：Git上传（更快）

```bash
# 在你的电脑上
git clone https://huggingface.co/spaces/YOUR_USERNAME/calm-ai-agent
cd calm-ai-agent

# 下载文件
# 从这里下载：https://gitee.com/r1se23/ai-agent
# 把 calm-agent-hf 文件夹里的3个文件复制过来

# 提交并推送
git add .
git commit -m "Deploy Calm AI Agent"
git push
```

### 第四步：等待部署

- Hugging Face会自动构建（约2-3分钟）
- 可以在 **Logs** 标签查看进度

### 第五步：访问应用

部署成功后，使用以下地址访问：

- **国际线路**: `https://YOUR_USERNAME-calm-ai-agent.hf.space`
- **国内镜像**: `https://YOUR_USERNAME-calm-ai-agent.hf-mirror.com` ⭐ 推荐

## 配置API密钥（可选）

如果你想使用完整的AI功能：

1. 进入你的Space → **Settings**
2. 找到 **Repository Secrets**
3. 添加你的讯飞API密钥：
   ```
   XUNFEI_APP_ID = 你的APP_ID
   XUNFEI_API_KEY = 你的API_KEY
   XUNFEI_API_SECRET = 你的API_SECRET
   ```

不配置也能使用基础对话功能。

## 文件说明

```
calm-ai-agent/
├── README.md         # Space说明文件（必须）
├── app.py            # 主程序（单文件，约300行）
└── requirements.txt  # Python依赖
```

就这么简单！只有3个文件。

---

## 📱 测试访问

部署完成后，用手机浏览器访问：
```
https://YOUR_USERNAME-calm-ai-agent.hf-mirror.com
```

完美适配移动端！

---

## 常见问题

### Q: 部署失败怎么办？
A: 检查Logs，通常是文件名或格式问题

### Q: 访问很慢？
A: 使用国内镜像 `hf-mirror.com`

### Q: 想要修改功能？
A: 直接编辑 `app.py` 文件即可

### Q: 会消耗你的token吗？
A: **不会！** 完全独立运行，使用你自己的API密钥或基础模式

---

## 🎉 完成！

部署后，你就拥有了一个：
- ✅ 永久免费的AI助手
- ✅ 手机完美适配
- ✅ 国内可访问
- ✅ 支持自定义API

---

**如有问题，随时询问！**
