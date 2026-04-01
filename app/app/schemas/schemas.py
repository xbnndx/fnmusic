"""
Pydantic schemas for API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============ 用户相关 ============
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    netease_uid: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ============ 歌曲相关 ============
class SongBase(BaseModel):
    title: str
    artist: str
    album: Optional[str] = None
    cover_url: Optional[str] = None
    source: str
    source_id: str
    duration: Optional[int] = None


class SongResponse(SongBase):
    id: int
    quality: Optional[str] = None
    local_path: Optional[str] = None
    file_size: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SongSearchResult(BaseModel):
    id: int
    title: str
    artist: str
    album: Optional[str] = None
    cover_url: Optional[str] = None
    source: str
    source_id: str
    duration: Optional[int] = None
    has_lossless: bool = False
    quality_info: Optional[dict] = None


# ============ 歌单相关 ============
class PlaylistCreate(BaseModel):
    name: str
    description: Optional[str] = None
    source: Optional[str] = "local"


class PlaylistImport(BaseModel):
    url: str  # 分享链接
    source: str = "netease"


class PlaylistResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    source: str
    song_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PlaylistDetail(PlaylistResponse):
    songs: List[SongResponse] = []


# ============ 下载相关 ============
class DownloadRequest(BaseModel):
    song_id: Optional[int] = None
    source: Optional[str] = None
    source_id: Optional[str] = None
    quality: str = "lossless"  # standard, high, lossless


class DownloadTaskResponse(BaseModel):
    id: int
    song_id: int
    status: str
    progress: int
    quality: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============ 网易云音乐相关 ============
class NeteaseLoginRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    password: str
    captcha: Optional[str] = None


class NeteaseQrCodeResponse(BaseModel):
    qr_code_url: str
    key: str


class NeteaseLoginStatus(BaseModel):
    logged_in: bool
    user_id: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


class DailyRecommendSong(BaseModel):
    song: SongResponse
    reason: Optional[str] = None


class RankingListResponse(BaseModel):
    id: int
    name: str
    source: str
    cover_url: Optional[str] = None
    song_count: int
    
    class Config:
        from_attributes = True


class RankingDetailResponse(RankingListResponse):
    songs: List[dict]  # 包含排名信息


# ============ 搜索相关 ============
class SearchRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    source: str = "all"  # all, netease, qq, kugou
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class SearchResult(BaseModel):
    songs: List[SongSearchResult]
    total: int
    page: int
    page_size: int
    has_more: bool


# ============ 通用响应 ============
class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
