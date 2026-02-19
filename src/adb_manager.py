import subprocess

class ADBManager:
    def __init__(self, adb_path="adb", device_serial=None):
        self.adb_path = adb_path
        self.device_serial = device_serial

    def run_command(self, cmd):
        """Executes an ADB command."""
        base_cmd = [self.adb_path]
        if self.device_serial:
            base_cmd.extend(["-s", self.device_serial])
        
        full_cmd = base_cmd + cmd
        try:
            result = subprocess.run(full_cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"ADB Error: {e.stderr}")
            return None

    def get_connected_devices(self):
        """Returns a list of connected devices."""
        output = self.run_command(["devices"])
        if not output:
            return []
        
        devices = []
        lines = output.split('\n')[1:] # Skip header
        for line in lines:
            if "\tdevice" in line:
                devices.append(line.split("\t")[0])
        return devices

    def take_screenshot(self, local_path="/tmp/screen.png"):
        """Captures a screenshot and saves it locally."""
        # 1. Capture to device temp
        self.run_command(["shell", "screencap", "-p", "/sdcard/screen.png"])
        # 2. Pull using base ADB (simpler than shell for pull)
        # Note: pull command is `adb pull remote local`
        # We need to use subprocess directly for pull if run_command appends shell or similar, 
        # but our run_command is generic.
        
        pull_cmd = ["pull", "/sdcard/screen.png", local_path]
        self.run_command(pull_cmd)
        
        # 3. Cleanup
        self.run_command(["shell", "rm", "/sdcard/screen.png"])
        return local_path

    def tap(self, x, y):
        """Simulate a tap at coordinates (x, y)."""
        self.run_command(["shell", "input", "tap", str(x), str(y)])

    def input_text(self, text):
        """Input text into the focused field."""
        # Escape spaces and special chars if needed
        # Simple implementation for now
        escaped_text = text.replace(" ", "%s") 
        self.run_command(["shell", "input", "text", escaped_text])

    def swipe(self, x1, y1, x2, y2, duration=300):
        """Simulate a swipe."""
        self.run_command(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)])

