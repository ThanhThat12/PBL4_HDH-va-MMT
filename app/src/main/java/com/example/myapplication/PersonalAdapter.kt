package com.example.myapplication

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class PersonalAdapter(private val personalInfoList: List<PersonalInfo>) :
    RecyclerView.Adapter<PersonalAdapter.PersonalViewHolder>() {

    // ViewHolder định nghĩa giao diện của mỗi item
    class PersonalViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvHoTen: TextView = itemView.findViewById(R.id.hoten)
        val tvNgaySinh: TextView = itemView.findViewById(R.id.ngaysinh)
        val tvGioiTinh: TextView = itemView.findViewById(R.id.gioitinh)
        val tvNganhHoc: TextView = itemView.findViewById(R.id.nganhhoc)
        val tvEmail: TextView = itemView.findViewById(R.id.email)
        val tvCTDT: TextView = itemView.findViewById(R.id.ctdt)
    }

    // Phương thức tạo view cho mỗi item
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): PersonalViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.personal_item, parent, false) // Trỏ đến layout personal_item.xml
        return PersonalViewHolder(view)
    }

    // Gắn dữ liệu vào mỗi item trong RecyclerView
    override fun onBindViewHolder(holder: PersonalViewHolder, position: Int) {
        val personalInfo = personalInfoList[position]

        // Gắn dữ liệu kèm theo mô tả
        holder.tvHoTen.text = "Họ và tên: ${personalInfo.HoTen}"
        holder.tvNgaySinh.text = "Ngày sinh: ${personalInfo.NgaySinh}"
        holder.tvGioiTinh.text = "Giới tính: ${personalInfo.GioiTinh}"
        holder.tvNganhHoc.text = "Ngành học: ${personalInfo.NganhHoc}"
        holder.tvEmail.text = "Email: ${personalInfo.Email}"
        holder.tvCTDT.text = "CTĐT: ${personalInfo.CTDT}"
    }


    // Trả về số lượng item trong RecyclerView
    override fun getItemCount(): Int = personalInfoList.size
}
