# 平静AI - Flutter客户端

一个功能完整的AI对话客户端，支持模型切换、图片生成、代码执行等功能。

## 功能特性

### 🤖 智能对话
- **三档模型切换**：
  - Mini快速：轻量模型，秒级响应
  - Pro思考：平衡性能，深度分析
  - Agent专家：完整工具链，画图/搜索/代码

### 🖼️ 图片功能
- **图片生成**：让AI画出你想要的图片
- **图片识别**：拍照或上传图片让AI分析
- **图片下载**：一键保存AI生成的图片
- **图片预览**：点击放大，双指缩放

### 📝 操作体验
- **一键复制**：长按消息可复制全文
- **链接复制**：自动识别链接，单独复制
- **下载图片**：长按图片直接下载到相册
- **保存文档**：将对话保存为文本文件
- **分享功能**：分享消息给其他应用

### 📱 输入增强
- **多行输入**：支持最多6行输入
- **图片上传**：拍照或从相册选择
- **URL输入**：直接粘贴图片链接

## 快速开始

### 环境要求
- Flutter SDK >= 3.0.0
- Android SDK >= 21
- Xcode (iOS开发)

### 安装依赖
```bash
cd calm_app
flutter pub get
```

### 运行调试
```bash
flutter run
```

### 打包APK
```bash
# 使用打包脚本
chmod +x build_apk.sh
./build_apk.sh release

# 或手动打包
flutter build apk --release
```

APK输出位置：`build/app/outputs/flutter-apk/app-release.apk`

## 项目结构

```
calm_app/
├── lib/
│   └── main.dart          # 主程序入口
├── android/
│   ├── app/
│   │   ├── build.gradle   # Android构建配置
│   │   └── src/main/
│   │       └── AndroidManifest.xml  # 权限配置
│   └── ...
├── ios/
├── pubspec.yaml           # 依赖配置
├── build_apk.sh           # APK打包脚本
└── README.md
```

## API配置

API地址在 `lib/main.dart` 中配置：

```dart
static const String _apiUrl = 'YOUR_API_URL/run';
```

## 权限说明

### Android权限
- `INTERNET` - 网络访问
- `CAMERA` - 拍照
- `READ_EXTERNAL_STORAGE` - 读取存储
- `WRITE_EXTERNAL_STORAGE` - 写入存储
- `READ_MEDIA_IMAGES` - 读取图片（Android 13+）

### iOS权限
需要在 `ios/Runner/Info.plist` 中添加：
```xml
<key>NSCameraUsageDescription</key>
<string>需要相机权限来拍照</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>需要相册权限来选择图片</string>
```

## 使用指南

### 模型切换
1. 点击顶部的模型标签
2. 或点击右上角的调节图标
3. 选择适合的模型

### 发送图片
1. 点击输入框左侧的 **+** 按钮
2. 选择拍照/相册/URL
3. 输入文字描述（可选）
4. 点击发送

### 保存内容
1. **复制消息**：长按消息 → 选择"复制全文"
2. **下载图片**：长按图片 → 选择"下载图片"
3. **复制链接**：长按消息 → 选择要复制的链接
4. **保存文档**：长按消息 → 选择"保存为文本文件"

## 常见问题

### Q: 图片上传失败？
A: 检查是否授予了相机和存储权限

### Q: 无法下载图片？
A: Android 10+需要授予存储权限，图片会保存到Download目录

### Q: 模型切换不生效？
A: 确保后端API支持model参数传递

## 后端配套

本项目需要配合后端API使用，后端项目位于 `src/` 目录。

后端支持：
- 动态模型选择
- 图片生成
- 代码执行
- 网络搜索
- 图片分析

## 版本历史

### v1.0.1 (当前版本)
- ✅ 新增模型切换功能
- ✅ 新增图片上传功能
- ✅ 新增一键复制功能
- ✅ 新增图片下载功能
- ✅ 新增文档保存功能
- ✅ 优化UI交互体验

### v1.0.0
- 初始版本
- 基础对话功能

## 技术栈

- **Flutter** - UI框架
- **http** - 网络请求
- **image_picker** - 图片选择
- **cached_network_image** - 图片缓存
- **path_provider** - 文件存储
- **share_plus** - 分享功能
- **url_launcher** - 打开链接

## License

MIT License
