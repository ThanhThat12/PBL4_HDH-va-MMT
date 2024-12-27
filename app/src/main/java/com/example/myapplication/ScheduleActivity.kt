package com.example.myapplication

import android.content.DialogInterface
import android.content.Intent
import android.content.res.ColorStateList
import android.os.Bundle
import android.widget.Button
import android.widget.ImageButton
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment


class ScheduleActivity : AppCompatActivity() {

    private lateinit var btnPersonal: Button
    private lateinit var btnLhn: Button
    private lateinit var btnLichHoc: Button
    private lateinit var btnLichThi: Button
    private lateinit var btnHocPhi: Button
    private lateinit var btnLogout: ImageButton

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_schedule)

        // Initialize buttons
        btnPersonal = findViewById(R.id.btnpersonal)
        btnLhn = findViewById(R.id.btnlhn)
        btnLichHoc = findViewById(R.id.btnlichhoc)
        btnLichThi = findViewById(R.id.btnlichthi)
        btnHocPhi = findViewById(R.id.btnhocphi)
        btnLogout = findViewById(R.id.buttonLogout)

        val buttons = listOf(btnPersonal, btnLhn, btnLichHoc, btnLichThi, btnHocPhi)

        // Set default fragment
        if (savedInstanceState == null) {
            openFragment(PersonalFragment())

        }

        // Reset button styles
        fun resetAllButtons() {
            for (button in buttons) {
                button.setTextColor(resources.getColor(android.R.color.black, null))
                button.compoundDrawableTintList =
                    ColorStateList.valueOf(resources.getColor(android.R.color.black, null))
            }
        }

        // Highlight selected button
        fun highlightButton(button: Button) {
            resetAllButtons()
            button.setTextColor(resources.getColor(android.R.color.holo_red_light, null))
            button.compoundDrawableTintList =
                ColorStateList.valueOf(resources.getColor(android.R.color.holo_red_light, null))
        }

        // Handle button clicks
        btnPersonal.setOnClickListener {
            highlightButton(btnPersonal)
            openFragment(PersonalFragment())
        }

        btnLhn.setOnClickListener {
            highlightButton(btnLhn)
            openFragment(ScheduleFragment())
        }

        btnLichHoc.setOnClickListener {
            highlightButton(btnLichHoc)
            openFragment(Schedule2Fragment())
        }

        btnLichThi.setOnClickListener {
            highlightButton(btnLichThi)
            openFragment(ExamFragment())
        }

        btnHocPhi.setOnClickListener {
            highlightButton(btnHocPhi)
            openFragment(TuitionFragment())
        }
        // Handle logout button click
        btnLogout.setOnClickListener {
            showLogoutConfirmation()
        }

    }

    private fun openFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragment_container, fragment)
            .addToBackStack(null)
            .commit()
    }
    private fun showLogoutConfirmation() {
        AlertDialog.Builder(this)
            .setTitle("Xác nhận đăng xuất")
            .setMessage("Bạn có chắc chắn muốn đăng xuất?")
            .setPositiveButton("Có") { _, _ ->
                val intent = Intent(this, MainActivity::class.java)
                intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_NEW_TASK
                startActivity(intent)
                finish()
            }
            .setNegativeButton("Không", null)
            .show()
    }

}

