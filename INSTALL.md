# 飞牛NAS音乐服务 - 安装指南

## 📦 文件说明

本目录包含飞牛NAS音乐服务的完整安装包，包含以下文件：

```
fnmusic-fpk/
├── fnpack.json      # 应用索引配置（用于FnDepot商店）
├── fnmusic.fpk      # 应用安装包
├── ICON.PNG         # 应用图标（256x256）
├── README.md        # 应用说明
├── Preview/         # 预览图目录
├── app/             # 应用源代码
│   ├── Dockerfile       # Docker构建文件
│   ├── docker.json      # Docker配置
│   ├── requirements.txt # Python依赖
│   ├── run.py           # 启动脚本
│   └── app/             # 应用代码
└── build.sh         # 打包脚本
```

## 🚀 安装方法

### 方法一：应用商店上传（推荐）

1. 打开飞牛NAS **应用中心**
2. 点击右上角 **设置** ⚙️
3. 选择 **手动安装应用**
4. 上传 `fnmusic.fpk` 文件
5. 点击安装，等待完成

### 方法二：SSH命令安装

```bash
# 1. 上传fpk文件到NAS
# 2. SSH连接到NAS
ssh admin@你的NAS_IP

# 3. 切换到root
sudo -i

# 4. 安装应用
appcenter-cli install-fpk fnmusic.fpk
```

### 方法三：Docker Compose手动部署

如果不想使用fpk，也可以手动部署：

```bash
# 1. 复制app目录到NAS
scp -r app/ admin@NAS_IP:/vol1/1000/fnmusic/

# 2. SSH连接并部署
ssh admin@NAS_IP
cd /vol1/1000/fnmusic

# 3. 构建并运行
docker build -t fnmusic .
docker run -d \
  --name fnmusic \
  --restart unless-stopped \
  -p 8000:8000 \
  -v /share/MusicApp/data:/app/data \
  -v /share/MusicApp/music:/app/data/music \
  fnmusic
```

## 📱 Android客户端配置

安装完成后，在Android应用中：

1. 打开应用，进入 **设置**
2. 修改服务器地址为：`http://你的NAS_IP:8000`
3. 注册账号并登录
4. 在设置中绑定网易云音乐账号

## ⚠️ 注意事项

1. **端口冲突**：如果8000端口被占用，需要修改docker配置
2. **存储空间**：确保有足够的存储空间存放音乐
3. **网络访问**：确保NAS和手机在同一局域网内
4. **版权问题**：仅供学习交流，请支持正版音乐

## 📚 相关链接

- API文档：`http://NAS_IP:8000/docs`
- 音乐存储：`/share/MusicApp/music`
- 数据目录：`/share/MusicApp/data`

## 🔧 故障排查

### 服务无法启动
```bash
# 查看容器日志
docker logs fnmusic

# 检查端口占用
netstat -tulpn | grep 8000
```

### 无法访问API
- 检查防火墙设置
- 确认容器正在运行：`docker ps`
- 检查端口映射是否正确

### 下载失败
- 检查网络连接
- 部分歌曲需要VIP账号
- 查看日志确认错误原因
