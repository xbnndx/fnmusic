FROM python:3.11-slim

LABEL maintainer="MusicApp Team"
LABEL description="Music service for FeiNiu NAS"
LABEL version="1.0.0"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    musl-dev \
    libffi-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY app/ ./app/
COPY run.py .

# 创建数据目录
RUN mkdir -p /app/data/music

# 创建非root用户
RUN useradd -m -u 1000 musicuser && \
    chown -R musicuser:musicuser /app

USER musicuser

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_URL=sqlite:///./data/music.db \
    MUSIC_DIR=/app/data/music \
    SECRET_KEY=please-change-this-secret-key \
    DEBUG=false

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 启动命令
CMD ["python", "run.py"]
