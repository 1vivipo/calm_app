# 🌊 平静 Pro 部署指南

## 一、获取API Key（推荐免费方案）

### 方案1：讯飞星火Lite（推荐，永久免费）
1. 访问：https://console.xfyun.cn/
2. 注册/登录
3. 创建应用 → 选择"星火认知大模型"
4. 获取：APP ID、API Key、API Secret

### 方案2：通义千问（有免费额度）
1. 访问：https://dashscope.console.aliyun.com/
2. 开通"灵积模型服务"
3. 获取：API Key

---

## 二、部署到Hugging Face

### 步骤1：创建账号
访问：https://huggingface.co/ → 注册

### 步骤2：创建Space
1. 点击右上角头像 → New Space
2. 填写信息：
   - Space name: `calm-pro`（或任意名称）
   - SDK: 选择 `Streamlit`
   - License: MIT
3. 点击 `Create Space`

### 步骤3：上传文件
在Space页面，点击 `Files` → `Add file` → `Upload files`

**必须上传这3个文件：**
- `app.py`（应用主文件）
- `requirements.txt`（依赖文件）
- `README.md`（说明文件）

### 步骤4：等待部署
- 上传后自动开始部署
- 等待2-3分钟
- 部署完成后，访问地址：`https://huggingface.co/spaces/你的用户名/calm-pro`

---

## 三、使用方法

1. 打开部署后的网页
2. 在左侧边栏选择模型
3. 填写API配置
4. 点击"保存配置"
5. 开始对话！

---

## 四、文件下载

文件已保存在 `/workspace/projects/calm-pro-final/` 目录：
- app.py
- requirements.txt  
- README.md

---

## 五、常见问题

### Q: 部署失败怎么办？
A: 检查requirements.txt是否正确，确保streamlit版本匹配

### Q: API调用失败？
A: 确认API Key正确，且账户有余额/额度

### Q: 手机端显示异常？
A: 本应用已适配移动端，刷新页面即可

---

**祝你使用愉快！🌊**
