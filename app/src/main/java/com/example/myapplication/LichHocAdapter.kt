package com.example.myapplication

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class LichHocAdapter(private val lichHocList: List<LichHoc>) :
    RecyclerView.Adapter<LichHocAdapter.LichHocViewHolder>() {

    inner class LichHocViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvSoTT: TextView = view.findViewById(R.id.TT)
        val tvMaLHP: TextView = view.findViewById(R.id.MaLHP)
        val tvTenLHP: TextView = view.findViewById(R.id.TenLHP)
        val tvSoTC: TextView = view.findViewById(R.id.SoTCH)
        val tvGiangVien: TextView = view.findViewById(R.id.GV)
        val tvTKB: TextView = view.findViewById(R.id.TKB)
        val tvTuanHoc: TextView = view.findViewById(R.id.Tuanhoc)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): LichHocViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.lich_hoc_item, parent, false)
        return LichHocViewHolder(view)
    }

    override fun onBindViewHolder(holder: LichHocViewHolder, position: Int) {
        val item = lichHocList[position]

        // Thêm mô tả vào nội dung TextView
        holder.tvSoTT.text = "Số thứ tự: ${item.tt}"
        holder.tvMaLHP.text = "Mã LHP: ${item.maLHP}"
        holder.tvTenLHP.text = "Tên LHP: ${item.tenLHP}"
        holder.tvSoTC.text = "Số tín chỉ: ${item.soTC}"
        holder.tvGiangVien.text = "Giảng viên: ${item.giangVien}"
        holder.tvTKB.text = "Thời khóa biểu: ${item.tkb}"
        holder.tvTuanHoc.text = "Tuần học: ${item.tuanHoc}"
    }


    override fun getItemCount(): Int = lichHocList.size
}
