package com.musicapp

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class App : Application() {
    
    override fun onCreate() {
        super.onCreate()
        // 初始化代码
    }
}
