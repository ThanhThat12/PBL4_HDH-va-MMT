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

class Schedule2Fragment : Fragment() {
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: LichHocAdapter
    private val lichHocList = mutableListOf<LichHoc>()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_schedule2, container, false)

        // Khởi tạo RecyclerView
        recyclerView = view.findViewById(R.id.recyclerView1)
        recyclerView.layoutManager = LinearLayoutManager(context)
        adapter = LichHocAdapter(lichHocList)
        recyclerView.adapter = adapter

        // Gọi API để lấy dữ liệu
        fetchLichHoc()

        return view
    }

    private fun fetchLichHoc() {
        RetrofitClient.apiService.getLichHoc().enqueue(object : Callback<LichHocResponse> {
            override fun onResponse(call: Call<LichHocResponse>, response: Response<LichHocResponse>) {
                if (response.isSuccessful) {
                    val responseData = response.body()?.LichHoc
                    if (!responseData.isNullOrEmpty()) {
                        lichHocList.clear()
                        lichHocList.addAll(responseData)
                        adapter.notifyDataSetChanged()
                    } else {
                        Toast.makeText(context, "Không có dữ liệu lịch học", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Log.e("API Error", "Response Code: ${response.code()}, Message: ${response.message()}")
                    Toast.makeText(context, "Không tải được dữ liệu lịch học", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<LichHocResponse>, t: Throwable) {
                Log.e("API Failure", "Error: ${t.message}", t)
                Toast.makeText(context, "Không thể gọi API: ${t.localizedMessage}", Toast.LENGTH_SHORT).show()
            }
        })
    }
}
