package com.example.smartloggertest

import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class PerformanceDemoActivity : AppCompatActivity() {

    companion object {
        val leakedViews = mutableListOf<Any>()
    }

    private var cpuThread: Thread? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_performance)
        supportActionBar?.title = "Performance Simulations"
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        setupMemoryLeak()
        setupCpuSpike()
    }

    // ── 1. Memory Leak ─────────────────────────────────────────────────────

    private fun setupMemoryLeak() {
        val statusView = findViewById<TextView>(R.id.statusMemory)
        val leakBtn = findViewById<Button>(R.id.btnLeakMemory)
        val clearBtn = findViewById<Button>(R.id.btnClearLeak)

        fun updateStatus() {
            statusView.text = "Leaked views: ${leakedViews.size}"
        }

        leakBtn.setOnClickListener {
            Log.w("SmartLoggerTest", ">>> Memory Leak: Adding 500 views to static list (Activity context retained)")
            repeat(500) {
                leakedViews.add(TextView(this).apply { text = "Leaked #$it" })
            }
            updateStatus()
            Toast.makeText(
                this,
                "Leaked ${leakedViews.size} views total. Rotate screen — memory will NOT be freed.",
                Toast.LENGTH_LONG
            ).show()
        }

        clearBtn.setOnClickListener {
            leakedViews.clear()
            updateStatus()
            Log.d("SmartLoggerTest", "Memory Leak: Cleared leaked view list")
            Toast.makeText(this, "Cleared! GC can now reclaim memory.", Toast.LENGTH_SHORT).show()
        }

        updateStatus()
    }

    // ── 2. CPU Spike ───────────────────────────────────────────────────────

    private fun setupCpuSpike() {
        val statusView = findViewById<TextView>(R.id.statusCpu)
        val spikeBtn = findViewById<Button>(R.id.btnCpuSpike)

        spikeBtn.setOnClickListener {
            if (cpuThread?.isAlive == true) {
                cpuThread?.interrupt()
                spikeBtn.text = "▶ Start CPU Spike (15s)"
                statusView.text = "CPU Spike: Stopped by user"
                Log.d("SmartLoggerTest", "CPU Spike stopped")
                return@setOnClickListener
            }

            Log.w("SmartLoggerTest", ">>> Performance: Starting CPU busy loop for 15 seconds")
            spikeBtn.text = "⏹ Stop CPU Spike"
            statusView.text = "CPU Spike: 🔥 Running..."

            cpuThread = Thread {
                val end = System.currentTimeMillis() + 15_000
                var iterations = 0L
                while (!Thread.interrupted() && System.currentTimeMillis() < end) {
                    Math.sqrt(Math.random() * Math.random())
                    iterations++
                    if (iterations % 1_000_000 == 0L) {
                        val remaining = (end - System.currentTimeMillis()) / 1000
                        runOnUiThread {
                            if (!isFinishing) {
                                statusView.text = "CPU Spike: 🔥 Running... ${remaining}s remaining"
                            }
                        }
                    }
                }
                Log.d("SmartLoggerTest", "CPU Spike ended after $iterations iterations")
                runOnUiThread {
                    if (!isFinishing) {
                        spikeBtn.text = "▶ Start CPU Spike (15s)"
                        statusView.text = "CPU Spike: Idle (completed)"
                    }
                }
            }
            cpuThread!!.start()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        cpuThread?.interrupt()
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
