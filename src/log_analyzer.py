class LogAnalyzer:
    def __init__(self, adb_manager, gemini_client):
        self.adb = adb_manager
        self.gemini = gemini_client

    def extract_logcat(self, output_file="logs/logcat.txt", filter_level="E"):
        """Extract logcat from device, optionally filtered by log level."""
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Get logcat (errors only by default)
        cmd = ["logcat", "-d", f"*:{filter_level}"]
        output = self.adb.run_command(cmd)
        
        if output:
            with open(output_file, 'w') as f:
                f.write(output)
            print(f"Logcat saved to {output_file}")
            return output_file
        return None

    def extract_crash_logs(self, output_file="logs/crash.txt"):
        """Extract comprehensive logs for analysis."""
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Get full logcat (last 500 lines for context)
        cmd = ["logcat", "-d", "-t", "500"]
        output = self.adb.run_command(cmd)
        
        if output:
            # Save all relevant logs for AI analysis
            with open(output_file, 'w') as f:
                f.write(output)
            print(f"Logs saved to {output_file}")
            return output_file
        
        return None

    def analyze_logs_with_ai(self, log_file):
        """Use Gemini to analyze logs and suggest fixes."""
        if not log_file:
            return "No log file provided"
            
        try:
            with open(log_file, 'r') as f:
                log_content = f.read()
            
            if not log_content.strip():
                return "Log file is empty"
            
            prompt = f"""Analyze the following Android crash log and provide:
1. Root cause of the crash
2. Specific line/method where it occurred
3. Suggested fix for the developer
4. Severity assessment (Critical/High/Medium/Low)

Log:
{log_content[:5000]}  
"""  # Limit to 5000 chars to avoid token limits
            
            # Use the gemini client's analyze_text method
            if hasattr(self.gemini, 'analyze_text'):
                analysis = self.gemini.analyze_text(prompt)
            else:
                analysis = "Gemini client not properly initialized"
            
            return analysis
        except Exception as e:
            print(f"Error analyzing logs: {e}")
            return None

    def get_device_info(self):
        """Get device information for bug report context."""
        info = {}
        
        # Device model
        model = self.adb.run_command(["shell", "getprop", "ro.product.model"])
        info['model'] = model.strip() if model else "Unknown"
        
        # Android version
        version = self.adb.run_command(["shell", "getprop", "ro.build.version.release"])
        info['android_version'] = version.strip() if version else "Unknown"
        
        # Build number
        build = self.adb.run_command(["shell", "getprop", "ro.build.display.id"])
        info['build'] = build.strip() if build else "Unknown"
        
        return info
