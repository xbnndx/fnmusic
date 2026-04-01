# Services模块
from app.services.netease_service import netease_api, NeteaseMusicAPI
from app.services.qqmusic_service import qq_music_api, QQMusicAPI
from app.services.kugou_service import kugou_music_api, KugouMusicAPI
from app.services.download_service import download_service, DownloadService

__all__ = [
    "netease_api", "NeteaseMusicAPI",
    "qq_music_api", "QQMusicAPI",
    "kugou_music_api", "KugouMusicAPI",
    "download_service", "DownloadService"
]
