package com.example.area

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.area.data.ApiClient
import com.example.area.data.AppUser
import com.example.area.data.CreateUser
import kotlinx.coroutines.launch

@Composable
fun AboutScreen(paddingValues: PaddingValues) {
    var json by remember { mutableStateOf("Loading…") }
    val scope = rememberCoroutineScope()
    LaunchedEffect(true) {
        scope.launch {
            runCatching { ApiClient.getAbout() }
                .onSuccess { json = it.toString() }
                .onFailure { json = "Error: ${it.message}" }
        }
    }
    Column(Modifier.padding(paddingValues).padding(16.dp)) {
        Text("About.json")
        Spacer(Modifier.height(8.dp))
        Text(json)
    }
}

@Composable
fun UsersScreen(paddingValues: PaddingValues) {
    val scope = rememberCoroutineScope()
    var users by remember { mutableStateOf<List<AppUser>>(emptyList()) }
    var name by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }

    fun reload() {
        scope.launch { runCatching { ApiClient.listUsers() }
            .onSuccess { users = it; error = null }
            .onFailure { error = it.message } }
    }

    LaunchedEffect(true) { reload() }

    Column(Modifier.padding(paddingValues).padding(16.dp)) {
        Text("Users")
        Spacer(Modifier.height(8.dp))
        if (error != null) Text("Error: $error")
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedTextField(value = name, onValueChange = { name = it }, label = { Text("Name") })
            OutlinedTextField(value = email, onValueChange = { email = it }, label = { Text("Email") })
            Button(onClick = {
                scope.launch {
                    runCatching { ApiClient.createUser(CreateUser(email, name)) }
                        .onSuccess { name = ""; email = ""; reload() }
                        .onFailure { error = it.message }
                }
            }) { Text("Create") }
        }
        Spacer(Modifier.height(16.dp))
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(users) { u ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("${u.id}: ${u.name} <${u.email}>")
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Button(onClick = { scope.launch { runCatching { ApiClient.deleteUser(u.id) }.onSuccess { reload() } } }) { Text("Delete") }
                    }
                }
            }
        }
    }
}
