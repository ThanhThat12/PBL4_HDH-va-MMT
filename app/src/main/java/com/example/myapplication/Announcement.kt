package com.example.myapplication

import com.google.gson.annotations.SerializedName

data class Announcement(
    val content: String,
    val date: String,
    val title: String
)
data class PersonalInfoResponse(
    val data: PersonalInfo
)

data class PersonalInfo(

    val HoTen: String,
    val NgaySinh: String,
    val GioiTinh: String,
    val NganhHoc: String,
    val Email: String,
    val CTDT: String
)

data class Schedule(
    val STT: String,
    val Ma: String,
    val TenLopHocPhan: String,
    val GiangVien: String,
    val ThoiKhoaBieu: String,
    val NgayHoc: String,
    val HocOnline: String,
    val GhiChu: String
)
data class LichHocResponse(
    @SerializedName("Lịch Học") val LichHoc: List<LichHoc>?
)

data class LichHoc(
    @SerializedName("TT") val tt: String,
    @SerializedName("MaLHP") val maLHP: String,
    @SerializedName("TenLHP") val tenLHP: String,


    @SerializedName("SoTC") val soTC: String,
    @SerializedName("GiangVien") val giangVien: String,
    @SerializedName("TKB") val tkb: String,


    @SerializedName("TuanHoc") val tuanHoc: String
)



data class LichThiResponse(
    @SerializedName("Lịch Thi") val lichThi: List<LichThi>?  // Dùng @SerializedName cho trường có dấu cách
)

data class LichThi(
    val TT: String,
    val MaLHP: String,
    val TenLHP: String,
    val NhomThi: String,
    val ThiChung: String,
    val LichThi: String
)

// Data class for the response containing a list of HocPhi objects
data class HocPhiResponse(
    @SerializedName("hocPhiList") val hocPhiList: List<HocPhi>
)

// Data class for each HocPhi object
// Data class for each HocPhi object
data class HocPhi(
    @SerializedName("HOCPHI") val hocPhi: String,
    @SerializedName("MaHP") val maHP: String,
    @SerializedName("STT") val stt: String,
    @SerializedName("SoTC") val soTC: String,
    @SerializedName("TenHP") val tenHP: String
)














