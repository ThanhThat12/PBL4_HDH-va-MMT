package com.example.myapplication

import retrofit2.Call
import retrofit2.http.GET

interface ApiService {
    @GET("/tab1") // Thay đổi đường dẫn đến API của bạn
    fun getAnnouncements(): Call<List<Announcement>>
}