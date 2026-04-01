#!/bin/bash
# 飞牛NAS音乐服务 - 打包脚本

# 打包说明
# 飞牛NAS的fpk格式本质上是一个压缩包
# 可以手动打包或使用fnpack工具

echo "📦 开始打包飞牛NAS音乐服务..."

# 创建临时目录
TMP_DIR=$(mktemp -d)
APP_NAME="fnmusic"
OUTPUT_DIR="/workspace/fnmusic-fpk"

# 复制必要文件
cp -r "$OUTPUT_DIR/app" "$TMP_DIR/"
cp "$OUTPUT_DIR/ICON.PNG" "$TMP_DIR/app/"
cp "$OUTPUT_DIR/README.md" "$TMP_DIR/app/"

# 打包（fpk实际上是tar.gz格式）
cd "$TMP_DIR"
tar -czf "$OUTPUT_DIR/${APP_NAME}.fpk" app

# 清理
rm -rf "$TMP_DIR"

echo "✅ 打包完成: $OUTPUT_DIR/${APP_NAME}.fpk"
