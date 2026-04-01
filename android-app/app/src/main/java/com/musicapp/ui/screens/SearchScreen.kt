package com.musicapp.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Download
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import coil.compose.AsyncImage
import com.musicapp.model.Song
import com.musicapp.repository.MusicRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SearchScreen(
    onNavigateBack: () -> Unit,
    onSongClick: (Song) -> Unit,
    viewModel: SearchViewModel = hiltViewModel()
) {
    var searchText by remember { mutableStateOf("") }
    var selectedSource by remember { mutableStateOf("all") }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    OutlinedTextField(
                        value = searchText,
                        onValueChange = { searchText = it },
                        placeholder = { Text("搜索歌曲") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true
                    )
                },
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
            // 来源选择
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilterChip(
                    selected = selectedSource == "all",
                    onClick = { selectedSource = "all" },
                    label = { Text("全部") }
                )
                FilterChip(
                    selected = selectedSource == "netease",
                    onClick = { selectedSource = "netease" },
                    label = { Text("网易云") }
                )
                FilterChip(
                    selected = selectedSource == "qq",
                    onClick = { selectedSource = "qq" },
                    label = { Text("QQ音乐") }
                )
                FilterChip(
                    selected = selectedSource == "kugou",
                    onClick = { selectedSource = "kugou" },
                    label = { Text("酷狗") }
                )
            }
            
            // 搜索结果
            if (viewModel.isLoading) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            } else {
                LazyColumn {
                    items(viewModel.searchResults) { song ->
                        SongItem(
                            song = song,
                            onClick = { onSongClick(song) },
                            onDownloadClick = { viewModel.downloadSong(song) }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun SongItem(
    song: Song,
    onClick: () -> Unit,
    onDownloadClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            AsyncImage(
                model = song.coverUrl,
                contentDescription = null,
                modifier = Modifier.size(48.dp),
                contentScale = ContentScale.Crop
            )
            
            Spacer(modifier = Modifier.width(12.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = song.title,
                    style = MaterialTheme.typography.titleSmall
                )
                Text(
                    text = song.artist,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            IconButton(onClick = onDownloadClick) {
                Icon(Icons.Default.Download, contentDescription = "下载")
            }
        }
    }
}

@HiltViewModel
class SearchViewModel @Inject constructor(
    private val repository: MusicRepository
) : ViewModel() {
    
    var searchResults by mutableStateOf<List<Song>>(emptyList())
        private set
    
    var isLoading by mutableStateOf(false)
        private set
    
    fun search(keyword: String, source: String = "all") {
        if (keyword.isBlank()) return
        
        viewModelScope.launch {
            isLoading = true
            repository.searchMusic(keyword, source)
                .onSuccess { result ->
                    searchResults = result.songs
                }
            isLoading = false
        }
    }
    
    fun downloadSong(song: Song) {
        viewModelScope.launch {
            repository.downloadSong(song.source, song.sourceId)
        }
    }
}
