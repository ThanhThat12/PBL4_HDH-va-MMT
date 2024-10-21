package com.example.myapplication

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class LoginActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        val loginButton: Button = findViewById(R.id.buttonLogin)
        loginButton.setOnClickListener {
            val username = findViewById<EditText>(R.id.editTextUsername).text.toString()
            val password = findViewById<EditText>(R.id.editTextPassword).text.toString()

            // Gọi API đăng nhập
            login(username, password)
        }

        // Nút Trở Lại
        val backButton: Button = findViewById(R.id.buttonBack)
        backButton.setOnClickListener {
            // Kết thúc activity hiện tại và quay lại activity trước đó
            finish()
        }
    }

    private fun login(username: String, password: String) {
        // Tạo đối tượng LoginRequest
        val loginRequest = LoginRequest(username, password)

        // Gọi API thông qua RetrofitClient
        RetrofitClient.instance.login(loginRequest).enqueue(object : Callback<LoginResponse> {
            override fun onResponse(call: Call<LoginResponse>, response: Response<LoginResponse>) {
                if (response.isSuccessful && response.body()?.success == true) {
                    // Đăng nhập thành công, chuyển sang ScheduleActivity
                    val intent = Intent(this@LoginActivity, ScheduleActivity::class.java)
                    intent.putExtra("data", response.body()) // Chuyển dữ liệu
                    startActivity(intent)
                    finish()
                } else {
                    // Xử lý khi đăng nhập không thành công
                    Toast.makeText(this@LoginActivity, "Đăng nhập thất bại", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
                Toast.makeText(this@LoginActivity, "Lỗi: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }
}
