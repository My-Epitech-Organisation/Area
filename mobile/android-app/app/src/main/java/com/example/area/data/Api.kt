package com.example.area.data

import com.example.area.BuildConfig
import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.engine.android.Android
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.serialization.kotlinx.json.json
import io.ktor.client.request.delete
import io.ktor.client.request.get
import io.ktor.client.request.post
import io.ktor.client.request.put
import io.ktor.client.request.setBody
import io.ktor.http.ContentType
import io.ktor.http.contentType
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

object ApiClient {
    val json = Json { ignoreUnknownKeys = true }
    val client = HttpClient(Android) {
        install(ContentNegotiation) { json(json) }
    }
    private val base = BuildConfig.API_BASE_URL

    suspend fun getAbout(): About = client.get("$base/about.json").body()
    suspend fun listUsers(): List<AppUser> = client.get("$base/api/users/").body()
    suspend fun createUser(u: CreateUser): AppUser =
        client.post("$base/api/users/") { contentType(ContentType.Application.Json); setBody(u) }.body()
    suspend fun updateUser(id: Int, u: CreateUser): AppUser =
        client.put("$base/api/users/$id/") { contentType(ContentType.Application.Json); setBody(u) }.body()
    suspend fun deleteUser(id: Int) { client.delete("$base/api/users/$id/") }
}

@Serializable
data class About(val client: Client, val server: Server)
@Serializable
data class Client(val host: String)
@Serializable
data class Server(val current_time: Long, val services: List<Service>)
@Serializable
data class Service(val name: String, val actions: List<Action>, val reactions: List<Reaction>)
@Serializable
data class Action(val name: String, val description: String)
@Serializable
data class Reaction(val name: String, val description: String)

@Serializable
data class AppUser(val id: Int, val email: String, val name: String)
@Serializable
data class CreateUser(val email: String, val name: String)
