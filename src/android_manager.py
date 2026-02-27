"""
Android device manager — wraps ADB.
Implements the DeviceManager interface so all platform-agnostic code
(GUI, LogAnalyzer, VideoRecorder) works without knowing about ADB.
"""

import subprocess
from src.device_manager import DeviceManager


class AndroidManager(DeviceManager):
    """ADB-backed implementation of DeviceManager for Android devices."""

    def __init__(self, adb_path: str = "adb", device_serial: str = None):
        self.adb_path = adb_path
        self.device_serial = device_serial

    # ── Platform identity ─────────────────────────────────────────────────────

    @property
    def platform(self) -> str:
        return "android"

    @property
    def app_id_label(self) -> str:
        return "Package"

    # ── Device discovery ──────────────────────────────────────────────────────

    def set_device(self, device_id: str):
        self.device_serial = device_id

    def get_connected_devices(self) -> list:
        """Return list of connected ADB device serials."""
        print("[ADB] Fetching connected devices...")
        output = self.run_command(["devices"])
        if not output:
             print("[ADB] Run command returned no output for devices.")
             return []
        devices = []
        for line in output.split("\n")[1:]:
            if "\tdevice" in line:
                devices.append(line.split("\t")[0])
        print(f"[ADB] Found {len(devices)} connected device(s): {devices}")
        return devices

    # ── Shell / command execution ─────────────────────────────────────────────

    def run_command(self, cmd: list, timeout: int = 10) -> "Optional[str]":
        """Run an ADB command and return stdout."""
        base = [self.adb_path]
        if self.device_serial:
            base += ["-s", self.device_serial]
        try:
            result = subprocess.run(
                base + cmd, capture_output=True, text=True, check=True, timeout=timeout)
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            print(f"ADB Error: command {' '.join(cmd)} timed out after {timeout}s")
            return None
        except subprocess.CalledProcessError as e:
            print(f"ADB Error: {e.stderr.strip()}")
            return None

    # ── App management ────────────────────────────────────────────────────────

    def list_installed_apps(self) -> list:
        """Return third-party package names."""
        print(f"[ADB] Fetching installed apps for device {self.device_serial or 'default'}...")
        out = self.run_command(["shell", "pm", "list", "packages", "-3"])
        if not out:
            print("[ADB] Run command returned no output for packages.")
            return []
        packages = []
        for line in out.splitlines():
            if line.startswith("package:"):
                packages.append(line[len("package:"):].strip())
        
        packages = sorted(packages)
        print(f"[ADB] Found {len(packages)} installed packages.")
        
        fg_app = self.get_foreground_app()
        if fg_app:
            print(f"[ADB] Foreground app detected: {fg_app}")
            if fg_app in packages:
                packages.remove(fg_app)
            packages.insert(0, fg_app)
        else:
            print("[ADB] No foreground app detected.")
            
        return packages

    def get_foreground_app(self) -> str:
        """Return the package name of the app currently in the foreground."""
        print("[ADB] Determining foreground application...")
        import re
        
        # Method 1: dumpsys window
        out = self.run_command(["shell", "dumpsys", "window", "windows"])
        if out:
            for line in out.splitlines():
                if "mCurrentFocus" in line or "mFocusedApp" in line:
                    match = re.search(r' u0 ([a-zA-Z0-9_.]+)/', line)
                    if match:
                        return match.group(1)
                        
        # Method 2: dumpsys activity (fallback for newer Android versions)
        print("[ADB] Falling back to dumpsys activity...")
        out2 = self.run_command(["shell", "dumpsys", "activity", "activities"])
        if out2:
            for line in out2.splitlines():
                if "mResumedActivity" in line or "topResumedActivity" in line:
                    match = re.search(r' u0 ([a-zA-Z0-9_.]+)/', line)
                    if match:
                        return match.group(1)
        
        return ""

    def get_pid(self, app_id: str) -> str:
        """Return PID of the running package, or ''."""
        out = self.run_command(["shell", "pidof", app_id])
        return out.strip() if out else ""

    # ── Device info ───────────────────────────────────────────────────────────

    def get_device_info(self) -> dict:
        def prop(key):
            v = self.run_command(["shell", "getprop", key])
            return v.strip() if v else "Unknown"
        return {
            "model":           prop("ro.product.model"),
            "android_version": prop("ro.build.version.release"),
            "os_version":      prop("ro.build.version.release"),  # alias
            "build":           prop("ro.build.display.id"),
        }

    # ── Screen capture ────────────────────────────────────────────────────────

    def take_screenshot(self, local_path: str = "/tmp/screen.png") -> str:
        self.run_command(["shell", "screencap", "-p", "/sdcard/screen.png"])
        self.run_command(["pull", "/sdcard/screen.png", local_path])
        self.run_command(["shell", "rm", "/sdcard/screen.png"])
        return local_path

    # ── Log streaming ─────────────────────────────────────────────────────────

    def logcat_command(self, app_id: str = "", pid: str = "", min_level: str = "") -> list:
        """Return the adb logcat command to stream logs."""
        base = [self.adb_path]
        if self.device_serial:
            base += ["-s", self.device_serial]
        cmd = base + ["logcat", "-v", "threadtime"]
        if pid:
            cmd += [f"--pid={pid}"]
        if min_level:
            cmd += [f"*:{min_level}"]
        return cmd

    # ── Legacy helpers (kept for existing callers) ────────────────────────────

    def tap(self, x, y):
        self.run_command(["shell", "input", "tap", str(x), str(y)])

    def input_text(self, text):
        self.run_command(["shell", "input", "text", text.replace(" ", "%s")])

    def swipe(self, x1, y1, x2, y2, duration=300):
        self.run_command(["shell", "input", "swipe",
                          str(x1), str(y1), str(x2), str(y2), str(duration)])
