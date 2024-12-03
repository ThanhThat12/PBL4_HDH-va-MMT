package com.example.myapplication

import AnnouncementAdapter
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.Gravity
import android.widget.Button
import android.widget.ImageButton
import androidx.appcompat.app.ActionBarDrawerToggle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GravityCompat
import androidx.drawerlayout.widget.DrawerLayout
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.navigation.NavigationView
import okhttp3.OkHttpClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

class MainActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var announcementAdapter: AnnouncementAdapter
    private lateinit var apiService: ApiService
    private var announcements: MutableList<Announcement> = mutableListOf()
    private lateinit var drawerLayout: DrawerLayout

    // Track the currently selected button
    private var selectedButtonId: Int = R.id.buttonApi1 // Default to buttonApi1

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize DrawerLayout
        drawerLayout = findViewById(R.id.drawer_layout)

        // Initialize NavigationView
        val navigationView: NavigationView = findViewById(R.id.nav_view)

        // Create toggle for Drawer
        val toggle = ActionBarDrawerToggle(
            this, drawerLayout, R.string.navigation_drawer_open, R.string.navigation_drawer_close
        )
        drawerLayout.addDrawerListener(toggle)
        toggle.syncState()

        // Set item click listener for NavigationView
        navigationView.setNavigationItemSelectedListener { menuItem ->
            when (menuItem.itemId) {
                R.id.nav_calendar -> {
                    Log.d("MainActivity", "Calendar selected")
                    true
                }
                R.id.nav_contacts -> {
                    Log.d("MainActivity", "Contacts selected")
                    true
                }
                else -> false
            }
        }


        // Initialize Login button
        val buttonLogin: ImageButton = findViewById(R.id.buttonLogin)
        buttonLogin.setOnClickListener {
            val intent = Intent(this, LoginActivity::class.java)
            startActivity(intent)
        }

        // Initialize Menu button
        val buttonMenu: Button = findViewById(R.id.buttonMenu)
        buttonMenu.setOnClickListener {
            drawerLayout.openDrawer(GravityCompat.START) // Open drawer from left
        }

        // Initialize RecyclerView
        recyclerView = findViewById(R.id.recyclerView)
        recyclerView.layoutManager = LinearLayoutManager(this)

        // Initialize adapter with an empty list
        announcementAdapter = AnnouncementAdapter(announcements)
        recyclerView.adapter = announcementAdapter

        // Create OkHttpClient for HTTP requests with timeouts
        val okHttpClient = OkHttpClient.Builder()
            .connectTimeout(60, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .build()

        // Initialize Retrofit with the base URL
        val retrofit = Retrofit.Builder()
            .baseUrl("http://10.0.2.2:5000/") // Localhost for Android emulator
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        // Initialize ApiService for API calls
        apiService = retrofit.create(ApiService::class.java)

        // Map buttons to API calls
        val buttonApi1: Button = findViewById(R.id.buttonApi1)
        val buttonApi2: Button = findViewById(R.id.buttonApi2)

        // Set click listener for buttonApi1
        buttonApi1.setOnClickListener {
            getAnnouncements(apiService.getAnnouncementsTab0())
            updateButtonSelection(buttonApi1.id) // Update selected button state
        }

        // Set click listener for buttonApi2
        buttonApi2.setOnClickListener {
            getAnnouncements(apiService.getAnnouncementsTab1())
            updateButtonSelection(buttonApi2.id) // Update selected button state
        }

        // Update colors for initially selected buttons
        updateButtonSelection(selectedButtonId)
    }

    // Update color for selected buttons
    private fun updateButtonSelection(selectedId: Int) {
        val buttonApi1: Button = findViewById(R.id.buttonApi1)
        val buttonApi2: Button = findViewById(R.id.buttonApi2)

        // Update color for selected button
        if (selectedId == buttonApi1.id) {
            buttonApi1.setTextColor(getColor(R.color.colorAccent)) // Change this color as desired
            buttonApi2.setTextColor(getColor(android.R.color.black)) // Default color
        } else {
            buttonApi2.setTextColor(getColor(R.color.colorAccent)) // Change this color as desired
            buttonApi1.setTextColor(getColor(android.R.color.black)) // Default color
        }
        selectedButtonId = selectedId // Update state
    }

    // Handle API results and update RecyclerView
    private fun getAnnouncements(call: Call<List<Announcement>>) {
        call.enqueue(object : Callback<List<Announcement>> {
            override fun onResponse(call: Call<List<Announcement>>, response: Response<List<Announcement>>) {
                if (response.isSuccessful) {
                    response.body()?.let {
                        announcements.clear() // Clear old data
                        announcements.addAll(it) // Add new data
                        announcementAdapter.notifyDataSetChanged() // Notify adapter
                        Log.d("MainActivity", "Announcements: $it")
                    }
                } else {
                    Log.e("MainActivity", "Error: ${response.code()}")
                }
            }

            override fun onFailure(call: Call<List<Announcement>>, t: Throwable) {
                Log.e("MainActivity", "Failure: ${t.message}", t)
            }
        })
    }

    // Handle back press to close drawer
    override fun onBackPressed() {
        if (drawerLayout.isDrawerOpen(GravityCompat.START)) {
            drawerLayout.closeDrawer(GravityCompat.START)
        } else {
            super.onBackPressed()
        }
    }
}
