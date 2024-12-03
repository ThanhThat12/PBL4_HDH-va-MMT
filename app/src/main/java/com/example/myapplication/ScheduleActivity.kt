package com.example.myapplication

import android.content.res.ColorStateList
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response


class ScheduleActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var personalAdapter: PersonalAdapter
    private lateinit var scheduleAdapter: ScheduleAdapter
    private lateinit var btnPersonal: Button
    private lateinit var btnLhn: Button
    private lateinit var btnLichHoc: Button // Nút btnlichhoc
    private lateinit var btnLichThi: Button // Nút btnlichthi
    private lateinit var btnHocPhi: Button

    private val personalInfoList = mutableListOf<PersonalInfo>()
    private val scheduleList = mutableListOf<Schedule>()
    private val lichHocList = mutableListOf<LichHoc>()
    private val lichThiList = mutableListOf<LichThi>()
    private val hocPhiList =  mutableListOf<HocPhi>()

    private lateinit var lichHocAdapter: LichHocAdapter
    private lateinit var lichThiAdapter: LichThiAdapter
    private lateinit var hocPhiAdapter: HocPhiAdapter




    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_schedule)

        // Initialize RecyclerView
        recyclerView = findViewById(R.id.recyclerView1)
        recyclerView.layoutManager = LinearLayoutManager(this)

        // Initialize adapters
        personalAdapter = PersonalAdapter(personalInfoList)
        scheduleAdapter = ScheduleAdapter(scheduleList)
        lichHocAdapter = LichHocAdapter(lichHocList)
        lichThiAdapter = LichThiAdapter(lichThiList)
        hocPhiAdapter = HocPhiAdapter(hocPhiList)

        // Initially set the personal adapter
        recyclerView.adapter = personalAdapter

        // Set up buttons
        btnPersonal = findViewById(R.id.btnpersonal)
        btnLhn = findViewById(R.id.btnlhn)
        btnLichHoc = findViewById(R.id.btnlichhoc) // Correct button ID for study schedule
        btnLichThi = findViewById(R.id.btnlichthi) // Correct button ID for exam schedule
        btnHocPhi = findViewById(R.id.btnhocphi)

        val buttons = listOf(btnPersonal, btnLhn, btnLichHoc, btnLichThi, btnHocPhi)
        // Load personal info initially
        fetchPersonalInfo()

        // Button click to show personal info
        fun resetAllButtons() {
            for (button in buttons) {
                button.setTextColor(resources.getColor(android.R.color.black, null)) // Màu chữ mặc định
                button.compoundDrawableTintList =
                    ColorStateList.valueOf(resources.getColor(android.R.color.black, null)) // Màu icon mặc định
            }
        }

// Xử lý sự kiện click cho từng nút
        btnPersonal.setOnClickListener {
            resetAllButtons() // Đặt lại trạng thái tất cả các nút
            recyclerView.adapter = personalAdapter
            fetchPersonalInfo()

            // Đổi màu logo và chữ của nút được chọn
            btnPersonal.setTextColor(resources.getColor(android.R.color.holo_red_light, null))
            btnPersonal.compoundDrawableTintList =
                ColorStateList.valueOf(resources.getColor(android.R.color.holo_red_light, null))
        }

        btnLhn.setOnClickListener {
            resetAllButtons()
            recyclerView.adapter = scheduleAdapter
            fetchSchedule()

            btnLhn.setTextColor(resources.getColor(android.R.color.holo_red_light, null))
            btnLhn.compoundDrawableTintList =
                ColorStateList.valueOf(resources.getColor(android.R.color.holo_red_light, null))
        }

        btnLichHoc.setOnClickListener {
            resetAllButtons()
            recyclerView.adapter = lichHocAdapter
            fetchLichHoc()

            btnLichHoc.setTextColor(resources.getColor(android.R.color.holo_red_light, null))
            btnLichHoc.compoundDrawableTintList =
                ColorStateList.valueOf(resources.getColor(android.R.color.holo_red_light, null))
        }

        btnLichThi.setOnClickListener {
            resetAllButtons()
            recyclerView.adapter = lichThiAdapter
            fetchLichThi()

            btnLichThi.setTextColor(resources.getColor(android.R.color.holo_red_light, null))
            btnLichThi.compoundDrawableTintList =
                ColorStateList.valueOf(resources.getColor(android.R.color.holo_red_light, null))
        }
        btnHocPhi.setOnClickListener {
            resetAllButtons()
            recyclerView.adapter = hocPhiAdapter
            fetchHocPhiData()

            btnHocPhi.setTextColor(resources.getColor(android.R.color.holo_red_light, null))
            btnHocPhi.compoundDrawableTintList =
                ColorStateList.valueOf(resources.getColor(android.R.color.holo_red_light, null))
        }

    }

    private fun fetchPersonalInfo() {
        RetrofitClient.apiService.getPersonalInfo().enqueue(object : Callback<PersonalInfoResponse> {
            override fun onResponse(call: Call<PersonalInfoResponse>, response: Response<PersonalInfoResponse>) {
                if (response.isSuccessful) {
                    val personalInfoResponse = response.body()
                    personalInfoResponse?.let {
                        val personalInfo = it.data
                        personalInfoList.clear()
                        personalInfoList.add(personalInfo)
                        personalAdapter.notifyDataSetChanged()
                    }
                } else {
                    Toast.makeText(applicationContext, "Failed to load personal info", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<PersonalInfoResponse>, t: Throwable) {
                Toast.makeText(applicationContext, "API call failed: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })


    }

    private fun fetchSchedule() {
        RetrofitClient.apiService.getSchedule().enqueue(object : Callback<List<Schedule>> {
            override fun onResponse(call: Call<List<Schedule>>, response: Response<List<Schedule>>) {
                if (response.isSuccessful) {
                    val scheduleData = response.body()
                    if (!scheduleData.isNullOrEmpty()) {
                        scheduleList.clear()
                        scheduleList.addAll(scheduleData)
                        scheduleAdapter.notifyDataSetChanged()
                    } else {
                        Toast.makeText(applicationContext, "No schedule data available", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Log.e("API Error", "Response Code: ${response.code()}, Message: ${response.message()}")
                    Toast.makeText(applicationContext, "Failed to load schedule", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<List<Schedule>>, t: Throwable) {
                Log.e("API Failure", "Error: ${t.message}", t)
                Toast.makeText(applicationContext, "API call failed: ${t.localizedMessage}", Toast.LENGTH_SHORT).show()
            }
        })
    }


    private fun fetchLichHoc() {
        RetrofitClient.apiService.getLichHoc().enqueue(object : Callback<LichHocResponse> {
            override fun onResponse(call: Call<LichHocResponse>, response: Response<LichHocResponse>) {
                if (response.isSuccessful) {
                    val lichHocResponse = response.body()
                    Log.d("ScheduleActivity", "LichHoc Response: $lichHocResponse")
                    val lichHocData = lichHocResponse?.LichHoc
                    if (!lichHocData.isNullOrEmpty()) {
                        lichHocList.clear()
                        lichHocList.addAll(lichHocData)
                        lichHocAdapter.notifyDataSetChanged()
                    } else {
                        Toast.makeText(applicationContext, "Study schedule is empty", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Toast.makeText(applicationContext, "Failed to load study schedule", Toast.LENGTH_SHORT).show()
                }
            }


            override fun onFailure(call: Call<LichHocResponse>, t: Throwable) {
                Toast.makeText(applicationContext, "API call failed: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }


    private fun fetchLichThi() {
        RetrofitClient.apiService.getLichThi().enqueue(object : Callback<LichThiResponse> {
            override fun onResponse(call: Call<LichThiResponse>, response: Response<LichThiResponse>) {
                if (response.isSuccessful && response.body() != null) {
                    val lichThiData = response.body()?.lichThi  // Dùng tên trường đúng là "lichThi"
                    if (!lichThiData.isNullOrEmpty()) {
                        lichThiList.clear()
                        lichThiList.addAll(lichThiData)
                        lichThiAdapter.notifyDataSetChanged()
                    } else {
                        Toast.makeText(applicationContext, "Không có dữ liệu lịch thi.", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Toast.makeText(applicationContext, "Lỗi khi tải dữ liệu.", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<LichThiResponse>, t: Throwable) {
                Toast.makeText(applicationContext, "API call failed: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

    private fun fetchHocPhiData() {
        RetrofitClient.apiService.getHocPhi().enqueue(object : Callback<List<HocPhi>> {
            override fun onResponse(call: Call<List<HocPhi>>, response: Response<List<HocPhi>>) {
                if (response.isSuccessful) {
                    val hocPhiData = response.body()
                    hocPhiData?.let {
                        // Set the RecyclerView adapter
                        recyclerView.adapter = HocPhiAdapter(it)
                    }
                } else {
                    Log.e("API Error", "Response Code: ${response.code()}, Message: ${response.message()}")
                    Toast.makeText(applicationContext, "Lỗi khi tải dữ liệu học phí", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<List<HocPhi>>, t: Throwable) {
                Log.e("API Failure", "Error: ${t.message}", t)
                Toast.makeText(applicationContext, "Lỗi kết nối API: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }





}
