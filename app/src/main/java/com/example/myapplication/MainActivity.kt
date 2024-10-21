package com.example.myapplication

import AnnouncementAdapter
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.Gravity
import android.widget.Button
import androidx.appcompat.app.ActionBarDrawerToggle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GravityCompat
import androidx.drawerlayout.widget.DrawerLayout
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.navigation.NavigationView
import okhttp3.OkHttpClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import android.widget.ImageButton

class MainActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var announcementAdapter: AnnouncementAdapter
    private lateinit var apiService: ApiService
    private var announcements: MutableList<Announcement> = mutableListOf()
    private lateinit var drawerLayout: DrawerLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Khởi tạo DrawerLayout
        drawerLayout = findViewById(R.id.drawer_layout)

        // Khởi tạo NavigationView
        val navigationView: NavigationView = findViewById(R.id.nav_view)

        // Tạo toggle cho Drawer
        val toggle = ActionBarDrawerToggle(
            this, drawerLayout, R.string.navigation_drawer_open, R.string.navigation_drawer_close
        )
        drawerLayout.addDrawerListener(toggle)
        toggle.syncState()

        // Sự kiện click cho các mục trong NavigationView
        navigationView.setNavigationItemSelectedListener { menuItem ->
            when (menuItem.itemId) {
                R.id.nav_calendar -> {
                    // Xử lý sự kiện cho mục "Lịch"
                    Log.d("MainActivity", "Lịch được chọn")
                    true
                }
                R.id.nav_contacts -> {
                    // Xử lý sự kiện cho mục "Liên Hệ"
                    Log.d("MainActivity", "Liên hệ được chọn")
                    true
                }
                else -> false
            }
        }

        // Tìm nút "Đăng Nhập/Đăng Ký"
        val buttonLogin: ImageButton = findViewById(R.id.buttonLogin)

        // Thêm sự kiện OnClickListener để mở LoginActivity
        buttonLogin.setOnClickListener {
            val intent = Intent(this, LoginActivity::class.java)
            startActivity(intent)
        }

        // Tìm nút Menu
        val buttonMenu: Button = findViewById(R.id.buttonMenu)
        buttonMenu.setOnClickListener {
            drawerLayout.openDrawer(GravityCompat.START) // Mở menu từ bên trái
        }

        // Khởi tạo RecyclerView
        recyclerView = findViewById(R.id.recyclerView)
        recyclerView.layoutManager = LinearLayoutManager(this)

        // Khởi tạo adapter với danh sách rỗng ban đầu
        announcementAdapter = AnnouncementAdapter(announcements)
        recyclerView.adapter = announcementAdapter

        // Tạo OkHttpClient cho các yêu cầu HTTP với thời gian chờ
        val okHttpClient = OkHttpClient.Builder()
            .connectTimeout(60, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .build()

        // Khởi tạo Retrofit với base URL chung cho cả hai API
        val retrofit = Retrofit.Builder()
            .baseUrl("http://10.0.2.2:5000/") // Localhost cho giả lập Android
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        // Khởi tạo ApiService để gọi API
        apiService = retrofit.create(ApiService::class.java)

        // Ánh xạ các nút để gọi API tương ứng
        val buttonApi1: Button = findViewById(R.id.buttonApi1)
        val buttonApi2: Button = findViewById(R.id.buttonApi2)

        // Gọi API cho tab 0
        buttonApi1.setOnClickListener {
            getAnnouncements(apiService.getAnnouncementsTab0())
        }

        // Gọi API cho tab 1
        buttonApi2.setOnClickListener {
            getAnnouncements(apiService.getAnnouncementsTab1())
        }
    }

    // Phương thức chung để xử lý kết quả API và cập nhật RecyclerView
    private fun getAnnouncements(call: Call<List<Announcement>>) {
        call.enqueue(object : Callback<List<Announcement>> {
            override fun onResponse(call: Call<List<Announcement>>, response: Response<List<Announcement>>) {
                if (response.isSuccessful) {
                    response.body()?.let {
                         // Xóa danh sách cũ
                        announcements.clear()
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

    // Đảm bảo rằng menu được đóng khi người dùng chạm ra ngoài
    override fun onBackPressed() {
        if (drawerLayout.isDrawerOpen(GravityCompat.START)) {
            drawerLayout.closeDrawer(GravityCompat.START)
        } else {
            super.onBackPressed()
        }
    }
}
