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

            // Kiểm tra xem người dùng đã nhập đủ tài khoản và mật khẩu hay chưa
            if (username.isNotEmpty() && password.isNotEmpty()) {
                // Gọi API đăng nhập
                login(username, password)
            } else {
                Toast.makeText(this, "Vui lòng nhập tài khoản và mật khẩu", Toast.LENGTH_SHORT).show()
            }
        }

        // Nút Trở Lại
        val backButton: Button = findViewById(R.id.buttonBack)
        backButton.setOnClickListener {
            finish()
        }
    }

    private fun login(username: String, password: String) {
        // Tạo đối tượng LoginRequest
        val loginRequest = LoginRequest(username, password)

        // Gọi API thông qua RetrofitClient (Sử dụng apiService)
        RetrofitClient.apiService.login(loginRequest).enqueue(object : Callback<LoginResponse> {
            override fun onResponse(call: Call<LoginResponse>, response: Response<LoginResponse>) {
                if (response.isSuccessful && response.body()?.status == "success") {
                    // Đăng nhập thành công, chuyển sang ScheduleActivity
                    val intent = Intent(this@LoginActivity, ScheduleActivity::class.java)
                    startActivity(intent)
                    finish()
                } else {
                    // Thông báo khi đăng nhập không thành công
                    Toast.makeText(this@LoginActivity, "Vui lòng kiểm tra lại tài khoản và mật khẩu", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
                Toast.makeText(this@LoginActivity, "Lỗi: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }
}
