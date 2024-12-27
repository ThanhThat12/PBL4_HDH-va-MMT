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


class PersonalFragment : Fragment() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var personalAdapter: PersonalAdapter
    private val personalInfoList = mutableListOf<PersonalInfo>()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Inflate the layout for this fragment
        val rootView = inflater.inflate(R.layout.fragment_personal, container, false)

        // Initialize RecyclerView
        recyclerView = rootView.findViewById(R.id.recyclerView1)
        recyclerView.layoutManager = LinearLayoutManager(requireContext())
        personalAdapter = PersonalAdapter(personalInfoList)
        recyclerView.adapter = personalAdapter

        // Fetch data
        fetchPersonalInfo()

        return rootView
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
                    Toast.makeText(requireContext(), "Failed to load personal info", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<PersonalInfoResponse>, t: Throwable) {
                Toast.makeText(requireContext(), "API call failed: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }
}
