"""
歌单管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models import get_db, User, Playlist, Song, PlaylistSong
from app.schemas import PlaylistCreate, PlaylistResponse, PlaylistDetail, SongResponse, MessageResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/playlists", tags=["歌单"])


@router.get("", response_model=List[PlaylistResponse])
async def get_playlists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的所有歌单"""
    playlists = db.query(Playlist).filter(
        Playlist.user_id == current_user.id
    ).order_by(Playlist.created_at.desc()).all()
    
    return playlists


@router.post("", response_model=PlaylistResponse)
async def create_playlist(
    playlist_data: PlaylistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新歌单"""
    playlist = Playlist(
        user_id=current_user.id,
        name=playlist_data.name,
        description=playlist_data.description,
        source=playlist_data.source or "local"
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    
    return playlist


@router.get("/{playlist_id}", response_model=PlaylistDetail)
async def get_playlist(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取歌单详情"""
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.user_id == current_user.id
    ).first()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    
    # 获取歌曲列表
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


@router.put("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: int,
    playlist_data: PlaylistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新歌单信息"""
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.user_id == current_user.id
    ).first()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    
    playlist.name = playlist_data.name
    playlist.description = playlist_data.description
    db.commit()
    db.refresh(playlist)
    
    return playlist


@router.delete("/{playlist_id}", response_model=MessageResponse)
async def delete_playlist(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除歌单"""
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.user_id == current_user.id
    ).first()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    
    db.delete(playlist)
    db.commit()
    
    return {"message": "删除成功", "success": True}


@router.post("/{playlist_id}/songs/{song_id}", response_model=MessageResponse)
async def add_song_to_playlist(
    playlist_id: int,
    song_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加歌曲到歌单"""
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.user_id == current_user.id
    ).first()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    
    # 检查是否已存在
    existing = db.query(PlaylistSong).filter(
        PlaylistSong.playlist_id == playlist_id,
        PlaylistSong.song_id == song_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="歌曲已在歌单中")
    
    # 添加歌曲
    max_order = db.query(PlaylistSong).filter(
        PlaylistSong.playlist_id == playlist_id
    ).count()
    
    playlist_song = PlaylistSong(
        playlist_id=playlist_id,
        song_id=song_id,
        sort_order=max_order
    )
    db.add(playlist_song)
    
    # 更新歌曲数量
    playlist.song_count += 1
    db.commit()
    
    return {"message": "添加成功", "success": True}


@router.delete("/{playlist_id}/songs/{song_id}", response_model=MessageResponse)
async def remove_song_from_playlist(
    playlist_id: int,
    song_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """从歌单移除歌曲"""
    playlist_song = db.query(PlaylistSong).filter(
        PlaylistSong.playlist_id == playlist_id,
        PlaylistSong.song_id == song_id
    ).first()
    
    if not playlist_song:
        raise HTTPException(status_code=404, detail="歌曲不在歌单中")
    
    db.delete(playlist_song)
    
    # 更新歌曲数量
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if playlist:
        playlist.song_count -= 1
    
    db.commit()
    
    return {"message": "移除成功", "success": True}
