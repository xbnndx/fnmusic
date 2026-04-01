"""
网易云音乐API服务
基于 https://github.com/Binaryify/NeteaseCloudMusicApi 的接口实现
"""
import httpx
import asyncio
import json
import re
import time
import hashlib
import base64
import os
from typing import Optional, List, Dict, Any
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from urllib.parse import urlencode
import random


class NeteaseMusicAPI:
    """网易云音乐API"""
    
    def __init__(self):
        self.base_url = "https://music.163.com"
        self.api_base = "https://music.163.com/weapi"
        self.cookie = ""
        
        # 加密相关常量
        self.aes_key = b"0CoJUm6Qyw8W8jud"
        self.aes_iv = b"0102030405060708"
        self.public_key = "010001"
        self.modulus = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685667daafb4d1b67f8b625a2c7a12b712a0e02e3e1d0efb2a5a7c0a3b3a0a5e5a7b8c9d0e1f2a3b4c5d6"
        self.chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    def set_cookie(self, cookie: str):
        """设置登录Cookie"""
        self.cookie = cookie
    
    def _create_secret_key(self, length: int = 16) -> str:
        """生成随机密钥"""
        return ''.join(random.choice(self.chars) for _ in range(length))
    
    def _aes_encrypt(self, data: str, key: bytes, iv: bytes) -> str:
        """AES加密"""
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(data.encode(), AES.block_size))
        return base64.b64encode(encrypted).decode()
    
    def _rsa_encrypt(self, data: str) -> str:
        """RSA加密"""
        # 简化的RSA加密实现
        text = data[::-1]
        result = pow(int(text.encode().hex(), 16), int(self.public_key, 16), int(self.modulus, 16))
        return format(result, 'x')
    
    def _encrypt_params(self, params: dict) -> dict:
        """加密请求参数"""
        json_str = json.dumps(params)
        random_key = self._create_secret_key(16)
        
        # 两层AES加密
        params_encrypted = self._aes_encrypt(json_str, self.aes_key, self.aes_iv)
        params_encrypted = self._aes_encrypt(params_encrypted, random_key.encode(), self.aes_iv)
        
        # RSA加密密钥
        key_encrypted = self._rsa_encrypt(random_key)
        
        return {
            "params": params_encrypted,
            "encSecKey": key_encrypted
        }
    
    async def _request(self, endpoint: str, params: dict, method: str = "POST") -> dict:
        """发送API请求"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://music.163.com",
            "Cookie": self.cookie,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        encrypted = self._encrypt_params(params)
        
        async with httpx.AsyncClient() as client:
            try:
                if method == "POST":
                    response = await client.post(url, data=encrypted, headers=headers, timeout=30)
                else:
                    response = await client.get(url, params=params, headers=headers, timeout=30)
                
                return response.json()
            except Exception as e:
                return {"error": str(e)}
    
    async def login_by_qr_code(self) -> dict:
        """获取二维码登录"""
        # 获取二维码key
        url = f"{self.base_url}/api/login/qrcode/unikey"
        params = {"type": 1}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                params=params,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://music.163.com"
                }
            )
            data = response.json()
            
            if data.get("code") == 200:
                key = data.get("unikey")
                qr_url = f"https://music.163.com/login?codekey={key}"
                return {
                    "key": key,
                    "qr_code_url": qr_url
                }
        
        return {"error": "Failed to get QR code"}
    
    async def check_qr_code_status(self, key: str) -> dict:
        """检查二维码扫码状态"""
        url = f"{self.base_url}/api/login/qrcode/client/login"
        params = {"key": key, "type": 1}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                params=params,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://music.163.com"
                }
            )
            data = response.json()
            
            if data.get("code") == 803:  # 登录成功
                # 获取cookie
                cookies = response.cookies
                cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
                return {
                    "status": "success",
                    "cookie": cookie_str,
                    "user": data.get("profile", {})
                }
            elif data.get("code") == 800:
                return {"status": "expired"}
            elif data.get("code") == 801:
                return {"status": "waiting"}
            elif data.get("code") == 802:
                return {"status": "scanned"}
            
            return {"status": "unknown"}
    
    async def login_by_phone(self, phone: str, password: str) -> dict:
        """手机号登录"""
        # 密码MD5加密
        password_md5 = hashlib.md5(password.encode()).hexdigest()
        
        params = {
            "phone": phone,
            "password": password_md5,
            "rememberLogin": "true"
        }
        
        result = await self._request("/weapi/login/cellphone", params)
        
        if result.get("code") == 200:
            return {
                "status": "success",
                "user": result.get("profile", {}),
                "cookie": result.get("cookie", "")
            }
        
        return {
            "status": "failed",
            "message": result.get("msg", "登录失败")
        }
    
    async def login_by_email(self, email: str, password: str) -> dict:
        """邮箱登录"""
        password_md5 = hashlib.md5(password.encode()).hexdigest()
        
        params = {
            "username": email,
            "password": password_md5,
            "rememberLogin": "true"
        }
        
        result = await self._request("/weapi/login", params)
        
        if result.get("code") == 200:
            return {
                "status": "success",
                "user": result.get("profile", {}),
                "cookie": result.get("cookie", "")
            }
        
        return {
            "status": "failed",
            "message": result.get("msg", "登录失败")
        }
    
    async def get_login_status(self) -> dict:
        """获取登录状态"""
        params = {}
        result = await self._request("/weapi/w/nuser/account/get", params)
        
        if result.get("code") == 200 and result.get("profile"):
            return {
                "logged_in": True,
                "user": result.get("profile", {})
            }
        
        return {
            "logged_in": False,
            "user": None
        }
    
    async def get_daily_recommend_songs(self) -> List[dict]:
        """获取每日推荐歌曲"""
        params = {}
        result = await self._request("/weapi/v3/discovery/recommend/songs", params)
        
        if result.get("code") == 200:
            songs = result.get("data", {}).get("dailySongs", [])
            return [
                {
                    "id": song.get("id"),
                    "title": song.get("name"),
                    "artist": ", ".join([ar.get("name", "") for ar in song.get("ar", [])]),
                    "album": song.get("al", {}).get("name"),
                    "cover_url": song.get("al", {}).get("picUrl"),
                    "duration": song.get("dt"),
                    "reason": song.get("recommendReason", "")
                }
                for song in songs
            ]
        
        return []
    
    async def get_playlist_detail(self, playlist_id: str) -> dict:
        """获取歌单详情"""
        params = {
            "id": playlist_id,
            "n": 100000,
            "s": 8
        }
        
        result = await self._request("/weapi/v3/playlist/detail", params)
        
        if result.get("code") == 200:
            playlist = result.get("playlist", {})
            tracks = playlist.get("tracks", [])
            
            return {
                "id": playlist.get("id"),
                "name": playlist.get("name"),
                "description": playlist.get("description"),
                "cover_url": playlist.get("coverImgUrl"),
                "play_count": playlist.get("playCount"),
                "song_count": playlist.get("trackCount"),
                "songs": [
                    {
                        "id": song.get("id"),
                        "title": song.get("name"),
                        "artist": ", ".join([ar.get("name", "") for ar in song.get("ar", [])]),
                        "album": song.get("al", {}).get("name"),
                        "cover_url": song.get("al", {}).get("picUrl"),
                        "duration": song.get("dt")
                    }
                    for song in tracks
                ]
            }
        
        return {}
    
    def extract_playlist_id(self, url: str) -> Optional[str]:
        """从URL提取歌单ID"""
        patterns = [
            r'playlist[?/]id=(\d+)',
            r'playlist[?/](\d+)',
            r'[?&]id=(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def get_ranking_lists(self) -> List[dict]:
        """获取所有排行榜"""
        params = {}
        result = await self._request("/weapi/toplist", params)
        
        if result.get("code") == 200:
            lists = result.get("list", [])
            return [
                {
                    "id": lst.get("id"),
                    "name": lst.get("name"),
                    "cover_url": lst.get("coverImgUrl"),
                    "update_frequency": lst.get("updateFrequency"),
                    "play_count": lst.get("playCount")
                }
                for lst in lists
            ]
        
        return []
    
    async def get_ranking_detail(self, ranking_id: int) -> dict:
        """获取排行榜详情"""
        params = {
            "id": ranking_id,
            "n": 100
        }
        
        result = await self._request("/weapi/playlist/detail", params)
        
        if result.get("code") == 200:
            playlist = result.get("playlist", {})
            tracks = playlist.get("tracks", [])
            
            return {
                "id": playlist.get("id"),
                "name": playlist.get("name"),
                "cover_url": playlist.get("coverImgUrl"),
                "songs": [
                    {
                        "rank": idx + 1,
                        "id": song.get("id"),
                        "title": song.get("name"),
                        "artist": ", ".join([ar.get("name", "") for ar in song.get("ar", [])]),
                        "album": song.get("al", {}).get("name"),
                        "cover_url": song.get("al", {}).get("picUrl"),
                        "duration": song.get("dt")
                    }
                    for idx, song in enumerate(tracks)
                ]
            }
        
        return {}
    
    async def search_songs(self, keyword: str, page: int = 1, page_size: int = 20) -> dict:
        """搜索歌曲"""
        params = {
            "s": keyword,
            "type": 1,  # 1: 单曲
            "offset": (page - 1) * page_size,
            "limit": page_size
        }
        
        result = await self._request("/weapi/search/get", params)
        
        if result.get("code") == 200:
            songs = result.get("result", {}).get("songs", [])
            song_count = result.get("result", {}).get("songCount", 0)
            
            return {
                "songs": [
                    {
                        "id": song.get("id"),
                        "title": song.get("name"),
                        "artist": ", ".join([ar.get("name", "") for ar in song.get("ar", [])]),
                        "album": song.get("al", {}).get("name"),
                        "cover_url": song.get("al", {}).get("picUrl"),
                        "duration": song.get("dt")
                    }
                    for song in songs
                ],
                "total": song_count,
                "page": page,
                "page_size": page_size,
                "has_more": page * page_size < song_count
            }
        
        return {"songs": [], "total": 0, "page": page, "page_size": page_size, "has_more": False}
    
    async def get_song_url(self, song_id: int, quality: str = "lossless") -> dict:
        """获取歌曲播放URL"""
        # 音质对应：standard(128k), high(320k), lossless(flac)
        quality_map = {
            "standard": "standard",
            "high": "exhigh",
            "lossless": "lossless",
            "hires": "hires"
        }
        
        params = {
            "ids": f"[{song_id}]",
            "level": quality_map.get(quality, "lossless"),
            "encodeType": "flac" if quality == "lossless" else "mp3"
        }
        
        result = await self._request("/weapi/song/enhance/player/url/v1", params)
        
        if result.get("code") == 200:
            data = result.get("data", [])
            if data:
                song_data = data[0]
                return {
                    "url": song_data.get("url"),
                    "size": song_data.get("size"),
                    "type": song_data.get("type"),
                    "br": song_data.get("br"),
                    "quality": quality
                }
        
        return {}
    
    async def get_song_lyric(self, song_id: int) -> dict:
        """获取歌词"""
        params = {"id": song_id}
        result = await self._request("/weapi/song/lyric", params)
        
        if result.get("code") == 200:
            return {
                "lyric": result.get("lrc", {}).get("lyric", ""),
                "tlyric": result.get("tlyric", {}).get("lyric", "")
            }
        
        return {"lyric": "", "tlyric": ""}


# 创建全局实例
netease_api = NeteaseMusicAPI()
