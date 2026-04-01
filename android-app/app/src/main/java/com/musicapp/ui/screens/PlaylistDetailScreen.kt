package com.musicapp.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import coil.compose.AsyncImage
import com.musicapp.model.Playlist
import com.musicapp.model.Song
import com.musicapp.repository.MusicRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PlaylistDetailScreen(
    playlistId: Int,
    onNavigateBack: () -> Unit,
    viewModel: PlaylistDetailViewModel = hiltViewModel()
) {
    LaunchedEffect(playlistId) {
        viewModel.loadPlaylist(playlistId)
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(viewModel.playlist?.name ?: "歌单详情") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "返回")
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.playAll() }) {
                        Icon(Icons.Default.PlayArrow, contentDescription = "播放全部")
                    }
                }
            )
        }
    ) { padding ->
        if (viewModel.isLoading) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = androidx.compose.ui.Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
            ) {
                // 歌单封面和信息
                item {
                    viewModel.playlist?.let { playlist ->
                        Column(
                            modifier = Modifier.padding(16.dp)
                        ) {
                            AsyncImage(
                                model = playlist.coverUrl,
                                contentDescription = null,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .aspectRatio(1f),
                                contentScale = ContentScale.Crop
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                text = playlist.name,
                                style = MaterialTheme.typography.headlineSmall
                            )
                            playlist.description?.let {
                                Text(
                                    text = it,
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                            Text(
                                text = "共${playlist.songCount}首",
                                style = MaterialTheme.typography.labelMedium,
                                color = MaterialTheme.colorScheme.primary
                            )
                        }
                    }
                }
                
                // 歌曲列表
                items(viewModel.playlist?.songs ?: emptyList()) { song ->
                    SongItem(
                        song = song,
                        onClick = { /* 播放歌曲 */ },
                        onDownloadClick = { /* 下载歌曲 */ }
                    )
                }
            }
        }
    }
}

@HiltViewModel
class PlaylistDetailViewModel @Inject constructor(
    private val repository: MusicRepository
) : ViewModel() {
    
    var playlist by mutableStateOf<Playlist?>(null)
        private set
    
    var isLoading by mutableStateOf(false)
        private set
    
    fun loadPlaylist(playlistId: Int) {
        viewModelScope.launch {
            isLoading = true
            repository.getPlaylist(playlistId)
                .onSuccess { playlist = it }
            isLoading = false
        }
    }
    
    fun playAll() {
        // 播放歌单所有歌曲
    }
}
