package com.example.smartloggertest

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        findViewById<CardView>(R.id.cardCrash).setOnClickListener {
            startActivity(Intent(this, CrashDemoActivity::class.java))
        }
        findViewById<CardView>(R.id.cardAnr).setOnClickListener {
            startActivity(Intent(this, AnrDemoActivity::class.java))
        }
        findViewById<CardView>(R.id.cardUiBug).setOnClickListener {
            startActivity(Intent(this, UiBugDemoActivity::class.java))
        }
        findViewById<CardView>(R.id.cardNetwork).setOnClickListener {
            startActivity(Intent(this, NetworkDemoActivity::class.java))
        }
        findViewById<CardView>(R.id.cardPerformance).setOnClickListener {
            startActivity(Intent(this, PerformanceDemoActivity::class.java))
        }
        findViewById<CardView>(R.id.cardSecurity).setOnClickListener {
            startActivity(Intent(this, SecurityDemoActivity::class.java))
        }
    }
}
