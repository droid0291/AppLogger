package com.example.smartloggertest

import android.os.Bundle
import android.view.WindowManager
import android.widget.Button
import android.widget.EditText
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.switchmaterial.SwitchMaterial

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val secureToggle = findViewById<SwitchMaterial>(R.id.secureToggle)
        val inputField = findViewById<EditText>(R.id.inputField)
        val crashButton = findViewById<Button>(R.id.crashButton)

        secureToggle.setOnCheckedChangeListener { _, isChecked ->
            setSecureFlag(isChecked)
        }

        crashButton.setOnClickListener {
            // Simulate a realistic crash scenario
            simulateCrash()
        }
    }

    private fun setSecureFlag(isSecure: Boolean) {
        if (isSecure) {
            window.setFlags(
                WindowManager.LayoutParams.FLAG_SECURE,
                WindowManager.LayoutParams.FLAG_SECURE
            )
        } else {
            window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE)
        }
    }

    private fun simulateCrash() {
        // Simulate a realistic banking app crash
        val transactions = loadTransactions()
        val balance = calculateBalance(transactions)
        updateUI(balance)
    }

    private fun loadTransactions(): List<String>? {
        // Simulate network/database call that returns null
        return null
    }

    private fun calculateBalance(transactions: List<String>?): Double {
        // This will crash with NPE when transactions is null
        return transactions!!.size.toDouble() * 100.0
    }

    private fun updateUI(balance: Double) {
        // Never reached due to crash
    }
}
