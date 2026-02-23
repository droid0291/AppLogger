package com.example.smartloggertest

import android.content.Context
import android.graphics.Color
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class NetworkDemoActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_network)
        supportActionBar?.title = "Network Failures"
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        setupTimeoutSimulation()
        setupHttp500Simulation()
        setupOfflineSimulation()
    }

    // ── 1. Network Timeout ─────────────────────────────────────────────────

    private fun setupTimeoutSimulation() {
        val status = findViewById<TextView>(R.id.statusTimeout)
        val btn = findViewById<Button>(R.id.btnTriggerTimeout)

        btn.setOnClickListener {
            status.text = "⏳  Connecting to non-routable host (10.255.255.1)..."
            status.setTextColor(Color.parseColor("#FFB347"))
            btn.isEnabled = false
            Log.e("SmartLoggerTest", ">>> Network: Simulating timeout to 10.255.255.1")

            Thread {
                try {
                    val url = java.net.URL("http://10.255.255.1/api/data")
                    val conn = url.openConnection() as java.net.HttpURLConnection
                    conn.connectTimeout = 8000
                    conn.readTimeout = 8000
                    conn.connect()
                    runOnUiThread {
                        status.text = "✓  Connected (unexpected)"
                        status.setTextColor(Color.GREEN)
                    }
                } catch (e: java.net.SocketTimeoutException) {
                    Log.e("SmartLoggerTest", "Network Timeout: ${e.message}")
                    runOnUiThread {
                        status.text = "❌  SocketTimeoutException: ${e.message}\n\nBug: App shows blank screen instead of error state."
                        status.setTextColor(Color.parseColor("#FF6B6B"))
                        btn.isEnabled = true
                    }
                } catch (e: Exception) {
                    Log.e("SmartLoggerTest", "Timeout sim error: ${e.javaClass.simpleName}: ${e.message}")
                    runOnUiThread {
                        status.text = "❌  ${e.javaClass.simpleName}: ${e.message}"
                        status.setTextColor(Color.parseColor("#FF6B6B"))
                        btn.isEnabled = true
                    }
                }
            }.start()
        }
    }

    // ── 2. HTTP 500 ────────────────────────────────────────────────────────

    private fun setupHttp500Simulation() {
        val status = findViewById<TextView>(R.id.statusHttp500)
        val btn = findViewById<Button>(R.id.btnTriggerHttp500)

        btn.setOnClickListener {
            status.text = "⏳  Calling https://httpstat.us/500..."
            status.setTextColor(Color.parseColor("#FFB347"))
            btn.isEnabled = false
            Log.e("SmartLoggerTest", ">>> Network: Requesting HTTP 500 from httpstat.us")

            Thread {
                try {
                    val url = java.net.URL("https://httpstat.us/500")
                    val conn = url.openConnection() as java.net.HttpURLConnection
                    conn.connectTimeout = 8000
                    conn.readTimeout = 8000
                    val code = conn.responseCode
                    Log.e("SmartLoggerTest", "HTTP Response: $code")
                    runOnUiThread {
                        if (code >= 500) {
                            status.text = "❌  HTTP $code — Internal Server Error\n\nBug: App shows blank screen. Should display a user-friendly error message."
                            status.setTextColor(Color.parseColor("#FF6B6B"))
                        } else {
                            status.text = "✓  HTTP $code"
                            status.setTextColor(Color.GREEN)
                        }
                        btn.isEnabled = true
                    }
                } catch (e: Exception) {
                    Log.e("SmartLoggerTest", "HTTP500 error: ${e.message}")
                    runOnUiThread {
                        status.text = "❌  ${e.javaClass.simpleName}: ${e.message}"
                        status.setTextColor(Color.parseColor("#FF6B6B"))
                        btn.isEnabled = true
                    }
                }
            }.start()
        }
    }

    // ── 3. Offline ─────────────────────────────────────────────────────────

    private fun setupOfflineSimulation() {
        val status = findViewById<TextView>(R.id.statusOffline)
        val btn = findViewById<Button>(R.id.btnTriggerOffline)

        btn.setOnClickListener {
            val connected = isConnected()
            Log.e("SmartLoggerTest", ">>> Network: Offline check — connected=$connected")

            if (connected) {
                status.text = "📶  You are ONLINE.\n\nTurn off Wi-Fi + mobile data, then tap again to see the UnknownHostException in Logcat."
                status.setTextColor(Color.parseColor("#FFB347"))
            } else {
                status.text = "📵  No internet — making API call anyway (the bug)..."
                status.setTextColor(Color.parseColor("#FFB347"))
                btn.isEnabled = false

                Thread {
                    try {
                        val url = java.net.URL("https://api.example.com/data")
                        url.openConnection().connect()
                    } catch (e: java.net.UnknownHostException) {
                        Log.e("SmartLoggerTest", "Offline crash: UnknownHostException: ${e.message}")
                        runOnUiThread {
                            status.text = "❌  UnknownHostException: ${e.message}\n\nBug: App crashed instead of showing an offline banner."
                            status.setTextColor(Color.parseColor("#FF6B6B"))
                            btn.isEnabled = true
                        }
                    } catch (e: Exception) {
                        Log.e("SmartLoggerTest", "Offline error: ${e.javaClass.simpleName}: ${e.message}")
                        runOnUiThread {
                            status.text = "❌  ${e.javaClass.simpleName}: ${e.message}"
                            status.setTextColor(Color.parseColor("#FF6B6B"))
                            btn.isEnabled = true
                        }
                    }
                }.start()
            }
        }
    }

    private fun isConnected(): Boolean {
        val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = cm.activeNetwork ?: return false
        val caps = cm.getNetworkCapabilities(network) ?: return false
        return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
