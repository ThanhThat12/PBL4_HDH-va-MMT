package com.example.myapplication

import retrofit2.http.GET
import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.POST
import java.io.Serializable

// Đối tượng dữ liệu gửi lên API
data class LoginRequest(val username: String, val password: String)
data class LoginResponse(val status: String, val error: String? = null)
// Thêm lớp LoginResponse nếu chưa có


interface ApiService {
    @POST("/login") // Endpoint để đăng nhập và lấy dữ liệu
    fun login(@Body request: LoginRequest): Call<LoginResponse>

    @GET("/tab1") // Thay đổi đường dẫn đến API của bạn
    fun getAnnouncementsTab1(): Call<List<Announcement>>

    @GET("/tab0") // Endpoint cho API 2
    fun getAnnouncementsTab0(): Call<List<Announcement>>
}
