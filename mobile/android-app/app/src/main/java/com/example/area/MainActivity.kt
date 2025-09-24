package com.example.area

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.*
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.tooling.preview.Preview
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                App()
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun App() {
    val navController = rememberNavController()
    val backStack by navController.currentBackStackEntryAsState()
    val route = backStack?.destination?.route ?: "about"

    Scaffold(topBar = {
        TopAppBar(title = { Text("AREA POC") }, actions = {
            TextButton(onClick = { navController.navigate("about") }) { Text("About") }
            TextButton(onClick = { navController.navigate("users") }) { Text("Users") }
        })
    }) { padding ->
        NavHost(navController, startDestination = "about") {
            composable("about") { AboutScreen(paddingValues = padding) }
            composable("users") { UsersScreen(paddingValues = padding) }
        }
    }
}

@Preview
@Composable
fun PreviewApp() {
    MaterialTheme { App() }
}
