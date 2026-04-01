package com.musicapp.repository

import com.musicapp.api.CreatePlaylistRequest
import com.musicapp.api.DownloadRequest
import com.musicapp.api.MusicApiService
import com.musicapp.api.TokenManager
import com.musicapp.model.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 音乐数据仓库
 */
@Singleton
class MusicRepository @Inject constructor(
    private val apiService: MusicApiService,
    private val tokenManager: TokenManager
) {
    
    // ============ 认证相关 ============
    
    suspend fun login(username: String, password: String): Result<LoginResponse> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.login(mapOf(
                "username" to username,
                "password" to password
            ))
            if (response.isSuccessful && response.body() != null) {
                tokenManager.saveToken(response.body()!!.accessToken)
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("登录失败: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun register(username: String, password: String): Result<User> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.register(mapOf(
                "username" to username,
                "password" to password
            ))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("注册失败: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    fun logout() {
        tokenManager.clearToken()
    }
    
    fun isLoggedIn(): Boolean = tokenManager.isLoggedIn()
    
    // ============ 搜索相关 ============
    
    suspend fun searchMusic(
        keyword: String,
        source: String = "all",
        page: Int = 1
    ): Result<SearchResult> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.searchMusic(keyword, source, page)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("搜索失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ============ 歌曲播放 ============
    
    suspend fun getSongUrl(
        source: String,
        sourceId: String,
        quality: String = "lossless"
    ): Result<SongUrlInfo> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getSongUrl(source, sourceId, quality)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("获取播放链接失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ============ 网易云音乐相关 ============
    
    suspend fun getNeteaseLoginQrCode(): Result<Map<String, String>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getNeteaseLoginQrCode()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("获取二维码失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun checkNeteaseQrCodeStatus(key: String): Result<Map<String, Any>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.checkNeteaseQrCodeStatus(key)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("检查状态失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getNeteaseLoginStatus(): Result<NeteaseLoginStatus> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getNeteaseLoginStatus()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("获取登录状态失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getDailyRecommend(): Result<List<DailyRecommendSong>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getDailyRecommend()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("获取每日推荐失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getNeteaseRankings(): Result<List<RankingList>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getNeteaseRankings()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("获取排行榜失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getNeteaseRankingDetail(rankingId: Int): Result<RankingDetail> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getNeteaseRankingDetail(rankingId)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("获取排行榜详情失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun importNeteasePlaylist(url: String): Result<Playlist> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.importNeteasePlaylist(mapOf("url" to url, "source" to "netease"))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("导入歌单失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ============ 歌单管理 ============
    
    suspend fun getPlaylists(): Result<List<Playlist>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getPlaylists()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("获取歌单失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun createPlaylist(name: String, description: String? = null): Result<Playlist> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.createPlaylist(CreatePlaylistRequest(name, description))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("创建歌单失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getPlaylist(playlistId: Int): Result<Playlist> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getPlaylist(playlistId)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("获取歌单失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ============ 下载相关 ============
    
    suspend fun downloadSong(
        source: String,
        sourceId: String,
        quality: String = "lossless"
    ): Result<DownloadTask> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.createDownloadTask(
                DownloadRequest(source = source, sourceId = sourceId, quality = quality)
            )
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("创建下载任务失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getDownloadTasks(): Result<List<DownloadTask>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getDownloadTasks()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("获取下载任务失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
