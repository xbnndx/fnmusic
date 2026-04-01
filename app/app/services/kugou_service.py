"""
酷狗音乐API服务
"""
import httpx
import asyncio
import json
import re
import hashlib
from typing import Optional, List, Dict, Any
import time


class KugouMusicAPI:
    """酷狗音乐API"""
    
    def __init__(self):
        self.base_url = "https://www.kugou.com"
        self.api_base = "https://complexsearch.kugou.com"
        self.mobile_api = "https://m.kugou.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.kugou.com/"
        }
    
    async def _request(self, url: str, params: dict, method: str = "GET") -> dict:
        """发送API请求"""
        async with httpx.AsyncClient() as client:
            try:
                if method == "GET":
                    response = await client.get(url, params=params, headers=self.headers, timeout=30)
                else:
                    response = await client.post(url, data=params, headers=self.headers, timeout=30)
                
                # 尝试解析JSON
                try:
                    return response.json()
                except:
                    return {"raw_text": response.text}
            except Exception as e:
                return {"error": str(e)}
    
    async def search_songs(self, keyword: str, page: int = 1, page_size: int = 20) -> dict:
        """搜索歌曲"""
        url = "https://complexsearch.kugou.com/v2/search/song"
        params = {
            "keyword": keyword,
            "page": page,
            "pagesize": page_size,
            "platform": "WebFilter",
            "format": "json"
        }
        
        result = await self._request(url, params)
        
        if result.get("status") == 1 or "data" in result:
            data = result.get("data", {})
            songs = data.get("lists", [])
            total = data.get("total", 0)
            
            return {
                "songs": [
                    {
                        "id": song.get("FileHash"),
                        "title": song.get("SongName"),
                        "artist": song.get("SingerName"),
                        "album": song.get("AlbumName"),
                        "cover_url": song.get("Image"),
                        "duration": song.get("Duration", 0) * 1000,
                        "has_lossless": song.get("SQFileHash", "") != ""  # 是否有无损
                    }
                    for song in songs
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "has_more": page * page_size < total
            }
        
        return {"songs": [], "total": 0, "page": page, "page_size": page_size, "has_more": False}
    
    async def get_song_url(self, song_hash: str, quality: str = "lossless") -> dict:
        """获取歌曲URL"""
        # 音质对应：standard, high, lossless, hires
        quality_map = {
            "standard": {"hash": song_hash, "album_audio_id": 0},
            "high": {"hash": song_hash, "album_audio_id": 0},
            "lossless": {"hash": song_hash, "album_audio_id": 0},
            "hires": {"hash": song_hash, "album_audio_id": 0}
        }
        
        # 先获取歌曲信息，找到对应品质的hash
        url = "https://wwwapi.kugou.com/yy/index.php"
        params = {
            "r": "play/getdata",
            "hash": song_hash,
            "format": "json"
        }
        
        result = await self._request(url, params)
        
        if result.get("status") == 1:
            data = result.get("data", {})
            
            # 根据品质选择不同的hash
            if quality == "lossless" and data.get("sq_hash"):
                song_hash = data["sq_hash"]
            elif quality == "hires" and data.get("res_hash"):
                song_hash = data["res_hash"]
            elif quality == "high" and data.get("320_hash"):
                song_hash = data["320_hash"]
            
            # 重新请求获取播放链接
            params["hash"] = song_hash
            result = await self._request(url, params)
            
            if result.get("status") == 1:
                data = result.get("data", {})
                return {
                    "url": data.get("play_url"),
                    "size": data.get("filesize"),
                    "quality": quality,
                    "format": data.get("extension", "mp3")
                }
        
        return {}
    
    async def get_song_detail(self, song_hash: str) -> dict:
        """获取歌曲详情"""
        url = "https://wwwapi.kugou.com/yy/index.php"
        params = {
            "r": "play/getdata",
            "hash": song_hash,
            "format": "json"
        }
        
        result = await self._request(url, params)
        
        if result.get("status") == 1:
            data = result.get("data", {})
            return {
                "id": data.get("hash"),
                "title": data.get("song_name"),
                "artist": data.get("author_name"),
                "album": data.get("album_name"),
                "cover_url": data.get("img"),
                "duration": data.get("timelength", 0),
                "play_url": data.get("play_url"),
                "lyrics": data.get("lyrics", "")
            }
        
        return {}
    
    async def get_ranking_lists(self) -> List[dict]:
        """获取排行榜列表"""
        url = "https://www.kugou.com/yy/rank/home"
        params = {
            "format": "json"
        }
        
        result = await self._request(url, params)
        
        # 简化处理，返回常见的榜单
        default_lists = [
            {"id": 8888, "name": "酷狗TOP500", "cover_url": "https://webfs.tx.kugou.com/rank/1.jpg"},
            {"id": 31373, "name": "飙升榜", "cover_url": "https://webfs.tx.kugou.com/rank/2.jpg"},
            {"id": 6666, "name": "热歌榜", "cover_url": "https://webfs.tx.kugou.com/rank/3.jpg"},
        ]
        
        return default_lists
    
    async def get_ranking_detail(self, rank_id: int) -> dict:
        """获取排行榜详情"""
        url = "https://wwwapi.kugou.com/yy/rank/playdata"
        params = {
            "rankid": rank_id,
            "page": 1,
            "pagesize": 100,
            "format": "json"
        }
        
        result = await self._request(url, params)
        
        if result.get("status") == 1:
            data = result.get("data", {})
            songs = data.get("info", [])
            
            return {
                "id": rank_id,
                "name": data.get("rankname", ""),
                "songs": [
                    {
                        "rank": idx + 1,
                        "id": song.get("hash"),
                        "title": song.get("songname"),
                        "artist": song.get("singername"),
                        "album": song.get("album_name"),
                        "cover_url": f"https://webfs.tx.kugou.com/{song.get('img')}"
                    }
                    for idx, song in enumerate(songs)
                ]
            }
        
        return {}
    
    async def download_song(self, song_hash: str, quality: str = "lossless") -> Optional[str]:
        """获取下载链接"""
        result = await self.get_song_url(song_hash, quality)
        return result.get("url")


# 创建全局实例
kugou_music_api = KugouMusicAPI()
