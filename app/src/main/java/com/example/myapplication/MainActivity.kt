package com.example.myapplication

import AnnouncementAdapter
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.ImageButton
import android.widget.Spinner
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

class MainActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var announcementAdapter: AnnouncementAdapter
    private lateinit var apiService: ApiService
    private var announcements: MutableList<Announcement> = mutableListOf()
    private lateinit var drawerLayout: DrawerLayout

    // Theo dõi nút hiện tại được chọn
    private var selectedButtonId: Int = R.id.buttonApi1 // Mặc định chọn buttonApi1

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

        // Thiết lập listener khi chọn mục trong NavigationView
        navigationView.setNavigationItemSelectedListener { menuItem ->
            when (menuItem.itemId) {
                R.id.nav_home -> {
                    // Handle Home click
                }
                R.id.nav_notice -> {
                    // Handle Emergency click
                }
                R.id.nav_about -> {
                    // Handle About Us click
                }
            }
            drawerLayout.closeDrawers()
            true
        }
        val searchButton: Button = findViewById(R.id.searchButton)
        searchButton.setOnClickListener {
            val query = findViewById<EditText>(R.id.searchKeywordEditText).text.toString()
            val criteria = findViewById<Spinner>(R.id.searchCriteriaSpinner).selectedItem.toString().toLowerCase()

            // Xử lý tìm kiếm theo tiêu chí và từ khóa
            searchAnnouncements(query, criteria)
        }
        // Khởi tạo nút Đăng nhập
        val buttonLogin: ImageButton = findViewById(R.id.buttonLogin)
        buttonLogin.setOnClickListener {
            val intent = Intent(this, LoginActivity::class.java)
            startActivity(intent)
        }

        // Khởi tạo nút Menu
        val buttonMenu: Button = findViewById(R.id.buttonMenu)
        buttonMenu.setOnClickListener {
            drawerLayout.openDrawer(GravityCompat.START) // Mở drawer từ bên trái
        }

        // Khởi tạo RecyclerView
        recyclerView = findViewById(R.id.recyclerView)
        recyclerView.layoutManager = LinearLayoutManager(this)

        // Khởi tạo adapter với danh sách rỗng
        announcementAdapter = AnnouncementAdapter(announcements)
        recyclerView.adapter = announcementAdapter

        // Tạo OkHttpClient cho các yêu cầu HTTP với thời gian chờ
        val okHttpClient = OkHttpClient.Builder()
            .connectTimeout(60, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .build()

        // Khởi tạo Retrofit với URL cơ bản
        val retrofit = Retrofit.Builder()
//            .baseUrl("http://192.168.1.11:5000/")
            .baseUrl("http://10.0.2.2:5000/")// Localhost cho trình giả lập Android
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        // Khởi tạo ApiService cho các cuộc gọi API
        apiService = retrofit.create(ApiService::class.java)

        // Ánh xạ các nút với các cuộc gọi API
        val buttonApi1: Button = findViewById(R.id.buttonApi1)
        val buttonApi2: Button = findViewById(R.id.buttonApi2)

        // Thiết lập listener cho buttonApi1
        buttonApi1.setOnClickListener {
            getAnnouncements(apiService.getAnnouncementsTab0())
            updateButtonSelection(buttonApi1.id) // Cập nhật trạng thái nút đã chọn
        }

        // Thiết lập listener cho buttonApi2
        buttonApi2.setOnClickListener {
            getAnnouncements(apiService.getAnnouncementsTab1())
            updateButtonSelection(buttonApi2.id) // Cập nhật trạng thái nút đã chọn
        }

        // Cập nhật màu sắc cho các nút đã chọn ban đầu
        getAnnouncements(apiService.getAnnouncementsTab0())
        updateButtonSelection(buttonApi1.id)
        updateButtonSelection(selectedButtonId)
    }

    // Cập nhật màu sắc cho nút đã chọn
    private fun updateButtonSelection(selectedId: Int) {
        val buttonApi1: Button = findViewById(R.id.buttonApi1)
        val buttonApi2: Button = findViewById(R.id.buttonApi2)

        // Cập nhật màu sắc cho nút được chọn
        if (selectedId == buttonApi1.id) {
            buttonApi1.setTextColor(getColor(R.color.colorAccent)) // Thay đổi màu này theo ý muốn
            buttonApi2.setTextColor(getColor(android.R.color.black)) // Màu mặc định
        } else {
            buttonApi2.setTextColor(getColor(R.color.colorAccent)) // Thay đổi màu này theo ý muốn
            buttonApi1.setTextColor(getColor(android.R.color.black)) // Màu mặc định
        }
        selectedButtonId = selectedId // Cập nhật trạng thái
    }

    // Xử lý kết quả API và cập nhật RecyclerView
    private fun getAnnouncements(call: Call<List<Announcement>>) {
        call.enqueue(object : Callback<List<Announcement>> {
            override fun onResponse(call: Call<List<Announcement>>, response: Response<List<Announcement>>) {
                if (response.isSuccessful) {
                    response.body()?.let {
                        announcements.clear() // Xóa dữ liệu cũ
                        announcements.addAll(it) // Thêm dữ liệu mới
                        announcementAdapter.notifyDataSetChanged() // Thông báo adapter
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
    private fun searchAnnouncements(query: String, criteria: String) {
        val selectedTab = if (selectedButtonId == R.id.buttonApi1) "tab0" else "tab1"
        apiService.searchAnnouncements(query, criteria, selectedTab).enqueue(object : Callback<List<Announcement>> {
            override fun onResponse(call: Call<List<Announcement>>, response: Response<List<Announcement>>) {
                if (response.isSuccessful) {
                    announcements.clear()
                    announcements.addAll(response.body() ?: emptyList())
                    announcementAdapter.notifyDataSetChanged()
                } else {
                    Log.e("MainActivity", "Error: ${response.message()}")
                }
            }

            override fun onFailure(call: Call<List<Announcement>>, t: Throwable) {
                Log.e("MainActivity", "Failure: ${t.message}")
            }
        })
    }
    // Xử lý nút quay lại để đóng drawer
    override fun onBackPressed() {
        if (drawerLayout.isDrawerOpen(GravityCompat.START)) {
            drawerLayout.closeDrawer(GravityCompat.START)
        } else {
            super.onBackPressed()
        }
    }
}
