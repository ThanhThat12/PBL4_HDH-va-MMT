package com.example.myapplication

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class LichThiAdapter(private val lichThiList: List<LichThi>) :
    RecyclerView.Adapter<LichThiAdapter.LichThiViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): LichThiViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_lich_thi, parent, false)
        return LichThiViewHolder(view)
    }

    override fun onBindViewHolder(holder: LichThiViewHolder, position: Int) {
        val lichThi = lichThiList[position]
        holder.bind(lichThi)
    }

    override fun getItemCount(): Int {
        return lichThiList.size
    }

    class LichThiViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val TT: TextView = itemView.findViewById(R.id.TT)
        private val MaLHP: TextView = itemView.findViewById(R.id.MaLHP)
        private val TenLHP: TextView = itemView.findViewById(R.id.TenLHP)
        private val NhomThi: TextView = itemView.findViewById(R.id.NhomThi)
        private val ThiChung: TextView = itemView.findViewById(R.id.thichung)
        private val Lichthi: TextView = itemView.findViewById(R.id.Lichthi)

        fun bind(lichThi: LichThi) {
            TT.text = "Số thứ tự: ${lichThi.TT}"
            MaLHP.text = "Mã LHP: ${lichThi.MaLHP}"
            TenLHP.text = "Tên LHP: ${lichThi.TenLHP}"
            NhomThi.text = "Nhóm thi: ${lichThi.NhomThi}"
            ThiChung.text = "Thi chung: ${lichThi.ThiChung}"
            Lichthi.text = "Lịch thi: ${lichThi.LichThi}"
        }
    }
}
