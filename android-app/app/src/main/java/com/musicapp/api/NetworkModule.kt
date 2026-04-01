package com.musicapp.api

import com.musicapp.model.LoginResponse
import com.musicapp.model.User
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

/**
 * 认证拦截器 - 自动添加Token到请求头
 */
class AuthInterceptor(
    private val tokenProvider: () -> String?
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val token = tokenProvider()
        val request = chain.request().newBuilder()
        
        token?.let {
            request.addHeader("Authorization", "Bearer $it")
        }
        
        return chain.proceed(request.build())
    }
}

/**
 * Retrofit配置模块
 */
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    
    // TODO: 替换为你的服务器地址
    private const val BASE_URL = "http://192.168.1.100:8000/"
    
    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(
                HttpLoggingInterceptor().apply {
                    level = HttpLoggingInterceptor.Level.BODY
                }
            )
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()
    }
    
    @Provides
    @Singleton
    fun provideAuthInterceptor(
        tokenManager: TokenManager
    ): AuthInterceptor {
        return AuthInterceptor { tokenManager.getToken() }
    }
    
    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
    
    @Provides
    @Singleton
    fun provideMusicApiService(retrofit: Retrofit): MusicApiService {
        return retrofit.create(MusicApiService::class.java)
    }
    
    @Provides
    @Singleton
    fun provideTokenManager(): TokenManager {
        return TokenManager()
    }
}

/**
 * Token管理器
 */
class TokenManager {
    private var token: String? = null
    
    fun saveToken(newToken: String) {
        token = newToken
    }
    
    fun getToken(): String? = token
    
    fun clearToken() {
        token = null
    }
    
    fun isLoggedIn(): Boolean = token != null
}
