package com.example.myapplication

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class ScheduleAdapter(private val scheduleList: List<Schedule>) :
    RecyclerView.Adapter<ScheduleAdapter.ScheduleViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ScheduleViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.lhn_item, parent, false)
        return ScheduleViewHolder(view)
    }

    override fun onBindViewHolder(holder: ScheduleViewHolder, position: Int) {
        val schedule = scheduleList[position]
        holder.bind(schedule)
    }

    override fun getItemCount(): Int = scheduleList.size

    class ScheduleViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val stt: TextView = itemView.findViewById(R.id.stt)
        private val ma: TextView = itemView.findViewById(R.id.ma)
        private val tenLopHocPhan: TextView = itemView.findViewById(R.id.tenLopHocPhan)
        private val giangVien: TextView = itemView.findViewById(R.id.giangVien)
        private val thoiKhoaBieu: TextView = itemView.findViewById(R.id.thoiKhoaBieu)
        private val ngayHoc: TextView = itemView.findViewById(R.id.ngayHoc)
        private val hocOnline: TextView = itemView.findViewById(R.id.hocOnline)
        private val ghiChu: TextView = itemView.findViewById(R.id.ghiChu)

        fun bind(schedule: Schedule) {
            stt.text = "Số thứ tự: ${schedule.STT}"
            ma.text = "Mã lớp: ${schedule.Ma}"
            tenLopHocPhan.text = "Tên lớp học phần: ${schedule.TenLopHocPhan}"
            giangVien.text = "Giảng viên: ${schedule.GiangVien}"
            thoiKhoaBieu.text = "Thời khóa biểu: ${schedule.ThoiKhoaBieu}"
            ngayHoc.text = "Ngày học: ${schedule.NgayHoc}"
            hocOnline.text = "Học online: ${schedule.HocOnline}"
            ghiChu.text = "Ghi chú: ${schedule.GhiChu}"
        }

    }

}
