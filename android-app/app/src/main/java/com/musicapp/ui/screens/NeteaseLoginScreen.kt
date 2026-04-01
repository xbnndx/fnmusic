package com.musicapp.ui.screens

import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.musicapp.repository.MusicRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import javax.inject.Inject

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NeteaseLoginScreen(
    onNavigateBack: () -> Unit,
    viewModel: NeteaseLoginViewModel = hiltViewModel()
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("网易云音乐登录") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "返回")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            when {
                viewModel.loginSuccess -> {
                    Icon(
                        imageVector = Icons.Default.Check,
                        contentDescription = null,
                        modifier = Modifier.size(64.dp),
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "登录成功！",
                        style = MaterialTheme.typography.titleLarge
                    )
                    Text(
                        text = "昵称: ${viewModel.nickname}",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
                viewModel.qrCodeUrl != null -> {
                    Text(
                        text = "请使用网易云音乐APP扫码登录",
                        style = MaterialTheme.typography.titleMedium
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    AndroidView(
                        factory = { context ->
                            WebView(context).apply {
                                webViewClient = WebViewClient()
                                settings.javaScriptEnabled = true
                                loadUrl(viewModel.qrCodeUrl!!)
                            }
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(400.dp)
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    viewModel.statusMessage?.let { message ->
                        Text(
                            text = message,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                viewModel.isLoading -> {
                    CircularProgressIndicator()
                    Text(
                        text = "正在获取登录二维码...",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
                else -> {
                    Button(onClick = { viewModel.getLoginQrCode() }) {
                        Text("获取登录二维码")
                    }
                }
            }
        }
    }
}

@HiltViewModel
class NeteaseLoginViewModel @Inject constructor(
    private val repository: MusicRepository
) : ViewModel() {
    
    var isLoading by mutableStateOf(false)
        private set
    
    var qrCodeUrl by mutableStateOf<String?>(null)
        private set
    
    var qrKey by mutableStateOf<String?>(null)
        private set
    
    var statusMessage by mutableStateOf<String?>(null)
        private set
    
    var loginSuccess by mutableStateOf(false)
        private set
    
    var nickname by mutableStateOf("")
        private set
    
    fun getLoginQrCode() {
        viewModelScope.launch {
            isLoading = true
            repository.getNeteaseLoginQrCode()
                .onSuccess { result ->
                    qrCodeUrl = result["qr_code_url"]
                    qrKey = result["key"]
                    startPolling()
                }
            isLoading = false
        }
    }
    
    private fun startPolling() {
        viewModelScope.launch {
            val key = qrKey ?: return@launch
            
            repeat(60) { // 最多轮询60次（5分钟）
                delay(5000) // 每5秒检查一次
                
                repository.checkNeteaseQrCodeStatus(key)
                    .onSuccess { result ->
                        when (result["status"]) {
                            "success" -> {
                                loginSuccess = true
                                nickname = (result["user"] as? Map<*, *>)?.get("nickname") as? String ?: ""
                                return@launch
                            }
                            "scanned" -> {
                                statusMessage = "已扫描，请在手机上确认登录"
                            }
                            "expired" -> {
                                statusMessage = "二维码已过期，请重新获取"
                                qrCodeUrl = null
                                return@launch
                            }
                        }
                    }
            }
        }
    }
}
