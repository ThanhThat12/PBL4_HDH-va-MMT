package com.example.myapplication

import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query


// Đối tượng dữ liệu gửi lên API
data class LoginRequest(val username: String, val password: String)
data class LoginResponse(val status: String, val error: String? = null)
// Thêm lớp LoginResponse nếu chưa có


interface ApiService {
    @GET("/search")
    fun searchAnnouncements(
        @Query("query") query: String,
        @Query("criteria") criteria: String,
        @Query("tab") tab: String
    ): Call<List<Announcement>>

    @POST("/login") // Endpoint để đăng nhập và lấy dữ liệu
    fun login(@Body request: LoginRequest): Call<LoginResponse>

    @GET("/tab1") // Thay đổi đường dẫn đến API của bạn
    fun getAnnouncementsTab1(): Call<List<Announcement>>

    @GET("/tab0") // Endpoint cho API 2
    fun getAnnouncementsTab0(): Call<List<Announcement>>

    @GET("personal_info")
    fun getPersonalInfo(): Call<PersonalInfoResponse>

    @GET("/page_lh_ngay")
    fun getScheduleByDate(@Query("ngay") date: String): Call<List<Schedule>>

    @GET("/exam_schedule/class_schedule")
    fun getLichHoc(): Call<LichHocResponse>

    @GET("/exam_schedule/exam_schedule")
    fun getLichThi(): Call<LichThiResponse>

    @GET("/tuition") // Thay URL endpoint API của bạn
    fun getHocPhi(): Call<List<HocPhi>>



}

