package com.example.smartloggertest

import android.graphics.Color
import android.os.Bundle
import android.util.Log
import android.view.WindowManager
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.switchmaterial.SwitchMaterial

class SecurityDemoActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_security)
        supportActionBar?.title = "Security Simulations"
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        setupPiiLogging()
        setupFlagSecure()
    }

    // ── 1. PII in Logcat ───────────────────────────────────────────────────

    private fun setupPiiLogging() {
        val preview = findViewById<TextView>(R.id.piiPreview)
        val btn = findViewById<Button>(R.id.btnLogPii)

        btn.setOnClickListener {
            val logLines = buildString {
                appendLine("D/SmartLoggerTest: user_email=john.doe@example.com password=SuperSecret123")
                appendLine("D/SmartLoggerTest: auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.faketoken")
                appendLine("D/SmartLoggerTest: credit_card=4111-1111-1111-1111 cvv=123 expiry=12/26")
                appendLine("D/SmartLoggerTest: ssn=123-45-6789")
            }

            // Write to actual Logcat
            Log.d("SmartLoggerTest", "user_email=john.doe@example.com password=SuperSecret123")
            Log.d("SmartLoggerTest", "auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.faketoken")
            Log.d("SmartLoggerTest", "credit_card=4111-1111-1111-1111 cvv=123 expiry=12/26")
            Log.d("SmartLoggerTest", "ssn=123-45-6789")

            // Show in the on-screen preview
            preview.text = logLines
            preview.setTextColor(Color.parseColor("#44FF88"))

            Toast.makeText(
                this,
                "PII written to Logcat! SmartLogger will detect this in your log analysis.",
                Toast.LENGTH_LONG
            ).show()
        }
    }

    // ── 2. FLAG_SECURE Toggle ─────────────────────────────────────────────

    private fun setupFlagSecure() {
        val toggle = findViewById<SwitchMaterial>(R.id.secureToggle)
        val status = findViewById<TextView>(R.id.statusSecure)

        toggle.isChecked = false

        toggle.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                window.setFlags(
                    WindowManager.LayoutParams.FLAG_SECURE,
                    WindowManager.LayoutParams.FLAG_SECURE
                )
                status.text = "🔒  STATUS: SECURE — screenshots blocked by OS"
                status.setTextColor(Color.parseColor("#6BFF9F"))
                status.setBackgroundColor(Color.parseColor("#0A1A0A"))
                Log.d("SmartLoggerTest", "Security: FLAG_SECURE enabled — ADB screenshot will fail")
                Toast.makeText(this, "FLAG_SECURE ON — try capturing a screenshot now!", Toast.LENGTH_SHORT).show()
            } else {
                window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE)
                status.text = "🔓  STATUS: INSECURE — screenshots allowed"
                status.setTextColor(Color.parseColor("#FF6B6B"))
                status.setBackgroundColor(Color.parseColor("#1A0A0A"))
                Log.w("SmartLoggerTest", "Security: FLAG_SECURE disabled — screen can be captured")
            }
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
