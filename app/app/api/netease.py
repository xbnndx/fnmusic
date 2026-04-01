"""
网易云音乐API
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import get_db, User, Playlist, Song, PlaylistSong
from app.schemas import (
    NeteaseLoginRequest, NeteaseQrCodeResponse, NeteaseLoginStatus,
    PlaylistImport, PlaylistResponse, PlaylistDetail,
    SongResponse, DailyRecommendSong, RankingListResponse, RankingDetailResponse,
    MessageResponse
)
from app.api.auth import get_current_user
from app.services import netease_api, download_service

router = APIRouter(prefix="/netease", tags=["网易云音乐"])


@router.get("/login/qrcode", response_model=NeteaseQrCodeResponse)
async def get_login_qrcode():
    """获取网易云登录二维码"""
    result = await netease_api.login_by_qr_code()
    
    if "error" in result:
        raise HTTPException(status_code=500, detail="获取二维码失败")
    
    return result


@router.get("/login/qrcode/status")
async def check_qrcode_status(key: str):
    """检查二维码扫码状态"""
    result = await netease_api.check_qr_code_status(key)
    return result


@router.post("/login", response_model=MessageResponse)
async def login_netease(
    login_data: NeteaseLoginRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """网易云账号登录"""
    if login_data.phone:
        result = await netease_api.login_by_phone(login_data.phone, login_data.password)
    elif login_data.email:
        result = await netease_api.login_by_email(login_data.email, login_data.password)
    else:
        raise HTTPException(status_code=400, detail="请提供手机号或邮箱")
    
    if result.get("status") == "success":
        # 保存登录信息到用户
        user_info = result.get("user", {})
        current_user.netease_uid = str(user_info.get("userId", ""))
        current_user.netease_cookie = result.get("cookie", "")
        db.commit()
        
        return {"message": "网易云登录成功", "success": True}
    
    raise HTTPException(status_code=401, detail=result.get("message", "登录失败"))


@router.post("/login/callback")
async def netease_login_callback(
    cookie: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保存网易云登录Cookie（二维码登录成功后调用）"""
    netease_api.set_cookie(cookie)
    
    # 获取用户信息
    status = await netease_api.get_login_status()
    
    if status.get("logged_in"):
        current_user.netease_cookie = cookie
        current_user.netease_uid = str(status.get("user", {}).get("userId", ""))
        db.commit()
        
        return {"message": "登录成功", "user": status.get("user")}
    
    raise HTTPException(status_code=400, detail="Cookie无效或已过期")


@router.get("/login/status", response_model=NeteaseLoginStatus)
async def get_netease_login_status(current_user: User = Depends(get_current_user)):
    """获取网易云登录状态"""
    if not current_user.netease_cookie:
        return {"logged_in": False}
    
    netease_api.set_cookie(current_user.netease_cookie)
    status = await netease_api.get_login_status()
    
    if status.get("logged_in"):
        user = status.get("user", {})
        return {
            "logged_in": True,
            "user_id": str(user.get("userId", "")),
            "nickname": user.get("nickname", ""),
            "avatar_url": user.get("avatarUrl", "")
        }
    
    return {"logged_in": False}


@router.get("/daily-recommend", response_model=List[DailyRecommendSong])
async def get_daily_recommend(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取每日推荐歌曲"""
    if not current_user.netease_cookie:
        raise HTTPException(status_code=401, detail="请先登录网易云音乐账号")
    
    netease_api.set_cookie(current_user.netease_cookie)
    songs = await netease_api.get_daily_recommend_songs()
    
    result = []
    for song_data in songs:
        # 检查是否已存在
        song = db.query(Song).filter(Song.source_id == str(song_data["id"])).first()
        
        if not song:
            song = Song(
                title=song_data["title"],
                artist=song_data["artist"],
                album=song_data.get("album"),
                cover_url=song_data.get("cover_url"),
                source="netease",
                source_id=str(song_data["id"]),
                duration=song_data.get("duration")
            )
            db.add(song)
            db.commit()
            db.refresh(song)
        
        result.append({
            "song": song,
            "reason": song_data.get("reason", "")
        })
    
    return result


@router.get("/rankings", response_model=List[RankingListResponse])
async def get_rankings():
    """获取网易云排行榜列表"""
    rankings = await netease_api.get_ranking_lists()
    
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "source": "netease",
            "cover_url": r.get("cover_url"),
            "song_count": 0
        }
        for r in rankings
    ]


@router.get("/rankings/{ranking_id}", response_model=RankingDetailResponse)
async def get_ranking_detail(
    ranking_id: int,
    db: Session = Depends(get_db)
):
    """获取排行榜详情"""
    detail = await netease_api.get_ranking_detail(ranking_id)
    
    if not detail:
        raise HTTPException(status_code=404, detail="排行榜不存在")
    
    songs = []
    for song_data in detail.get("songs", []):
        # 检查或创建歌曲记录
        song = db.query(Song).filter(Song.source_id == str(song_data["id"])).first()
        
        if not song:
            song = Song(
                title=song_data["title"],
                artist=song_data["artist"],
                album=song_data.get("album"),
                cover_url=song_data.get("cover_url"),
                source="netease",
                source_id=str(song_data["id"]),
                duration=song_data.get("duration")
            )
            db.add(song)
            db.commit()
            db.refresh(song)
        
        songs.append({
            "rank": song_data["rank"],
            "song": song
        })
    
    return {
        "id": detail["id"],
        "name": detail["name"],
        "source": "netease",
        "cover_url": detail.get("cover_url"),
        "song_count": len(songs),
        "songs": songs
    }


@router.post("/playlist/import", response_model=PlaylistDetail)
async def import_playlist(
    import_data: PlaylistImport,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导入网易云歌单"""
    playlist_id = netease_api.extract_playlist_id(import_data.url)
    
    if not playlist_id:
        raise HTTPException(status_code=400, detail="无效的歌单链接")
    
    detail = await netease_api.get_playlist_detail(playlist_id)
    
    if not detail:
        raise HTTPException(status_code=404, detail="歌单不存在或无法访问")
    
    # 创建本地歌单
    playlist = Playlist(
        user_id=current_user.id,
        name=detail["name"],
        description=detail.get("description"),
        cover_url=detail.get("cover_url"),
        source="netease",
        source_id=playlist_id,
        song_count=len(detail.get("songs", []))
    )
    db.add(playlist)
    db.flush()
    
    # 添加歌曲
    for idx, song_data in enumerate(detail.get("songs", [])):
        # 检查或创建歌曲
        song = db.query(Song).filter(Song.source_id == str(song_data["id"])).first()
        
        if not song:
            song = Song(
                title=song_data["title"],
                artist=song_data["artist"],
                album=song_data.get("album"),
                cover_url=song_data.get("cover_url"),
                source="netease",
                source_id=str(song_data["id"]),
                duration=song_data.get("duration")
            )
            db.add(song)
            db.flush()
        
        # 关联歌曲到歌单
        playlist_song = PlaylistSong(
            playlist_id=playlist.id,
            song_id=song.id,
            sort_order=idx
        )
        db.add(playlist_song)
    
    db.commit()
    db.refresh(playlist)
    
    # 获取完整歌单信息
    songs = db.query(Song).join(PlaylistSong).filter(
        PlaylistSong.playlist_id == playlist.id
    ).order_by(PlaylistSong.sort_order).all()
    
    return {
        "id": playlist.id,
        "name": playlist.name,
        "description": playlist.description,
        "cover_url": playlist.cover_url,
        "source": playlist.source,
        "song_count": playlist.song_count,
        "created_at": playlist.created_at,
        "songs": songs
    }


@router.post("/playlist/download")
async def download_playlist(
    playlist_id: int,
    quality: str = "lossless",
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """下载整个歌单"""
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.user_id == current_user.id
    ).first()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    
    if not current_user.netease_cookie:
        raise HTTPException(status_code=401, detail="请先登录网易云音乐")
    
    # 获取歌单歌曲
    songs = db.query(Song).join(PlaylistSong).filter(
        PlaylistSong.playlist_id == playlist.id
    ).all()
    
    # 转换为字典格式
    songs_data = [
        {
            "id": int(song.source_id),
            "title": song.title,
            "artist": song.artist,
            "album": song.album
        }
        for song in songs
    ]
    
    # 在后台执行下载
    netease_api.set_cookie(current_user.netease_cookie)
    
    async def download_task():
        results = await download_service.download_playlist(
            songs_data, 
            source="netease",
            quality=quality
        )
        # 更新歌曲本地路径
        for item in results["success"]:
            song = db.query(Song).filter(Song.title == item["song"]["title"]).first()
            if song:
                song.local_path = item["path"]
                song.quality = quality
        db.commit()
    
    if background_tasks:
        background_tasks.add_task(download_task)
    else:
        await download_task()
    
    return {"message": f"开始下载歌单，共{len(songs)}首歌曲", "total": len(songs)}
