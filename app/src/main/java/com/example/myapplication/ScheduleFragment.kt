package com.example.myapplication

import android.app.DatePickerDialog
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.text.SimpleDateFormat
import java.util.*


import android.widget.DatePicker



class ScheduleFragment : Fragment() {

    private lateinit var editTextDate: EditText
    private lateinit var recyclerView: RecyclerView
    private lateinit var scheduleAdapter: ScheduleAdapter
    private val scheduleList = mutableListOf<Schedule>()

    private val calendar = Calendar.getInstance() // Để lưu ngày hiện tại

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_schedule, container, false)

        // Ánh xạ các view
        editTextDate = view.findViewById(R.id.editTextDate)
        recyclerView = view.findViewById(R.id.recyclerView1)
        recyclerView.layoutManager = LinearLayoutManager(context)
        scheduleAdapter = ScheduleAdapter(scheduleList)
        recyclerView.adapter = scheduleAdapter

        setupDatePickerAndApiCall()
        return view
    }

    private fun setupDatePickerAndApiCall() {
        // Hiển thị ngày hiện tại trong EditText khi mở ứng dụng
        val currentDate = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault()).format(calendar.time)
        editTextDate.setText(currentDate)

        // Tự động gọi API với ngày hiện tại khi khởi tạo
        fetchScheduleInfo(currentDate)

        // Khi nhấn vào EditText
        editTextDate.setOnClickListener {
            showDatePickerDialog()
        }
    }

    private fun showDatePickerDialog() {
        val year = calendar.get(Calendar.YEAR)
        val month = calendar.get(Calendar.MONTH)
        val day = calendar.get(Calendar.DAY_OF_MONTH)

        // Hiển thị DatePickerDialog
        val datePickerDialog = DatePickerDialog(requireContext(),
            { _: DatePicker, selectedYear: Int, selectedMonth: Int, selectedDay: Int ->
                // Cập nhật Calendar và EditText khi người dùng chọn ngày
                calendar.set(selectedYear, selectedMonth, selectedDay)
                val formattedDate = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault()).format(calendar.time)
                editTextDate.setText(formattedDate)

                // Gọi API với ngày được chọn
                fetchScheduleInfo(formattedDate)
            }, year, month, day
        )
        datePickerDialog.show()
    }

    private fun fetchScheduleInfo(date: String) {
        RetrofitClient.apiService.getScheduleByDate(date).enqueue(object : Callback<List<Schedule>> {
            override fun onResponse(call: Call<List<Schedule>>, response: Response<List<Schedule>>) {
                if (response.isSuccessful) {
                    val scheduleData = response.body()
                    if (!scheduleData.isNullOrEmpty()) {
                        scheduleList.clear()
                        scheduleList.addAll(scheduleData)
                        scheduleAdapter.notifyDataSetChanged()
                    } else {
                        Toast.makeText(context, "Không có lịch học cho ngày $date", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Log.e("API Error", "Response Code: ${response.code()}, Message: ${response.message()}")
                    Toast.makeText(context, "Không có lịch học cho ngày $date", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<List<Schedule>>, t: Throwable) {
                Log.e("API Failure", "Error: ${t.message}", t)
                Toast.makeText(context, "API call failed: ${t.localizedMessage}", Toast.LENGTH_SHORT).show()
            }
        })
    }
}
