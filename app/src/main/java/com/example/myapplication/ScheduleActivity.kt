package com.example.myapplication

import android.os.Bundle
import android.view.MenuItem
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.ActionBarDrawerToggle
import androidx.appcompat.app.AppCompatActivity
import androidx.drawerlayout.widget.DrawerLayout
import androidx.core.view.GravityCompat
import com.google.android.material.navigation.NavigationView

class ScheduleActivity : AppCompatActivity() {

    private lateinit var loginResponse: LoginResponse
    private lateinit var textViewData: TextView
    private lateinit var drawerLayout: DrawerLayout
    private lateinit var toggle: ActionBarDrawerToggle

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_schedule)

        // Khởi tạo các view
        drawerLayout = findViewById(R.id.drawer_layout)
        textViewData = findViewById(R.id.textViewData)

        // Thiết lập ActionBarDrawerToggle
        toggle = ActionBarDrawerToggle(this, drawerLayout, R.string.navigation_drawer_open, R.string.navigation_drawer_close)
        drawerLayout.addDrawerListener(toggle)
        toggle.syncState()

        // Thiết lập toolbar
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        // Nhận dữ liệu từ Intent
        val dataString = intent.getSerializableExtra("data") as? LoginResponse
        if (dataString != null) {
            loginResponse = dataString
        } else {
            textViewData.text = "No data available"
            return
        }

        // Thiết lập nút nhấn
        findViewById<Button>(R.id.buttonSchedule).setOnClickListener {
            displayScheduleData()
        }

        findViewById<Button>(R.id.buttonSurveySchedule).setOnClickListener {
            displaySurveyScheduleData()
        }

        findViewById<Button>(R.id.buttonMenu).setOnClickListener {
            // Mở hoặc đóng drawer
            if (drawerLayout.isDrawerOpen(GravityCompat.START)) {
                drawerLayout.closeDrawer(GravityCompat.START)
            } else {
                drawerLayout.openDrawer(GravityCompat.START)
            }
        }

        // Xử lý sự kiện nhấp vào menu điều hướng
        val navigationView: NavigationView = findViewById(R.id.nav_view)
        navigationView.setNavigationItemSelectedListener { menuItem ->
            when (menuItem.itemId) {
                R.id.nav_calendar -> {
                    // Xử lý nhấp vào "Lịch"
                    displayScheduleData()
                }
                R.id.nav_contacts -> {
                    // Xử lý nhấp vào "Liên hệ"
                    // Có thể mở Activity khác nếu cần
                }
                R.id.nav_exit -> {
                    // Thoát ứng dụng
                    finish()
                }
            }
            drawerLayout.closeDrawer(GravityCompat.START) // Đóng drawer sau khi chọn
            true
        }
    }

    private fun displayScheduleData() {
        val schedule = loginResponse.schedule ?: return // Xử lý an toàn null
        val stringBuilder = StringBuilder()

        // Lặp qua lịch
        schedule.forEach { item ->
            if (item.isNotEmpty()) {
                stringBuilder.append("Môn học: ${item.getOrNull(2) ?: "Không có thông tin"}\n") // Tên môn
                stringBuilder.append("Giảng viên: ${item.getOrNull(3) ?: "Không có thông tin"}\n") // Giảng viên
                stringBuilder.append("Thời gian: ${item.getOrNull(5) ?: "Không có thông tin"}\n") // Thời gian
                stringBuilder.append("\n")
            }
        }

        textViewData.text = stringBuilder.toString()
    }

    private fun displaySurveyScheduleData() {
        val surveySchedule = loginResponse.survey_schedule ?: return // Xử lý an toàn null
        val stringBuilder = StringBuilder()

        // Lặp qua lịch khảo sát
        surveySchedule.forEach { item ->
            if (item.isNotEmpty()) {
                stringBuilder.append("Môn học: ${item.getOrNull(2) ?: "Không có thông tin"}\n") // Tên môn
                stringBuilder.append("Giảng viên: ${item.getOrNull(6) ?: "Không có thông tin"}\n") // Giảng viên
                stringBuilder.append("Thời gian: ${item.getOrNull(7) ?: "Không có thông tin"}\n") // Thời gian
                stringBuilder.append("\n")
            }
        }

        textViewData.text = stringBuilder.toString()
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        // Xử lý nhấp chuột vào ActionBarToggle
        return if (toggle.onOptionsItemSelected(item)) {
            true
        } else {
            super.onOptionsItemSelected(item)
        }
    }
}
