package com.example.myapplication

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class ExamFragment : Fragment() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var lichThiAdapter: LichThiAdapter
    private val lichThiList = mutableListOf<LichThi>()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_exam, container, false)
        recyclerView = view.findViewById(R.id.recyclerView1)

        // Setup RecyclerView
        lichThiAdapter = LichThiAdapter(lichThiList)
        recyclerView.layoutManager = LinearLayoutManager(context)
        recyclerView.adapter = lichThiAdapter

        // Button to fetch data

            fetchLichThi()


        return view
    }

    private fun fetchLichThi() {
        RetrofitClient.apiService.getLichThi().enqueue(object : Callback<LichThiResponse> {
            override fun onResponse(call: Call<LichThiResponse>, response: Response<LichThiResponse>) {
                if (response.isSuccessful && response.body() != null) {
                    val lichThiData = response.body()?.lichThi
                    if (!lichThiData.isNullOrEmpty()) {
                        lichThiList.clear()
                        lichThiList.addAll(lichThiData)
                        lichThiAdapter.notifyDataSetChanged()
                    } else {
                        Toast.makeText(context, "Không có dữ liệu lịch thi.", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Toast.makeText(context, "Lỗi khi tải dữ liệu.", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<LichThiResponse>, t: Throwable) {
                Toast.makeText(context, "API call failed: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }
}
