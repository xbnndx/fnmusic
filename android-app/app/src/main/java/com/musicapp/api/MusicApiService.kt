package com.musicapp.api

import com.musicapp.model.*
import retrofit2.Response
import retrofit2.http.*

/**
 * 音乐API接口
 */
interface MusicApiService {
    
    // ============ 认证相关 ============
    
    @POST("api/auth/register")
    suspend fun register(@Body request: Map<String, String>): Response<User>
    
    @POST("api/auth/login")
    suspend fun login(@Body request: Map<String, String>): Response<LoginResponse>
    
    @GET("api/auth/me")
    suspend fun getCurrentUser(): Response<User>
    
    // ============ 网易云音乐相关 ============
    
    @GET("api/netease/login/qrcode")
    suspend fun getNeteaseLoginQrCode(): Response<Map<String, String>>
    
    @GET("api/netease/login/qrcode/status")
    suspend fun checkNeteaseQrCodeStatus(@Query("key") key: String): Response<Map<String, Any>>
    
    @POST("api/netease/login/callback")
    suspend fun neteaseLoginCallback(@Body cookie: Map<String, String>): Response<Map<String, Any>>
    
    @GET("api/netease/login/status")
    suspend fun getNeteaseLoginStatus(): Response<NeteaseLoginStatus>
    
    @GET("api/netease/daily-recommend")
    suspend fun getDailyRecommend(): Response<List<DailyRecommendSong>>
    
    @GET("api/netease/rankings")
    suspend fun getNeteaseRankings(): Response<List<RankingList>>
    
    @GET("api/netease/rankings/{rankingId}")
    suspend fun getNeteaseRankingDetail(@Path("rankingId") rankingId: Int): Response<RankingDetail>
    
    @POST("api/netease/playlist/import")
    suspend fun importNeteasePlaylist(@Body request: Map<String, String>): Response<Playlist>
    
    @POST("api/netease/playlist/download")
    suspend fun downloadNeteasePlaylist(
        @Query("playlist_id") playlistId: Int,
        @Query("quality") quality: String = "lossless"
    ): Response<Map<String, Any>>
    
    // ============ 音乐搜索和下载 ============
    
    @GET("api/music/search")
    suspend fun searchMusic(
        @Query("keyword") keyword: String,
        @Query("source") source: String = "all",
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 20
    ): Response<SearchResult>
    
    @GET("api/music/song/{source}/{sourceId}/url")
    suspend fun getSongUrl(
        @Path("source") source: String,
        @Path("sourceId") sourceId: String,
        @Query("quality") quality: String = "lossless"
    ): Response<SongUrlInfo>
    
    @GET("api/music/song/{source}/{sourceId}/lyric")
    suspend fun getSongLyric(
        @Path("source") source: String,
        @Path("sourceId") sourceId: String
    ): Response<Map<String, String>>
    
    @POST("api/music/download")
    suspend fun createDownloadTask(@Body request: DownloadRequest): Response<DownloadTask>
    
    @GET("api/music/download/tasks")
    suspend fun getDownloadTasks(): Response<List<DownloadTask>>
    
    @GET("api/music/download/task/{taskId}")
    suspend fun getDownloadTask(@Path("taskId") taskId: Int): Response<DownloadTask>
    
    @GET("api/music/local")
    suspend fun getLocalSongs(): Response<Map<String, Any>>
    
    // ============ 歌单管理 ============
    
    @GET("api/playlists")
    suspend fun getPlaylists(): Response<List<Playlist>>
    
    @POST("api/playlists")
    suspend fun createPlaylist(@Body request: CreatePlaylistRequest): Response<Playlist>
    
    @GET("api/playlists/{playlistId}")
    suspend fun getPlaylist(@Path("playlistId") playlistId: Int): Response<Playlist>
    
    @PUT("api/playlists/{playlistId}")
    suspend fun updatePlaylist(
        @Path("playlistId") playlistId: Int,
        @Body request: CreatePlaylistRequest
    ): Response<Playlist>
    
    @DELETE("api/playlists/{playlistId}")
    suspend fun deletePlaylist(@Path("playlistId") playlistId: Int): Response<Map<String, Any>>
    
    @POST("api/playlists/{playlistId}/songs/{songId}")
    suspend fun addSongToPlaylist(
        @Path("playlistId") playlistId: Int,
        @Path("songId") songId: Int
    ): Response<Map<String, Any>>
    
    @DELETE("api/playlists/{playlistId}/songs/{songId}")
    suspend fun removeSongFromPlaylist(
        @Path("playlistId") playlistId: Int,
        @Path("songId") songId: Int
    ): Response<Map<String, Any>>
}

// 辅助数据类
data class DownloadRequest(
    val songId: Int? = null,
    val source: String? = null,
    val sourceId: String? = null,
    val quality: String = "lossless"
)

data class CreatePlaylistRequest(
    val name: String,
    val description: String? = null,
    val source: String? = "local"
)
