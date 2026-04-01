package com.musicapp.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.musicapp.model.DownloadTask
import com.musicapp.repository.MusicRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DownloadsScreen(
    onNavigateBack: () -> Unit,
    viewModel: DownloadsViewModel = hiltViewModel()
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("下载管理") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "返回")
                    }
                }
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            items(viewModel.tasks) { task ->
                DownloadTaskItem(task = task)
            }
        }
    }
}

@Composable
fun DownloadTaskItem(task: DownloadTask) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "歌曲ID: ${task.songId}",
                    style = MaterialTheme.typography.titleSmall
                )
                Text(
                    text = when(task.status) {
                        "pending" -> "等待中"
                        "downloading" -> "下载中"
                        "completed" -> "已完成"
                        "failed" -> "失败"
                        else -> task.status
                    },
                    style = MaterialTheme.typography.labelMedium,
                    color = when(task.status) {
                        "completed" -> MaterialTheme.colorScheme.primary
                        "failed" -> MaterialTheme.colorScheme.error
                        else -> MaterialTheme.colorScheme.onSurfaceVariant
                    }
                )
            }
            
            if (task.status == "downloading") {
                Spacer(modifier = Modifier.height(8.dp))
                LinearProgressIndicator(
                    progress = task.progress / 100f,
                    modifier = Modifier.fillMaxWidth()
                )
                Text(
                    text = "${task.progress}%",
                    style = MaterialTheme.typography.labelSmall
                )
            }
            
            task.errorMessage?.let { error ->
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = error,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.error
                )
            }
        }
    }
}

@HiltViewModel
class DownloadsViewModel @Inject constructor(
    private val repository: MusicRepository
) : ViewModel() {
    
    var tasks by mutableStateOf<List<DownloadTask>>(emptyList())
        private set
    
    init {
        loadTasks()
    }
    
    fun loadTasks() {
        viewModelScope.launch {
            repository.getDownloadTasks()
                .onSuccess { tasks = it }
        }
    }
}
