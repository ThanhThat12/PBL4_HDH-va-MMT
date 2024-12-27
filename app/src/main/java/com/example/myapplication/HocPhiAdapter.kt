package com.example.myapplication

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class HocPhiAdapter(private val hocPhiList: List<HocPhi>) :
    RecyclerView.Adapter<HocPhiAdapter.HocPhiViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): HocPhiViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.hocphi_item, parent, false)
        return HocPhiViewHolder(view)
    }

    override fun onBindViewHolder(holder: HocPhiViewHolder, position: Int) {
        val hocPhi = hocPhiList[position]
        holder.bind(hocPhi)
    }

    override fun getItemCount(): Int = hocPhiList.size

    class HocPhiViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val stt: TextView = itemView.findViewById(R.id.Stt)
        private val maHP: TextView = itemView.findViewById(R.id.MaHP)
        private val tenHP: TextView = itemView.findViewById(R.id.TenHP)
        private val soTC: TextView = itemView.findViewById(R.id.SoTC)
        private val hocPhiTextView: TextView = itemView.findViewById(R.id.HocPhi)

        fun bind(hocPhi: HocPhi) {
            stt.text = hocPhi.stt
            maHP.text = hocPhi.maHP
            tenHP.text = hocPhi.tenHP
            soTC.text = hocPhi.soTC
            hocPhiTextView.text = hocPhi.hocPhi
        }
    }
}
