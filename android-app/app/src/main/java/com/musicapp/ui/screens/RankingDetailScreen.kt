package com.musicapp.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Download
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.musicapp.model.RankedSong
import com.musicapp.repository.MusicRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RankingDetailScreen(
    rankingId: Int,
    onNavigateBack: () -> Unit,
    viewModel: RankingDetailViewModel = hiltViewModel()
) {
    LaunchedEffect(rankingId) {
        viewModel.loadRanking(rankingId)
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(viewModel.ranking?.name ?: "排行榜") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "返回")
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
                items(viewModel.ranking?.songs ?: emptyList()) { rankedSong ->
                    RankingSongItem(
                        rankedSong = rankedSong,
                        onDownloadClick = { }
                    )
                }
            }
        }
    }
}

@Composable
fun RankingSongItem(
    rankedSong: RankedSong,
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
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Row(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = "${rankedSong.rank}",
                    style = MaterialTheme.typography.titleMedium,
                    color = if (rankedSong.rank <= 3)
                        MaterialTheme.colorScheme.primary
                    else
                        MaterialTheme.colorScheme.onSurface,
                    modifier = Modifier.width(32.dp)
                )
                
                Column {
                    Text(
                        text = rankedSong.song.title,
                        style = MaterialTheme.typography.titleSmall
                    )
                    Text(
                        text = rankedSong.song.artist,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            IconButton(onClick = onDownloadClick) {
                Icon(Icons.Default.Download, contentDescription = "下载")
            }
        }
    }
}

@HiltViewModel
class RankingDetailViewModel @Inject constructor(
    private val repository: MusicRepository
) : ViewModel() {
    
    var ranking by mutableStateOf<com.musicapp.model.RankingDetail?>(null)
        private set
    
    var isLoading by mutableStateOf(false)
        private set
    
    fun loadRanking(rankingId: Int) {
        viewModelScope.launch {
            isLoading = true
            repository.getNeteaseRankingDetail(rankingId)
                .onSuccess { ranking = it }
            isLoading = false
        }
    }
}
