package com.musicapp.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.musicapp.ui.screens.*

sealed class Screen(val route: String) {
    object Login : Screen("login")
    object Register : Screen("register")
    object Home : Screen("home")
    object Search : Screen("search")
    object PlaylistDetail : Screen("playlist/{playlistId}")
    object Player : Screen("player")
    object Rankings : Screen("rankings")
    object RankingDetail : Screen("ranking/{rankingId}")
    object DailyRecommend : Screen("daily")
    object Downloads : Screen("downloads")
    object Settings : Screen("settings")
    object NeteaseLogin : Screen("netease_login")
}

@Composable
fun AppNavigation(
    navController: NavHostController = rememberNavController()
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Login.route
    ) {
        composable(Screen.Login.route) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                },
                onNavigateToRegister = {
                    navController.navigate(Screen.Register.route)
                }
            )
        }
        
        composable(Screen.Register.route) {
            RegisterScreen(
                onRegisterSuccess = {
                    navController.popBackStack()
                },
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
        
        composable(Screen.Home.route) {
            HomeScreen(
                onNavigateToSearch = { navController.navigate(Screen.Search.route) },
                onNavigateToPlaylist = { playlistId ->
                    navController.navigate("playlist/$playlistId")
                },
                onNavigateToRankings = { navController.navigate(Screen.Rankings.route) },
                onNavigateToDaily = { navController.navigate(Screen.DailyRecommend.route) },
                onNavigateToDownloads = { navController.navigate(Screen.Downloads.route) },
                onNavigateToSettings = { navController.navigate(Screen.Settings.route) }
            )
        }
        
        composable(Screen.Search.route) {
            SearchScreen(
                onNavigateBack = { navController.popBackStack() },
                onSongClick = { /* 播放歌曲 */ }
            )
        }
        
        composable(Screen.PlaylistDetail.route) { backStackEntry ->
            val playlistId = backStackEntry.arguments?.getString("playlistId")?.toIntOrNull() ?: 0
            PlaylistDetailScreen(
                playlistId = playlistId,
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.Rankings.route) {
            RankingsScreen(
                onNavigateBack = { navController.popBackStack() },
                onRankingClick = { rankingId ->
                    navController.navigate("ranking/$rankingId")
                }
            )
        }
        
        composable(Screen.RankingDetail.route) { backStackEntry ->
            val rankingId = backStackEntry.arguments?.getString("rankingId")?.toIntOrNull() ?: 0
            RankingDetailScreen(
                rankingId = rankingId,
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.DailyRecommend.route) {
            DailyRecommendScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.Downloads.route) {
            DownloadsScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.Settings.route) {
            SettingsScreen(
                onNavigateBack = { navController.popBackStack() },
                onNavigateToNeteaseLogin = { navController.navigate(Screen.NeteaseLogin.route) },
                onLogout = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }
        
        composable(Screen.NeteaseLogin.route) {
            NeteaseLoginScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}
