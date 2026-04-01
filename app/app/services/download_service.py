"""
音乐下载服务
"""
import os
import asyncio
import aiohttp
import aiofiles
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import logging

from app.core.config import settings
from app.services.netease_service import netease_api
from app.services.qqmusic_service import qq_music_api
from app.services.kugou_service import kugou_music_api

logger = logging.getLogger(__name__)


class DownloadService:
    """音乐下载服务"""
    
    def __init__(self):
        self.music_dir = Path(settings.MUSIC_DIR)
        self.music_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, song_info: dict, quality: str) -> Path:
        """生成文件保存路径"""
        artist = song_info.get("artist", "Unknown")
        title = song_info.get("title", "Unknown")
        source = song_info.get("source", "unknown")
        
        # 清理文件名中的非法字符
        safe_artist = "".join(c for c in artist if c.isalnum() or c in (' ', '-', '_'))[:50]
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:50]
        
        # 确定文件扩展名
        ext = "flac" if quality == "lossless" else "mp3"
        
        # 创建目录结构: music/{source}/{artist}/{title}.{ext}
        dir_path = self.music_dir / source / safe_artist
        dir_path.mkdir(parents=True, exist_ok=True)
        
        file_name = f"{safe_title}.{ext}"
        return dir_path / file_name
    
    async def download_from_netease(
        self, 
        song_id: int, 
        song_info: dict, 
        quality: str = "lossless",
        progress_callback=None
    ) -> Optional[Path]:
        """从网易云音乐下载"""
        try:
            # 获取下载链接
            url_info = await netease_api.get_song_url(song_id, quality)
            url = url_info.get("url")
            
            if not url:
                logger.error(f"Failed to get download URL for song {song_id}")
                return None
            
            # 生成保存路径
            file_path = self._get_file_path({**song_info, "source": "netease"}, quality)
            
            # 下载文件
            return await self._download_file(url, file_path, progress_callback)
            
        except Exception as e:
            logger.error(f"Error downloading from Netease: {e}")
            return None
    
    async def download_from_qq(
        self, 
        song_mid: str, 
        song_info: dict, 
        quality: str = "lossless",
        progress_callback=None
    ) -> Optional[Path]:
        """从QQ音乐下载"""
        try:
            # 获取下载链接
            url_info = await qq_music_api.get_song_url(song_mid, quality)
            url = url_info.get("url")
            
            if not url:
                logger.error(f"Failed to get download URL for song {song_mid}")
                return None
            
            # 生成保存路径
            file_path = self._get_file_path({**song_info, "source": "qq"}, quality)
            
            return await self._download_file(url, file_path, progress_callback)
            
        except Exception as e:
            logger.error(f"Error downloading from QQ Music: {e}")
            return None
    
    async def download_from_kugou(
        self, 
        song_hash: str, 
        song_info: dict, 
        quality: str = "lossless",
        progress_callback=None
    ) -> Optional[Path]:
        """从酷狗音乐下载"""
        try:
            # 获取下载链接
            url_info = await kugou_music_api.get_song_url(song_hash, quality)
            url = url_info.get("url")
            
            if not url:
                logger.error(f"Failed to get download URL for song {song_hash}")
                return None
            
            # 生成保存路径
            file_path = self._get_file_path({**song_info, "source": "kugou"}, quality)
            
            return await self._download_file(url, file_path, progress_callback)
            
        except Exception as e:
            logger.error(f"Error downloading from Kugou: {e}")
            return None
    
    async def _download_file(
        self, 
        url: str, 
        file_path: Path, 
        progress_callback=None
    ) -> Optional[Path]:
        """通用文件下载"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"Download failed with status {response.status}")
                        return None
                    
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 回调进度
                            if progress_callback and total_size > 0:
                                progress = int((downloaded / total_size) * 100)
                                await progress_callback(progress)
                    
                    logger.info(f"Downloaded: {file_path}")
                    return file_path
                    
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            if file_path.exists():
                file_path.unlink()
            return None
    
    async def download_playlist(
        self,
        songs: list,
        source: str = "netease",
        quality: str = "lossless",
        progress_callback=None
    ) -> Dict[str, Any]:
        """批量下载歌单"""
        results = {
            "success": [],
            "failed": []
        }
        
        for idx, song in enumerate(songs):
            song_id = song.get("id") or song.get("source_id")
            song_info = {
                "title": song.get("title") or song.get("name"),
                "artist": song.get("artist") or song.get("singer"),
                "album": song.get("album"),
                "source": source
            }
            
            # 根据来源选择下载方法
            if source == "netease":
                file_path = await self.download_from_netease(song_id, song_info, quality)
            elif source == "qq":
                file_path = await self.download_from_qq(song_id, song_info, quality)
            elif source == "kugou":
                file_path = await self.download_from_kugou(song_id, song_info, quality)
            else:
                file_path = None
            
            if file_path:
                results["success"].append({
                    "song": song_info,
                    "path": str(file_path)
                })
            else:
                results["failed"].append(song_info)
            
            # 总体进度回调
            if progress_callback:
                await progress_callback(idx + 1, len(songs), song_info, file_path is not None)
            
            # 避免请求过快
            await asyncio.sleep(0.5)
        
        return results
    
    def get_local_songs(self) -> list:
        """获取本地已下载的歌曲"""
        songs = []
        
        for source_dir in self.music_dir.iterdir():
            if not source_dir.is_dir():
                continue
            
            source = source_dir.name
            
            for artist_dir in source_dir.iterdir():
                if not artist_dir.is_dir():
                    continue
                
                artist = artist_dir.name
                
                for song_file in artist_dir.iterdir():
                    if song_file.suffix.lower() in [".mp3", ".flac", ".m4a", ".wav"]:
                        songs.append({
                            "title": song_file.stem,
                            "artist": artist,
                            "source": source,
                            "path": str(song_file),
                            "size": song_file.stat().st_size / (1024 * 1024)  # MB
                        })
        
        return songs
    
    def delete_song(self, file_path: str) -> bool:
        """删除本地歌曲"""
        try:
            path = Path(file_path)
            if path.exists() and path.is_relative_to(self.music_dir):
                path.unlink()
                logger.info(f"Deleted: {file_path}")
                return True
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
        return False


# 创建全局实例
download_service = DownloadService()
