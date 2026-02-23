package com.example.smartloggertest

import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import java.util.concurrent.locks.ReentrantLock

class AnrDemoActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_anr)
        supportActionBar?.title = "ANR Simulations"
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        val statusMainThread = findViewById<TextView>(R.id.statusMainThread)
        val statusDeadlock = findViewById<TextView>(R.id.statusDeadlock)

        findViewById<Button>(R.id.btnTriggerMainThread).setOnClickListener {
            statusMainThread.text = "Status: ⚠️ Blocking main thread for 6 seconds..."
            Log.e("SmartLoggerTest", ">>> ANR: Calling Thread.sleep(6000) on main thread")
            Toast.makeText(this, "UI is now frozen for 6s — ANR incoming!", Toast.LENGTH_SHORT).show()
            Thread.sleep(6000) // Blocks the UI thread → ANR after 5 seconds
            statusMainThread.text = "Status: Completed (ANR should have fired)"
        }

        findViewById<Button>(R.id.btnTriggerDeadlock).setOnClickListener {
            statusDeadlock.text = "Status: ⚠️ Deadlock in progress — main thread is blocked..."
            Log.e("SmartLoggerTest", ">>> ANR: Triggering deadlock between two threads")
            Toast.makeText(this, "Deadlock started — main thread will block forever", Toast.LENGTH_SHORT).show()
            simulateDeadlock()
        }
    }

    private fun simulateDeadlock() {
        val lock1 = ReentrantLock()
        val lock2 = ReentrantLock()

        val thread1 = Thread {
            lock1.lock()
            try {
                Log.d("SmartLoggerTest", "Thread1 acquired lock1, waiting for lock2")
                Thread.sleep(100)
                lock2.lock()  // will block forever — thread2 holds lock2
                try {
                    Log.d("SmartLoggerTest", "Thread1 acquired lock2 (deadlock resolved)")
                } finally {
                    lock2.unlock()
                }
            } finally {
                lock1.unlock()
            }
        }

        val thread2 = Thread {
            lock2.lock()
            try {
                Log.d("SmartLoggerTest", "Thread2 acquired lock2, waiting for lock1")
                Thread.sleep(100)
                lock1.lock()  // will block forever — thread1 holds lock1
                try {
                    Log.d("SmartLoggerTest", "Thread2 acquired lock1 (deadlock resolved)")
                } finally {
                    lock1.unlock()
                }
            } finally {
                lock2.unlock()
            }
        }

        thread1.start()
        thread2.start()

        // Main thread joins both — blocks indefinitely → ANR
        thread1.join()
        thread2.join()
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
