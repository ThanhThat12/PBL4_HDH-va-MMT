package com.example.myapplication

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class ScheduleFragment : Fragment() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var scheduleAdapter: ScheduleAdapter
    private val scheduleList = mutableListOf<Schedule>()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_schedule, container, false)
        recyclerView = view.findViewById(R.id.recyclerView1)
        recyclerView.layoutManager = LinearLayoutManager(context)
        scheduleAdapter = ScheduleAdapter(scheduleList)
        recyclerView.adapter = scheduleAdapter
        fetchScheduleInfo()
        return view
    }

    private fun fetchScheduleInfo() {
        RetrofitClient.apiService.getSchedule().enqueue(object : Callback<List<Schedule>> {
            override fun onResponse(call: Call<List<Schedule>>, response: Response<List<Schedule>>) {
                if (response.isSuccessful) {
                    val scheduleData = response.body()
                    if (!scheduleData.isNullOrEmpty()) {
                        scheduleList.clear()
                        scheduleList.addAll(scheduleData)
                        scheduleAdapter.notifyDataSetChanged()
                    } else {
                        Toast.makeText(context, "No schedule data available", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Log.e("API Error", "Response Code: ${response.code()}, Message: ${response.message()}")
                    Toast.makeText(context, "Failed to load schedule", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<List<Schedule>>, t: Throwable) {
                Log.e("API Failure", "Error: ${t.message}", t)
                Toast.makeText(context, "API call failed: ${t.localizedMessage}", Toast.LENGTH_SHORT).show()
            }
        })
    }
}
