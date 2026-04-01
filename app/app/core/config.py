"""
音乐APP后端配置
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Music App Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/music.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 音乐存储路径
    MUSIC_DIR: str = "./data/music"
    
    # 网易云音乐API配置
    NETEASE_API_URL: str = "https://music.163.com"
    
    # 代理配置（可选）
    PROXY: str = None
    
    # 允许的文件类型
    ALLOWED_EXTENSIONS: List[str] = ["mp3", "flac", "m4a", "wav"]
    
    # 文件大小限制（MB）
    MAX_FILE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
