# 飞牛NAS 音乐服务

支持网易云音乐、QQ音乐、酷狗音乐的歌单导入和无损音乐下载服务。

## 🚀 一键安装

SSH连接到飞牛NAS，执行：

```bash
curl -fsSL https://github.com/xbnndx/fnmusic/raw/main/install.sh | bash
```

## 📦 手动安装

```bash
# 1. SSH连接
ssh admin@你的NAS_IP
sudo -i

# 2. 创建目录并下载
mkdir -p /share/MusicApp && cd /share/MusicApp
git clone https://github.com/xbnndx/fnmusic.git
cd fnmusic

# 3. 执行安装
bash install.sh
```

## 🌐 访问地址

- API文档：`http://NAS_IP:8001/docs`
- 服务端口：**8001**（避免与飞牛NAS默认端口冲突）

## 📱 Android客户端

在Android应用设置中，服务器地址填：
```
http://你的NAS_IP:8001
```

## 🔧 常用命令

```bash
# 查看日志
docker logs -f fnmusic

# 重启服务
docker restart fnmusic

# 停止服务
docker stop fnmusic

# 卸载
bash /share/MusicApp/fnmusic/uninstall.sh
```

## 📂 目录说明

| 目录 | 说明 |
|------|------|
| `/share/MusicApp/data` | 数据库、配置 |
| `/share/MusicApp/music` | 下载的音乐文件 |

## ⚠️ 注意事项

- 默认端口：**8001**
- 仅供学习交流使用
- 请支持正版音乐
