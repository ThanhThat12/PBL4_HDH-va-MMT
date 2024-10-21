package com.example.myapplication

import retrofit2.http.GET
import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.POST
import java.io.Serializable

// Đối tượng dữ liệu gửi lên API
data class LoginRequest(val username: String, val password: String)

// Thêm lớp LoginResponse nếu chưa có
data class LoginResponse(
    val success: Boolean,
    val username: String,
    val schedule: List<List<String>>?,
    val survey_schedule: List<List<String>>?
) : Serializable

interface ApiService {
    @POST("/get_all_data") // Endpoint để đăng nhập và lấy dữ liệu
    fun login(@Body loginRequest: LoginRequest): Call<LoginResponse>

    @GET("/tab1") // Thay đổi đường dẫn đến API của bạn
    fun getAnnouncementsTab1(): Call<List<Announcement>>

    @GET("/tab0") // Endpoint cho API 2
    fun getAnnouncementsTab0(): Call<List<Announcement>>
}
