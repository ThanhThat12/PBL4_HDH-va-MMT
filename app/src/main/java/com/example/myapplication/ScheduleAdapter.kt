package com.example.myapplication

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class ScheduleAdapter(private val scheduleList: List<Schedule>) :
    RecyclerView.Adapter<ScheduleAdapter.ScheduleViewHolder>() {

    class ScheduleViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val stt: TextView = itemView.findViewById(R.id.stt)
        val ma: TextView = itemView.findViewById(R.id.ma)
        val tenLopHocPhan: TextView = itemView.findViewById(R.id.tenLopHocPhan)
        val giangVien: TextView = itemView.findViewById(R.id.giangVien)
        val thoiKhoaBieu: TextView = itemView.findViewById(R.id.thoiKhoaBieu)
        val ngayHoc: TextView = itemView.findViewById(R.id.ngayHoc)
        val hocOnline: TextView = itemView.findViewById(R.id.hocOnline)
        val ghiChu: TextView = itemView.findViewById(R.id.ghiChu)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ScheduleViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.lhn_item, parent, false)
        return ScheduleViewHolder(view)
    }

    override fun onBindViewHolder(holder: ScheduleViewHolder, position: Int) {
        val schedule = scheduleList[position]
        holder.stt.text = "STT: ${schedule.STT}"
        holder.ma.text = "Mã: ${schedule.Ma}"
        holder.tenLopHocPhan.text = "Tên LHP: ${schedule.TenLopHocPhan}"
        holder.giangVien.text = "Giảng viên: ${schedule.GiangVien}"
        holder.thoiKhoaBieu.text = "Thời khóa biểu: ${schedule.ThoiKhoaBieu}"
        holder.ngayHoc.text = "Ngày học: ${schedule.NgayHoc}"
        holder.hocOnline.text = "Học online: ${schedule.HocOnline}"
        holder.ghiChu.text = "Ghi chú: ${schedule.GhiChu}"
    }


    override fun getItemCount(): Int {
        return scheduleList.size
    }
}
