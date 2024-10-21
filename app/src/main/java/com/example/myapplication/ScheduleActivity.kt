package com.example.myapplication

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.io.Serializable

class ScheduleActivity : AppCompatActivity() {

    // Thay đổi kiểu dữ liệu để nhận LoginResponse
    private lateinit var loginResponse: LoginResponse
    private lateinit var textViewData: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_schedule)

        // Nhận dữ liệu từ Intent
        val dataString = intent.getSerializableExtra("data") as? LoginResponse
        if (dataString != null) {
            loginResponse = dataString
        }

        textViewData = findViewById(R.id.textViewData)

        // Xử lý nút Hiển thị Lịch Học
        val buttonSchedule: Button = findViewById(R.id.buttonSchedule)
        buttonSchedule.setOnClickListener {
            displayScheduleData()
        }

        // Xử lý nút Hiển thị Khảo Sát Ý Kiến
        val buttonSurveySchedule: Button = findViewById(R.id.buttonSurveySchedule)
        buttonSurveySchedule.setOnClickListener {
            displaySurveyScheduleData()
        }
    }

    private fun displayScheduleData() {
        val schedule = loginResponse.schedule
        val stringBuilder = StringBuilder()

        // Duyệt qua từng mục trong lịch học
        schedule?.forEach { item ->
            if (item.isNotEmpty()) {
                stringBuilder.append("Môn học: ${item[2]}\n") // Tên môn
                stringBuilder.append("Giảng viên: ${item[3]}\n") // Giảng viên
                stringBuilder.append("Thời gian: ${item[5]}\n") // Thời gian
                stringBuilder.append("\n")
            }
        }

        textViewData.text = stringBuilder.toString()
    }

    private fun displaySurveyScheduleData() {
        val surveySchedule = loginResponse.survey_schedule
        val stringBuilder = StringBuilder()

        // Duyệt qua từng mục trong lịch khảo sát
        surveySchedule?.forEach { item ->
            if (item.isNotEmpty()) {
                stringBuilder.append("Môn học: ${item[2]}\n") // Tên môn
                // Kiểm tra xem chỉ số 6 và 7 có hợp lệ không
                if (item.size > 6) {
                    stringBuilder.append("Giảng viên: ${item[6]}\n") // Giảng viên
                } else {
                    stringBuilder.append("Giảng viên: Không có thông tin\n")
                }
                if (item.size > 7) {
                    stringBuilder.append("Thời gian: ${item[7]}\n") // Thời gian
                } else {
                    stringBuilder.append("Thời gian: Không có thông tin\n")
                }
                stringBuilder.append("\n")
            }
        }

        textViewData.text = stringBuilder.toString()
    }

}


