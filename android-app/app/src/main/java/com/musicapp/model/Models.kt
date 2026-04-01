package com.musicapp.model

/**
 * 歌曲数据模型
 */
data class Song(
    val id: Int = 0,
    val title: String,
    val artist: String,
    val album: String? = null,
    val coverUrl: String? = null,
    val source: String, // netease, qq, kugou
    val sourceId: String,
    val duration: Int? = null,
    val quality: String? = null,
    val localPath: String? = null,
    val fileSize: Float? = null
)

/**
 * 歌单数据模型
 */
data class Playlist(
    val id: Int,
    val name: String,
    val description: String? = null,
    val coverUrl: String? = null,
    val source: String,
    val songCount: Int,
    val songs: List<Song> = emptyList()
)

/**
 * 下载任务
 */
data class DownloadTask(
    val id: Int,
    val songId: Int,
    val status: String, // pending, downloading, completed, failed
    val progress: Int,
    val quality: String,
    val errorMessage: String? = null
)

/**
 * 搜索结果
 */
data class SearchResult(
    val songs: List<Song>,
    val total: Int,
    val page: Int,
    val hasMore: Boolean
)

/**
 * 排行榜
 */
data class RankingList(
    val id: Int,
    val name: String,
    val source: String,
    val coverUrl: String? = null,
    val songCount: Int = 0
)

/**
 * 排行榜详情
 */
data class RankingDetail(
    val id: Int,
    val name: String,
    val source: String,
    val coverUrl: String? = null,
    val songs: List<RankedSong> = emptyList()
)

data class RankedSong(
    val rank: Int,
    val song: Song
)

/**
 * 每日推荐歌曲
 */
data class DailyRecommendSong(
    val song: Song,
    val reason: String? = null
)

/**
 * 用户信息
 */
data class User(
    val id: Int,
    val username: String,
    val neteaseUid: String? = null
)

/**
 * 网易云登录状态
 */
data class NeteaseLoginStatus(
    val loggedIn: Boolean,
    val userId: String? = null,
    val nickname: String? = null,
    val avatarUrl: String? = null
)

/**
 * 登录响应
 */
data class LoginResponse(
    val accessToken: String,
    val tokenType: String
)

/**
 * API响应包装
 */
data class ApiResponse<T>(
    val data: T? = null,
    val message: String? = null,
    val success: Boolean = true
)

/**
 * 歌曲URL信息
 */
data class SongUrlInfo(
    val url: String?,
    val size: Long? = null,
    val type: String? = null,
    val br: Int? = null,
    val quality: String
)
