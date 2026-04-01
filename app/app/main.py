"""
FastAPI应用主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging

from app.core.config import settings
from app.models import init_db
from app.api import auth_router, netease_router, music_router, playlists_router

# 配置日志
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 启动时
    logger.info("Starting up...")
    init_db()
    
    # 确保音乐目录存在
    os.makedirs(settings.MUSIC_DIR, exist_ok=True)
    
    yield
    
    # 关闭时
    logger.info("Shutting down...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="支持网易云音乐、QQ音乐、酷狗音乐的歌单导入和无损音乐下载",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(netease_router, prefix="/api")
app.include_router(music_router, prefix="/api")
app.include_router(playlists_router, prefix="/api")

# 静态文件服务（用于播放本地音乐）
if os.path.exists(settings.MUSIC_DIR):
    app.mount("/music", StaticFiles(directory=settings.MUSIC_DIR), name="music")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
