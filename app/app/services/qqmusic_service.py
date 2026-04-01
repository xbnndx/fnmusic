"""
QQ音乐API服务
"""
import httpx
import asyncio
import json
import re
import hashlib
from typing import Optional, List, Dict, Any
import time


class QQMusicAPI:
    """QQ音乐API"""
    
    def __init__(self):
        self.base_url = "https://c.y.qq.com"
        self.api_base = "https://u.y.qq.com/cgi-bin/musicu.fcg"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://y.qq.com/",
            "Cookie": "uin=; qm_keyst="
        }
    
    async def _request(self, params: dict) -> dict:
        """发送API请求"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.api_base,
                    params=params,
                    headers=self.headers,
                    timeout=30
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}
    
    def _get_sign(self, data: str) -> str:
        """生成签名（简化版）"""
        # QQ音乐的签名算法较复杂，这里使用简化版本
        return hashlib.md5(data.encode()).hexdigest()
    
    async def search_songs(self, keyword: str, page: int = 1, page_size: int = 20) -> dict:
        """搜索歌曲"""
        req_data = {
            "method": "DoSearchForQQMusicDesktop",
            "module": "music.search.SearchCgiService",
            "param": {
                "query": keyword,
                "search_type": 0,  # 0: 歌曲
                "num_per_page": page_size,
                "page_num": page
            }
        }
        
        params = {
            "data": json.dumps(req_data)
        }
        
        result = await self._request(params)
        
        if "search" in result.get("req_1", {}):
            data = result["req_1"]["search"]
            songs = data.get("body", {}).get("song", {}).get("list", [])
            total = data.get("body", {}).get("song", {}).get("totalnum", 0)
            
            return {
                "songs": [
                    {
                        "id": song.get("mid"),
                        "title": song.get("name"),
                        "artist": ", ".join([ar.get("name", "") for ar in song.get("singer", [])]),
                        "album": song.get("album", {}).get("name"),
                        "cover_url": f"https://y.gtimg.cn/music/photo_new/T002R300x300M000{song.get('album', {}).get('pmid', '')}.jpg",
                        "duration": song.get("interval", 0) * 1000
                    }
                    for song in songs
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "has_more": page * page_size < total
            }
        
        return {"songs": [], "total": 0, "page": page, "page_size": page_size, "has_more": False}
    
    async def get_song_url(self, song_mid: str, quality: str = "lossless") -> dict:
        """获取歌曲URL"""
        # 音质对应关系
        quality_map = {
            "standard": "M500",   # 128k MP3
            "high": "M800",       # 320k MP3
            "lossless": "A000",   # FLAC
            "hires": "RS01"       # Hi-Res
        }
        
        req_data = {
            "method": "CgiGetVkey",
            "module": "vkey.GetVkeyServer",
            "param": {
                "songmid_list": [song_mid],
                "songtype_list": [0],
                "guid": "0",
                "uin": "0",
                "loginflag": 0,
                "platform": "23",
                "filename_list": [f"{quality_map.get(quality, 'A000')}{song_mid}.{quality == 'lossless' and 'flac' or 'mp3'}"]
            }
        }
        
        params = {
            "data": json.dumps(req_data)
        }
        
        result = await self._request(params)
        
        if "req_0" in result:
            data = result["req_0"]["data"]
            mid_url_info = data.get("midurlinfo", [])
            sip = data.get("sip", [""])[0]
            
            if mid_url_info:
                url = mid_url_info[0].get("purl", "")
                if url:
                    return {
                        "url": sip + url,
                        "quality": quality
                    }
        
        return {}
    
    async def get_ranking_lists(self) -> List[dict]:
        """获取排行榜列表"""
        req_data = {
            "method": "GetAllTopList",
            "module": "MusicTopList.TopListInfoServer",
            "param": {}
        }
        
        params = {
            "data": json.dumps(req_data)
        }
        
        result = await self._request(params)
        
        if "topList" in result.get("req_1", {}).get("data", {}):
            lists = result["req_1"]["data"]["topList"]
            
            return [
                {
                    "id": lst.get("id"),
                    "name": lst.get("title"),
                    "cover_url": lst.get("headPicUrl") or lst.get("frontPicUrl"),
                    "play_count": lst.get("listenNum")
                }
                for lst in lists
            ]
        
        return []
    
    async def get_ranking_detail(self, top_id: int) -> dict:
        """获取排行榜详情"""
        req_data = {
            "method": "GetTopListInfo",
            "module": "MusicTopList.TopListInfoServer",
            "param": {
                "topid": top_id,
                "num": 100,
                "period": ""
            }
        }
        
        params = {
            "data": json.dumps(req_data)
        }
        
        result = await self._request(params)
        
        if "data" in result.get("req_1", {}):
            data = result["req_1"]["data"]
            songs = data.get("song", [])
            
            return {
                "id": data.get("topid"),
                "name": data.get("title"),
                "cover_url": data.get("headPicUrl"),
                "update_time": data.get("updateTime"),
                "songs": [
                    {
                        "rank": idx + 1,
                        "id": song.get("mid"),
                        "title": song.get("name"),
                        "artist": ", ".join([ar.get("name", "") for ar in song.get("singer", [])]),
                        "album": song.get("album", {}).get("name"),
                        "cover_url": song.get("album", {}).get("pmid") and f"https://y.gtimg.cn/music/photo_new/T002R300x300M000{song.get('album', {}).get('pmid')}.jpg"
                    }
                    for idx, song in enumerate(songs)
                ]
            }
        
        return {}


# 创建全局实例
qq_music_api = QQMusicAPI()
