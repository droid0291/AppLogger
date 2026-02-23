package com.example.smartloggertest

import android.os.Bundle
import android.util.Log
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity

class CrashDemoActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_crash)
        supportActionBar?.title = "Crash Simulations"
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        findViewById<Button>(R.id.btnTriggerNpe).setOnClickListener {
            triggerNPE()
        }
        findViewById<Button>(R.id.btnTriggerOom).setOnClickListener {
            triggerOOM()
        }
        findViewById<Button>(R.id.btnTriggerSoe).setOnClickListener {
            triggerStackOverflow()
        }
        findViewById<Button>(R.id.btnTriggerAiobe).setOnClickListener {
            triggerIndexOutOfBounds()
        }
    }

    private fun triggerNPE() {
        Log.e("SmartLoggerTest", ">>> Triggering NullPointerException")
        val result: List<String>? = loadTransactions()
        // Force-unwrap null → NullPointerException
        val count = result!!.size
        Log.d("SmartLoggerTest", "Count: $count") // never reached
    }

    private fun loadTransactions(): List<String>? = null // simulates failed network/DB call

    private fun triggerOOM() {
        Log.e("SmartLoggerTest", ">>> Triggering OutOfMemoryError — allocating until heap is full")
        val sink = mutableListOf<ByteArray>()
        while (true) {
            sink.add(ByteArray(1024 * 1024 * 10)) // 10 MB per iteration
        }
    }

    private fun triggerStackOverflow() {
        Log.e("SmartLoggerTest", ">>> Triggering StackOverflowError")
        infiniteRecursion(0)
    }

    private fun infiniteRecursion(depth: Int) {
        infiniteRecursion(depth + 1) // no base case
    }

    private fun triggerIndexOutOfBounds() {
        Log.e("SmartLoggerTest", ">>> Triggering ArrayIndexOutOfBoundsException")
        val items = listOf("apple", "banana", "cherry")
        val bad = items[99] // index 99 in a 3-item list
        Log.d("SmartLoggerTest", bad)
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
