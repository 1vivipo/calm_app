#!/bin/bash

# 平静AI - APK打包脚本
# 使用方法: ./build_apk.sh [release|debug]

set -e

BUILD_TYPE=${1:-release}
PROJECT_DIR=$(dirname "$0")

echo "=========================================="
echo "  平静AI - APK打包工具"
echo "  构建类型: $BUILD_TYPE"
echo "=========================================="

cd "$PROJECT_DIR"

# 检查Flutter环境
if ! command -v flutter &> /dev/null; then
    echo "❌ 错误: 未找到Flutter，请先安装Flutter SDK"
    exit 1
fi

echo ""
echo "📦 步骤1: 清理项目..."
flutter clean

echo ""
echo "📦 步骤2: 获取依赖..."
flutter pub get

echo ""
echo "📦 步骤3: 检查依赖问题..."
flutter doctor -v

echo ""
echo "📦 步骤4: 开始构建APK..."
if [ "$BUILD_TYPE" = "release" ]; then
    flutter build apk --release --target-platform android-arm64
else
    flutter build apk --debug --target-platform android-arm64
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 构建成功！"
    echo ""
    APK_PATH="build/app/outputs/flutter-apk/app-$BUILD_TYPE.apk"
    if [ -f "$APK_PATH" ]; then
        APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
        echo "📱 APK文件位置: $APK_PATH"
        echo "📊 APK文件大小: $APK_SIZE"
        echo ""
        echo "🎉 你可以将APK安装到Android设备上了！"
    fi
else
    echo ""
    echo "❌ 构建失败，请检查错误信息"
    exit 1
fi
