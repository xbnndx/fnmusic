#!/bin/bash
# 卸载脚本

APP_NAME="fnmusic"
INSTALL_DIR="/share/MusicApp"

echo "🛑 停止服务..."
docker stop $APP_NAME 2>/dev/null || true
docker rm $APP_NAME 2>/dev/null || true
docker rmi $APP_NAME 2>/dev/null || true

echo "✅ 服务已停止"
echo ""
echo "⚠️  数据目录 $INSTALL_DIR 已保留"
echo "   如需删除，执行: rm -rf $INSTALL_DIR"
