# 飞牛NAS音乐服务

支持网易云音乐、QQ音乐、酷狗音乐的歌单导入和无损音乐下载服务。

## 功能特性

- 🎵 **网易云音乐**：账号登录、每日推荐、排行榜、歌单导入、无损下载
- 🔍 **QQ音乐**：搜索、无损下载、排行榜
- 🎧 **酷狗音乐**：搜索、无损下载
- 📱 **Android客户端**：Material Design 3 界面、后台播放支持

## 快速安装

### 方法一：应用商店上传

1. 下载 `fnmusic.fpk` 文件
2. 打开飞牛NAS应用中心 → 设置 → 手动安装应用
3. 上传fpk文件，点击安装

### 方法二：Docker手动部署

```bash
docker build -t fnmusic ./app
docker run -d -p 8000:8000 \
  -v /share/MusicApp/data:/app/data \
  -v /share/MusicApp/music:/app/data/music \
  --name fnmusic \
  fnmusic
```

## 访问地址

- API文档：`http://NAS_IP:8000/docs`
- 服务端口：8000

## Android客户端

在 `android-app` 目录下，使用Android Studio打开项目构建APK。

## 目录结构

```
fnmusic/
├── fnpack.json      # 应用商店配置
├── fnmusic.fpk      # 安装包
├── ICON.PNG         # 图标
├── app/             # 后端源码
│   ├── Dockerfile
│   ├── docker.json
│   ├── requirements.txt
│   ├── run.py
│   └── app/         # Python代码
└── android-app/     # Android客户端源码
```

## 注意事项

- 仅供学习交流使用
- 请支持正版音乐
- 部分无损音乐需要VIP账号

## License

MIT
