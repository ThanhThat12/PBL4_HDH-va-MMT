package com.example.myapplication

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class PersonalAdapter(private val personalInfoList: List<PersonalInfo>) :
    RecyclerView.Adapter<PersonalAdapter.PersonalViewHolder>() {

    class PersonalViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvHoTen: TextView = itemView.findViewById(R.id.hoten)
        val tvNgaySinh: TextView = itemView.findViewById(R.id.ngaysinh)
        val tvGioiTinh: TextView = itemView.findViewById(R.id.gioitinh)
        val tvNganhHoc: TextView = itemView.findViewById(R.id.nganhhoc)
        val tvEmail: TextView = itemView.findViewById(R.id.email)
        val tvCTDT: TextView = itemView.findViewById(R.id.ctdt)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): PersonalViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.personal_item, parent, false)
        return PersonalViewHolder(view)
    }

    override fun onBindViewHolder(holder: PersonalViewHolder, position: Int) {
        val personalInfo = personalInfoList[position]
        holder.tvHoTen.text = "Họ và tên: ${personalInfo.HoTen}"
        holder.tvNgaySinh.text = "Ngày sinh: ${personalInfo.NgaySinh}"
        holder.tvGioiTinh.text = "Giới tính: ${personalInfo.GioiTinh}"
        holder.tvNganhHoc.text = "Ngành học: ${personalInfo.NganhHoc}"
        holder.tvEmail.text = "Email: ${personalInfo.Email}"
        holder.tvCTDT.text = "CTĐT: ${personalInfo.CTDT}"
    }

    override fun getItemCount(): Int = personalInfoList.size
}
