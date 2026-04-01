"""
音乐搜索和下载API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import get_db, User, Song, DownloadTask
from app.schemas import (
    SearchRequest, SearchResult, SongSearchResult,
    DownloadRequest, DownloadTaskResponse, MessageResponse
)
from app.api.auth import get_current_user
from app.services import netease_api, qq_music_api, kugou_music_api, download_service

router = APIRouter(prefix="/music", tags=["音乐"])


@router.get("/search", response_model=SearchResult)
async def search_music(
    keyword: str = Query(..., min_length=1),
    source: str = Query("all", regex="^(all|netease|qq|kugou)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """搜索歌曲"""
    all_songs = []
    total = 0
    
    if source in ["all", "netease"]:
        result = await netease_api.search_songs(keyword, page, page_size)
        for song in result.get("songs", []):
            all_songs.append(SongSearchResult(
                id=0,
                title=song["title"],
                artist=song["artist"],
                album=song.get("album"),
                cover_url=song.get("cover_url"),
                source="netease",
                source_id=str(song["id"]),
                duration=song.get("duration"),
                has_lossless=True,
                quality_info={"lossless": True}
            ))
    
    if source in ["all", "qq"] and (source != "all" or len(all_songs) < page_size):
        qq_page = 1 if source == "all" else page
        result = await qq_music_api.search_songs(keyword, qq_page, page_size)
        for song in result.get("songs", []):
            all_songs.append(SongSearchResult(
                id=0,
                title=song["title"],
                artist=song["artist"],
                album=song.get("album"),
                cover_url=song.get("cover_url"),
                source="qq",
                source_id=str(song["id"]),
                duration=song.get("duration"),
                has_lossless=True,
                quality_info={"lossless": True}
            ))
    
    if source in ["all", "kugou"] and (source != "all" or len(all_songs) < page_size):
        kugou_page = 1 if source == "all" else page
        result = await kugou_music_api.search_songs(keyword, kugou_page, page_size)
        for song in result.get("songs", []):
            all_songs.append(SongSearchResult(
                id=0,
                title=song["title"],
                artist=song["artist"],
                album=song.get("album"),
                cover_url=song.get("cover_url"),
                source="kugou",
                source_id=str(song["id"]),
                duration=song.get("duration"),
                has_lossless=song.get("has_lossless", False),
                quality_info={"lossless": song.get("has_lossless", False)}
            ))
    
    # 如果是搜索全部，限制结果数量
    if source == "all":
        all_songs = all_songs[:page_size]
    
    return SearchResult(
        songs=all_songs,
        total=len(all_songs) if source != "all" else len(all_songs),
        page=page,
        page_size=page_size,
        has_more=len(all_songs) >= page_size
    )


@router.get("/song/{source}/{source_id}/url")
async def get_song_url(
    source: str,
    source_id: str,
    quality: str = Query("lossless", regex="^(standard|high|lossless|hires)$")
):
    """获取歌曲播放URL"""
    if source == "netease":
        result = await netease_api.get_song_url(int(source_id), quality)
    elif source == "qq":
        result = await qq_music_api.get_song_url(source_id, quality)
    elif source == "kugou":
        result = await kugou_music_api.get_song_url(source_id, quality)
    else:
        raise HTTPException(status_code=400, detail="不支持的平台")
    
    if not result or not result.get("url"):
        raise HTTPException(status_code=404, detail="无法获取歌曲链接，可能需要VIP或歌曲不存在")
    
    return result


@router.get("/song/{source}/{source_id}/lyric")
async def get_song_lyric(source: str, source_id: str):
    """获取歌词"""
    if source == "netease":
        result = await netease_api.get_song_lyric(int(source_id))
        return result
    else:
        # 其他平台歌词获取需要额外实现
        return {"lyric": "", "tlyric": ""}


@router.post("/download", response_model=DownloadTaskResponse)
async def create_download_task(
    download_data: DownloadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建下载任务"""
    # 获取歌曲信息
    song_info = {}
    source = download_data.source
    source_id = download_data.source_id
    
    if not source or not source_id:
        if download_data.song_id:
            song = db.query(Song).filter(Song.id == download_data.song_id).first()
            if song:
                source = song.source
                source_id = song.source_id
                song_info = {
                    "title": song.title,
                    "artist": song.artist,
                    "album": song.album
                }
        else:
            raise HTTPException(status_code=400, detail="需要提供歌曲ID或平台信息")
    
    if not source or not source_id:
        raise HTTPException(status_code=400, detail="无法确定歌曲信息")
    
    # 创建歌曲记录（如果不存在）
    if not download_data.song_id:
        song = db.query(Song).filter(
            Song.source == source,
            Song.source_id == source_id
        ).first()
        
        if not song:
            # 需要先获取歌曲信息
            if source == "netease":
                # 从搜索结果获取基本信息
                song = Song(
                    title="Unknown",
                    artist="Unknown",
                    source=source,
                    source_id=source_id
                )
            else:
                song = Song(
                    title="Unknown",
                    artist="Unknown",
                    source=source,
                    source_id=source_id
                )
            db.add(song)
            db.commit()
            db.refresh(song)
        
        song_id = song.id
    else:
        song_id = download_data.song_id
    
    # 创建下载任务
    task = DownloadTask(
        user_id=current_user.id,
        song_id=song_id,
        quality=download_data.quality,
        status="pending"
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 开始下载（实际项目中应该在后台任务中执行）
    task.status = "downloading"
    db.commit()
    
    # 执行下载
    if source == "netease":
        file_path = await download_service.download_from_netease(
            int(source_id), 
            song_info or {"title": "Unknown", "artist": "Unknown", "source": source},
            download_data.quality
        )
    elif source == "qq":
        file_path = await download_service.download_from_qq(
            source_id,
            song_info or {"title": "Unknown", "artist": "Unknown", "source": source},
            download_data.quality
        )
    elif source == "kugou":
        file_path = await download_service.download_from_kugou(
            source_id,
            song_info or {"title": "Unknown", "artist": "Unknown", "source": source},
            download_data.quality
        )
    else:
        file_path = None
    
    # 更新任务状态
    if file_path:
        task.status = "completed"
        song = db.query(Song).filter(Song.id == song_id).first()
        if song:
            song.local_path = str(file_path)
            song.quality = download_data.quality
    else:
        task.status = "failed"
        task.error_message = "下载失败"
    
    from datetime import datetime
    task.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    return task


@router.get("/download/tasks", response_model=List[DownloadTaskResponse])
async def get_download_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取下载任务列表"""
    tasks = db.query(DownloadTask).filter(
        DownloadTask.user_id == current_user.id
    ).order_by(DownloadTask.created_at.desc()).all()
    
    return tasks


@router.get("/download/task/{task_id}", response_model=DownloadTaskResponse)
async def get_download_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取下载任务详情"""
    task = db.query(DownloadTask).filter(
        DownloadTask.id == task_id,
        DownloadTask.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task


@router.get("/local")
async def get_local_songs():
    """获取本地已下载的歌曲"""
    songs = download_service.get_local_songs()
    return {"songs": songs, "total": len(songs)}


@router.delete("/local/{file_path:path}")
async def delete_local_song(file_path: str):
    """删除本地歌曲"""
    success = download_service.delete_song(file_path)
    
    if success:
        return {"message": "删除成功", "success": True}
    
    raise HTTPException(status_code=400, detail="删除失败")
