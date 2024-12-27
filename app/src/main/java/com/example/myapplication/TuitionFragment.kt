package com.example.myapplication

import android.os.Bundle
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

class TuitionFragment : Fragment() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var hocPhiAdapter: HocPhiAdapter
    private val hocPhiList = mutableListOf<HocPhi>()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_tuition, container, false)
        recyclerView = view.findViewById(R.id.recyclerView1)

        // Setup RecyclerView
        hocPhiAdapter = HocPhiAdapter(hocPhiList)
        recyclerView.layoutManager = LinearLayoutManager(context)
        recyclerView.adapter = hocPhiAdapter

        // Fetch data from API
        fetchHocPhi()

        return view
    }

    private fun fetchHocPhi() {
        RetrofitClient.apiService.getHocPhi().enqueue(object : Callback<List<HocPhi>> {
            override fun onResponse(call: Call<List<HocPhi>>, response: Response<List<HocPhi>>) {
                if (response.isSuccessful && response.body() != null) {
                    val data = response.body()
                    if (!data.isNullOrEmpty()) {
                        hocPhiList.clear()
                        hocPhiList.addAll(data)
                        hocPhiAdapter.notifyDataSetChanged()
                    } else {
                        Toast.makeText(context, "Không có dữ liệu học phí.", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Toast.makeText(context, "Lỗi khi tải dữ liệu.", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<List<HocPhi>>, t: Throwable) {
                Toast.makeText(context, "API call failed: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }
}
