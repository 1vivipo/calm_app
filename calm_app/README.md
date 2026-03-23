# 平静 AI - 移动端应用

一个简洁的AI对话应用，支持Android和iOS。

## 功能特点

- 🗣️ 实时对话：直接与AI对话，无延迟
- 🔍 联网搜索：AI可以搜索网络获取实时信息
- 📱 双端支持：Android APK + iOS
- 🌙 深色模式：自动跟随系统主题

## 构建APK

### 方式一：GitHub Actions自动构建（推荐）

1. Fork本仓库
2. 进入Actions页面
3. 运行"Build APK"工作流
4. 构建完成后下载APK

### 方式二：本地构建

```bash
# 安装Flutter
# https://docs.flutter.dev/get-started/install

# 获取依赖
cd calm_app
flutter pub get

# 构建APK
flutter build apk --release

# APK位置
# build/app/outputs/flutter-apk/app-release.apk
```

## 配置API

首次打开应用时，需要配置Agent API地址：

1. 点击右上角设置图标
2. 输入你的Agent API地址
3. 保存后即可开始对话

### Coze平台API格式

```
https://api.coze.cn/v3/chat?token=YOUR_TOKEN
```

或使用你部署的Agent端点。

## 项目结构

```
calm_app/
├── lib/
│   └── main.dart      # 主代码
├── android/           # Android配置
├── ios/               # iOS配置
├── pubspec.yaml       # 依赖配置
└── .github/
    └── workflows/
        └── build.yml  # 自动构建
```

## 技术栈

- **框架**: Flutter 3.19
- **语言**: Dart
- **UI**: Material Design 3
- **网络**: http包

## License

MIT
