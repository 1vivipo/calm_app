---
title: 平静 AI Agent
emoji: 🌊
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.55.0
app_file: app.py
pinned: false
license: mit
---

# 🌊 平静 - AI助手

永久免费的多模态AI助手，支持对话、搜索、图像生成、视频生成、文档生成等功能。

## 功能特性

- 💬 **智能对话** - 多轮对话，上下文理解
- 🔍 **网页搜索** - 实时信息获取
- 🎨 **图像生成** - 文本转图像
- 🎬 **视频生成** - 文本转视频
- 📄 **文档生成** - PDF/Word/Excel
- 🖼️ **图像理解** - 图片识别分析

## 使用方法

1. 直接在对话框输入问题即可开始对话
2. 使用快捷指令：
   - `搜索 xxx` - 网页搜索
   - `生成图片 xxx` - 图像创作
   - `生成视频 xxx` - 视频制作
   - `生成文档 xxx` - 文档生成

## 部署说明

本项目支持多种部署方式：
- Hugging Face Spaces（推荐）
- Streamlit Cloud
- 本地部署

## 技术栈

- 前端：Streamlit
- 后端：Python + FastAPI
- AI模型：豆包/讯飞/开源模型

## 配置

可选配置环境变量：
- `XUNFEI_APP_ID` - 讯飞应用ID
- `XUNFEI_API_KEY` - 讯飞API密钥
- `XUNFEI_API_SECRET` - 讯飞API密钥

不配置也能使用基础功能。

## 许可证

MIT License
