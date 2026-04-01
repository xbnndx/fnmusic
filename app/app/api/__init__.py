# API模块
from app.api.auth import router as auth_router
from app.api.netease import router as netease_router
from app.api.music import router as music_router
from app.api.playlists import router as playlists_router

__all__ = ["auth_router", "netease_router", "music_router", "playlists_router"]
