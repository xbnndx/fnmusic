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
import com.musicapp.model.RankingList
import com.musicapp.repository.MusicRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RankingsScreen(
    onNavigateBack: () -> Unit,
    onRankingClick: (Int) -> Unit,
    viewModel: RankingsViewModel = hiltViewModel()
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("排行榜") },
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
            items(viewModel.rankings) { ranking ->
                RankingItem(
                    ranking = ranking,
                    onClick = { onRankingClick(ranking.id) }
                )
            }
        }
    }
}

@Composable
fun RankingItem(
    ranking: RankingList,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp),
        onClick = onClick
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = ranking.name,
                style = MaterialTheme.typography.titleMedium
            )
            Text(
                text = "${ranking.songCount}首歌曲",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@HiltViewModel
class RankingsViewModel @Inject constructor(
    private val repository: MusicRepository
) : ViewModel() {
    
    var rankings by mutableStateOf<List<RankingList>>(emptyList())
        private set
    
    init {
        loadRankings()
    }
    
    fun loadRankings() {
        viewModelScope.launch {
            repository.getNeteaseRankings()
                .onSuccess { rankings = it }
        }
    }
}
