#!/bin/bash
# 飞牛NAS 音乐服务 一键部署脚本

set -e

echo "======================================"
echo "  🎵 音乐服务 - 一键部署"
echo "======================================"
echo ""

# 配置
APP_NAME="fnmusic"
INSTALL_DIR="/share/MusicApp"
PORT=8000

# 检查是否为root
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root权限运行此脚本"
    echo "   执行: sudo bash $0"
    exit 1
fi

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先在飞牛NAS应用中心安装Docker"
    exit 1
fi

echo "📁 创建目录..."
mkdir -p $INSTALL_DIR/{data,music}
cd $INSTALL_DIR

echo "📥 下载代码..."
if [ -d "$APP_NAME" ]; then
    echo "目录已存在，更新代码..."
    cd $APP_NAME && git pull
else
    git clone https://github.com/xbnndx/$APP_NAME.git
    cd $APP_NAME
fi

echo "🔨 构建Docker镜像..."
docker build -t $APP_NAME ./app

echo "🛑 停止旧容器..."
docker stop $APP_NAME 2>/dev/null || true
docker rm $APP_NAME 2>/dev/null || true

echo "🚀 启动服务..."
docker run -d \
    --name $APP_NAME \
    --restart unless-stopped \
    -p $PORT:8000 \
    -v $INSTALL_DIR/data:/app/data \
    -v $INSTALL_DIR/music:/app/data/music \
    -e DATABASE_URL="sqlite:///./data/music.db" \
    -e MUSIC_DIR="/app/data/music" \
    -e SECRET_KEY="$(openssl rand -hex 32)" \
    -e DEBUG="false" \
    $APP_NAME

echo ""
sleep 3

# 检查状态
if docker ps | grep -q $APP_NAME; then
    echo "======================================"
    echo "  ✅ 部署成功！"
    echo "======================================"
    echo ""
    echo "📍 服务地址: http://$(hostname -I | awk '{print $1}'):$PORT"
    echo "📚 API文档: http://$(hostname -I | awk '{print $1}'):$PORT/docs"
    echo "🎵 音乐存储: $INSTALL_DIR/music"
    echo ""
    echo "查看日志: docker logs -f $APP_NAME"
else
    echo "❌ 部署失败，查看日志："
    docker logs $APP_NAME
fi
