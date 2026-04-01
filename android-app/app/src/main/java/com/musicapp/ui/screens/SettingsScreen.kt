package com.musicapp.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.musicapp.repository.MusicRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onNavigateBack: () -> Unit,
    onNavigateToNeteaseLogin: () -> Unit,
    onLogout: () -> Unit,
    viewModel: SettingsViewModel = hiltViewModel()
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("设置") },
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
                .padding(padding)
        ) {
            // 网易云音乐账号
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = "网易云音乐",
                                style = MaterialTheme.typography.titleMedium
                            )
                            Text(
                                text = if (viewModel.neteaseLoggedIn) 
                                    "已登录: ${viewModel.neteaseNickname}" 
                                else 
                                    "未登录",
                                style = MaterialTheme.typography.bodySmall,
                                color = if (viewModel.neteaseLoggedIn)
                                    MaterialTheme.colorScheme.primary
                                else
                                    MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        
                        Button(
                            onClick = onNavigateToNeteaseLogin
                        ) {
                            Text(if (viewModel.neteaseLoggedIn) "切换账号" else "登录")
                        }
                    }
                }
            }
            
            // 服务器设置
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "服务器设置",
                        style = MaterialTheme.typography.titleMedium
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedTextField(
                        value = viewModel.serverUrl,
                        onValueChange = { viewModel.serverUrl = it },
                        label = { Text("服务器地址") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true
                    )
                }
            }
            
            // 下载设置
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "下载设置",
                        style = MaterialTheme.typography.titleMedium
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    var selectedQuality by remember { mutableStateOf("lossless") }
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        listOf("standard", "high", "lossless").forEach { quality ->
                            FilterChip(
                                selected = selectedQuality == quality,
                                onClick = { selectedQuality = quality },
                                label = {
                                    Text(
                                        when(quality) {
                                            "standard" -> "标准"
                                            "high" -> "高品质"
                                            "lossless" -> "无损"
                                            else -> quality
                                        }
                                    )
                                }
                            )
                        }
                    }
                }
            }
            
            Spacer(modifier = Modifier.weight(1f))
            
            // 登出按钮
            Button(
                onClick = onLogout,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.error
                )
            ) {
                Icon(Icons.Default.Logout, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("退出登录")
            }
        }
    }
}

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val repository: MusicRepository
) : ViewModel() {
    
    var neteaseLoggedIn by mutableStateOf(false)
        private set
    
    var neteaseNickname by mutableStateOf("")
        private set
    
    var serverUrl by mutableStateOf("http://192.168.1.100:8000/")
    
    init {
        checkNeteaseLogin()
    }
    
    fun checkNeteaseLogin() {
        viewModelScope.launch {
            repository.getNeteaseLoginStatus()
                .onSuccess { status ->
                    neteaseLoggedIn = status.loggedIn
                    neteaseNickname = status.nickname ?: ""
                }
        }
    }
}
