class LogAnalyzer:
    """
    Platform-agnostic log analyser.
    Works with any DeviceManager (AndroidManager or IOSManager)
    passed in as `adb_manager`.
    """

    def __init__(self, adb_manager, gemini_client):
        self.adb    = adb_manager
        self.gemini = gemini_client

    # ── Log extraction ────────────────────────────────────────────────────────

    def extract_logcat(self, output_file: str = "logs/logcat.txt",
                       filter_level: str = "E") -> str | None:
        """Extract a snapshot of logs from the device."""
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        if getattr(self.adb, "platform", "android") == "ios":
            # iOS: run idevicesyslog with --match for errors only
            cmd = self.adb.logcat_command()
            # static snapshot is awkward for iOS; return None and rely on live stream
            return None
        else:
            cmd  = ["logcat", "-d", f"*:{filter_level}"]
            output = self.adb.run_command(cmd)
            if output:
                with open(output_file, "w") as f:
                    f.write(output)
                return output_file
        return None

    def extract_crash_logs(self, output_file: str = "logs/crash.txt") -> str | None:
        """Extract the last 500 log lines for crash analysis."""
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        if getattr(self.adb, "platform", "android") == "ios":
            return None   # live stream handled by GUI; no batch pull on iOS
        else:
            output = self.adb.run_command(["logcat", "-d", "-t", "500"])
            if output:
                with open(output_file, "w") as f:
                    f.write(output)
                return output_file
        return None

    # ── AI analysis ───────────────────────────────────────────────────────────

    def analyze_logs_with_ai(self, log_file: str) -> str | None:
        if not log_file:
            return "No log file provided"
        try:
            with open(log_file) as f:
                log_content = f.read()
            if not log_content.strip():
                return "Log file is empty"

            platform = getattr(self.adb, "platform", "android")
            os_label = "iOS" if platform == "ios" else "Android"

            prompt = (
                f"Analyse the following {os_label} crash log and provide:\n"
                "1. Root cause of the crash\n"
                "2. Specific line/method where it occurred\n"
                "3. Suggested fix for the developer\n"
                "4. Severity assessment (Critical/High/Medium/Low)\n\n"
                f"Log:\n{log_content[:5000]}"
            )
            if hasattr(self.gemini, "analyze_text"):
                return self.gemini.analyze_text(prompt)
            return "Gemini client not properly initialized"
        except Exception as e:
            print(f"Error analyzing logs: {e}")
            return None

    # ── Device info ───────────────────────────────────────────────────────────

    def get_device_info(self) -> dict:
        """Delegate to the active DeviceManager."""
        if hasattr(self.adb, "get_device_info"):
            return self.adb.get_device_info()
        return {}
