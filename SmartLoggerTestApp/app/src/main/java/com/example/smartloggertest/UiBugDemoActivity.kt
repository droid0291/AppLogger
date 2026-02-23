package com.example.smartloggertest

import android.graphics.Color
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class UiBugDemoActivity : AppCompatActivity() {

    private var overlapFixed = false
    private var truncationFixed = false
    private var contrastFixed = false
    private var imageFixed = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_ui_bug)
        supportActionBar?.title = "UI Bug Simulations"
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        setupOverlapDemo()
        setupTruncationDemo()
        setupContrastDemo()
        setupImageDemo()
    }

    // ── 1. Overlapping Views ───────────────────────────────────────────────

    private fun setupOverlapDemo() {
        val overlayText = findViewById<TextView>(R.id.demoOverlapText)
        val toggleBtn = findViewById<Button>(R.id.btnToggleOverlap)

        Log.w("SmartLoggerTest", "UI Bug: Overlapping view is visible on screen")

        toggleBtn.setOnClickListener {
            overlapFixed = !overlapFixed
            if (overlapFixed) {
                overlayText.visibility = View.GONE
                toggleBtn.text = "Toggle: Show Bug (overlap)"
                Log.d("SmartLoggerTest", "UI Fix: Overlap removed")
            } else {
                overlayText.visibility = View.VISIBLE
                toggleBtn.text = "Toggle: Show Fix"
                Log.w("SmartLoggerTest", "UI Bug: Overlap re-introduced")
            }
        }
    }

    // ── 2. Text Truncation ─────────────────────────────────────────────────

    private fun setupTruncationDemo() {
        val textView = findViewById<TextView>(R.id.demoTruncText)
        val toggleBtn = findViewById<Button>(R.id.btnToggleTruncation)

        Log.w("SmartLoggerTest", "UI Bug: Long username with no ellipsize — text will overflow container")

        toggleBtn.setOnClickListener {
            truncationFixed = !truncationFixed
            if (truncationFixed) {
                textView.maxLines = 1
                textView.ellipsize = android.text.TextUtils.TruncateAt.END
                toggleBtn.text = "Toggle: Show Bug (no ellipsize)"
                Log.d("SmartLoggerTest", "UI Fix: Added maxLines=1 + ellipsize=END")
            } else {
                textView.maxLines = Integer.MAX_VALUE
                textView.ellipsize = null
                toggleBtn.text = "Toggle: Show Fix (ellipsize)"
                Log.w("SmartLoggerTest", "UI Bug: Removed ellipsize — text overflows again")
            }
        }
    }

    // ── 3. Low Contrast ───────────────────────────────────────────────────

    private fun setupContrastDemo() {
        val button = findViewById<Button>(R.id.demoContrastButton)
        val toggleBtn = findViewById<Button>(R.id.btnToggleContrast)

        Log.w("SmartLoggerTest", "UI Bug: Button has near-white text on white background — WCAG contrast fail")

        toggleBtn.setOnClickListener {
            contrastFixed = !contrastFixed
            if (contrastFixed) {
                // Fix: high-contrast
                button.setBackgroundColor(Color.parseColor("#1565C0"))
                button.setTextColor(Color.WHITE)
                button.text = "Submit Payment ✓ (Fixed)"
                toggleBtn.text = "Toggle: Show Bug (low contrast)"
                Log.d("SmartLoggerTest", "UI Fix: High-contrast button colors applied")
            } else {
                // Bug: near-invisible text
                button.setBackgroundColor(Color.WHITE)
                button.setTextColor(Color.parseColor("#EEEEEE"))
                button.text = "Submit Payment"
                toggleBtn.text = "Toggle: Show Fix (proper contrast)"
                Log.w("SmartLoggerTest", "UI Bug: Low-contrast white-on-white button re-applied")
            }
        }
    }

    // ── 4. Missing Image ─────────────────────────────────────────────────

    private fun setupImageDemo() {
        val imageView = findViewById<ImageView>(R.id.demoImageView)
        val toggleBtn = findViewById<Button>(R.id.btnToggleImage)

        Log.w("SmartLoggerTest", "UI Bug: ImageView has no src — blank placeholder shown to user")

        toggleBtn.setOnClickListener {
            imageFixed = !imageFixed
            if (imageFixed) {
                // Fix: use a built-in Android placeholder drawable
                imageView.setImageResource(android.R.drawable.ic_menu_gallery)
                imageView.setBackgroundColor(Color.parseColor("#1A237E"))
                toggleBtn.text = "Toggle: Show Bug (missing image)"
                Log.d("SmartLoggerTest", "UI Fix: Placeholder drawable applied to ImageView")
            } else {
                // Bug: empty image
                imageView.setImageDrawable(null)
                imageView.setBackgroundColor(Color.parseColor("#222233"))
                toggleBtn.text = "Toggle: Show Fix (placeholder)"
                Log.w("SmartLoggerTest", "UI Bug: ImageView src cleared — blank space visible")
            }
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
