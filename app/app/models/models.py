"""
数据库模型
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

from app.core.config import settings

# 确保数据目录存在
os.makedirs(os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite需要
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255))
    netease_uid = Column(String(50), nullable=True)  # 网易云用户ID
    netease_cookie = Column(Text, nullable=True)  # 网易云登录Cookie
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    playlists = relationship("Playlist", back_populates="user", cascade="all, delete-orphan")
    download_tasks = relationship("DownloadTask", back_populates="user", cascade="all, delete-orphan")


class Playlist(Base):
    """歌单表"""
    __tablename__ = "playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(200))
    description = Column(Text, nullable=True)
    cover_url = Column(String(500), nullable=True)
    source = Column(String(50))  # netease, qq, kugou
    source_id = Column(String(100), nullable=True)  # 原平台歌单ID
    song_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    user = relationship("User", back_populates="playlists")
    songs = relationship("PlaylistSong", back_populates="playlist", cascade="all, delete-orphan")


class Song(Base):
    """歌曲表"""
    __tablename__ = "songs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    artist = Column(String(200))
    album = Column(String(200), nullable=True)
    cover_url = Column(String(500), nullable=True)
    source = Column(String(50))  # netease, qq, kugou
    source_id = Column(String(100), unique=True)  # 原平台歌曲ID
    duration = Column(Integer, nullable=True)  # 时长（毫秒）
    quality = Column(String(20), nullable=True)  # 品质：standard, high, lossless
    local_path = Column(String(500), nullable=True)  # 本地存储路径
    file_size = Column(Float, nullable=True)  # 文件大小（MB）
    created_at = Column(DateTime, default=datetime.utcnow)


class PlaylistSong(Base):
    """歌单-歌曲关联表"""
    __tablename__ = "playlist_songs"
    
    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"))
    song_id = Column(Integer, ForeignKey("songs.id"))
    sort_order = Column(Integer, default=0)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联
    playlist = relationship("Playlist", back_populates="songs")
    song = relationship("Song")


class DownloadTask(Base):
    """下载任务表"""
    __tablename__ = "download_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    song_id = Column(Integer, ForeignKey("songs.id"))
    status = Column(String(20), default="pending")  # pending, downloading, completed, failed
    progress = Column(Integer, default=0)  # 下载进度 0-100
    quality = Column(String(20))  # 下载品质
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # 关联
    user = relationship("User", back_populates="download_tasks")
    song = relationship("Song")


class NeteaseDaily(Base):
    """网易云音乐每日推荐缓存"""
    __tablename__ = "netease_daily"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    song_id = Column(Integer, ForeignKey("songs.id"))
    reason = Column(String(200), nullable=True)  # 推荐理由
    date = Column(String(10))  # YYYY-MM-DD
    created_at = Column(DateTime, default=datetime.utcnow)


class RankingList(Base):
    """排行榜缓存"""
    __tablename__ = "ranking_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    source = Column(String(50))  # netease, qq, kugou
    source_id = Column(String(100))  # 原平台榜单ID
    cover_url = Column(String(500), nullable=True)
    update_frequency = Column(String(50), nullable=True)  # 更新频率
    updated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RankingSong(Base):
    """榜单歌曲"""
    __tablename__ = "ranking_songs"
    
    id = Column(Integer, primary_key=True, index=True)
    ranking_id = Column(Integer, ForeignKey("ranking_lists.id"))
    song_id = Column(Integer, ForeignKey("songs.id"))
    rank = Column(Integer)
    last_rank = Column(Integer, nullable=True)
    trend = Column(String(20), nullable=True)  # up, down, new, stable
    created_at = Column(DateTime, default=datetime.utcnow)


# 创建数据库表
def init_db():
    Base.metadata.create_all(bind=engine)


# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
