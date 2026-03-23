# 平静AI - 安装与使用指南

## 📱 APK下载

APK已构建成功！由于GitHub限制，请按以下步骤下载：

### 方式一：GitHub Actions下载（推荐）
1. 打开链接：https://github.com/1vivipo/calm_app/actions
2. 点击最新的 "Build APK" 工作流
3. 滚动到底部 "Artifacts" 区域
4. 点击 `calm-ai-apk` 下载ZIP文件
5. 解压得到 `calm-ai.apk`
6. 安装到手机

### 方式二：直接下载链接
需要登录GitHub账号：
- Artifact ID: 6052524586
- 直接链接：https://github.com/1vivipo/calm_app/actions/artifacts/6052524586

---

## ⚙️ 配置Agent API

App安装后，首次打开需要配置API地址。

### 获取API地址
如果你已部署Agent到Coze平台：
1. 打开Coze平台
2. 进入你的Bot详情页
3. 找到API调用地址
4. 复制完整URL（包含token参数）

### 配置示例
```
https://api.coze.cn/v3/chat?token=YOUR_TOKEN_HERE
```

---

## 🤖 当前Agent能力

已部署的Agent具备以下能力：

### ✅ 已实现
| 能力 | 说明 |
|------|------|
| 联网搜索 | 实时获取新闻、数据、信息 |
| 对话记忆 | 保留最近20轮对话 |
| 多轮对话 | 支持上下文连续对话 |
| 智能问答 | 知识问答、问题分析 |

### 使用示例
```
用户: 今天有什么新闻？
Agent: [自动调用搜索工具] 根据最新消息...

用户: 帮我解释一下什么是机器学习
Agent: 机器学习是人工智能的一个分支...

用户: 翻译这段英文到中文...
Agent: [直接翻译]
```

---

## 🔧 项目仓库

- App代码：https://github.com/1vivipo/calm_app
- 查看构建日志：https://github.com/1vivipo/calm_app/actions

---

## 📝 后续优化建议

1. **图片理解** - 添加多模态模型支持
2. **语音对话** - 集成语音识别和合成
3. **文件处理** - 支持文档上传和分析
4. **本地缓存** - 优化对话历史存储

---

## ❓ 常见问题

**Q: APK下载需要登录吗？**
A: 是的，GitHub Actions的Artifacts需要登录GitHub账号才能下载。

**Q: Agent API如何获取？**
A: 在Coze平台部署Agent后，会获得一个API调用地址。

**Q: App支持iOS吗？**
A: 当前只构建了Android APK。iOS需要Apple开发者账号才能分发。

---

*构建时间: 2026-03-23*
*APK版本: 1.0.0*
