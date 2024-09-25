package com.example.myapplication
import java.util.concurrent.TimeUnit

import AnnouncementAdapter
import com.example.myapplication.ApiService
import com.example.myapplication.Announcement
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class MainActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var announcementAdapter: AnnouncementAdapter
    private lateinit var apiService: ApiService // Khai báo apiService
    private var announcements: MutableList<Announcement> = mutableListOf() // Danh sách thông báo

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        recyclerView = findViewById(R.id.recyclerView)
        recyclerView.layoutManager = LinearLayoutManager(this)

        // Khởi tạo adapter với danh sách rỗng ban đầu
        announcementAdapter = AnnouncementAdapter(announcements)
        recyclerView.adapter = announcementAdapter
        val okHttpClient = OkHttpClient.Builder()
            .connectTimeout(60, TimeUnit.SECONDS) // thời gian chờ kết nối
            .readTimeout(60, TimeUnit.SECONDS)    // thời gian chờ đọc dữ liệu
            .build()
        // Khởi tạo Retrofit và ApiService
        val retrofit = Retrofit.Builder()
            .baseUrl("http://10.0.2.2:5000/") // Thay đổi URL nếu cần
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        apiService = retrofit.create(ApiService::class.java) // Khởi tạo apiService

        // Gọi API
        getAnnouncements()
    }

    private fun getAnnouncements() {
        apiService.getAnnouncements().enqueue(object : Callback<List<Announcement>> {
            override fun onResponse(call: Call<List<Announcement>>, response: Response<List<Announcement>>) {
                if (response.isSuccessful) {
                    response.body()?.let {
                        announcements.clear() // Xóa danh sách cũ
                        announcements.addAll(it) // Thêm dữ liệu mới
                        announcementAdapter.notifyDataSetChanged() // Cập nhật adapter
                        Log.d("MainActivity", "Announcements: $it")
                    }
                } else {
                    Log.e("MainActivity", "Error: ${response.code()}")
                }
            }

            override fun onFailure(call: Call<List<Announcement>>, t: Throwable) {
                Log.e("MainActivity", "Failure: ${t.message}", t)
            }
        })
    }
}
