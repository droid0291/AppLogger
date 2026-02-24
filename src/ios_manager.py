"""
iOS device manager — wraps libimobiledevice CLI tools.
Implements the DeviceManager interface using:
  • idevice_id       – list connected devices
  • ideviceinfo      – device metadata
  • idevicescreenshot – screenshots
  • idevicesyslog    – log streaming
  • ideviceinstaller – app list

Requirements (macOS):
  brew install libimobiledevice ideviceinstaller
"""

import subprocess
import shutil
from src.device_manager import DeviceManager


def _tool_available(name: str) -> bool:
    return shutil.which(name) is not None


class IOSManager(DeviceManager):
    """libimobiledevice-backed implementation of DeviceManager for iOS devices."""

    def __init__(self, udid: str = None):
        self.udid = udid          # None → first connected device
        self._sim_mode = False    # set True if a simulator UDID is detected

    # ── Platform identity ─────────────────────────────────────────────────────

    @property
    def platform(self) -> str:
        return "ios"

    @property
    def app_id_label(self) -> str:
        return "Bundle ID"

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _base_args(self, tool: str) -> list:
        """Return [tool, -u, udid] if a UDID is selected, else [tool]."""
        cmd = [tool]
        if self.udid:
            cmd += ["-u", self.udid]
        return cmd

    def _run(self, cmd: list, timeout: int = 10) -> "Optional[str]":
        """Run an external command and return stdout, or None on failure."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout)
            if result.returncode == 0:
                return result.stdout.strip()
            print(f"iOS tool error ({cmd[0]}): {result.stderr.strip()}")
            return None
        except FileNotFoundError:
            print(f"❌  '{cmd[0]}' not found — run: brew install libimobiledevice")
            return None
        except subprocess.TimeoutExpired:
            print(f"⏱  '{cmd[0]}' timed out")
            return None

    def _is_simulator(self, udid: str) -> bool:
        """Simulators have a UUID format rather than a hex UDID."""
        return "-" in udid and len(udid) == 36

    # ── Device discovery ──────────────────────────────────────────────────────

    def set_device(self, device_id: str):
        self.udid = device_id
        self._sim_mode = self._is_simulator(device_id)

    def get_connected_devices(self) -> list:
        """Return list of real-device UDIDs + booted simulator UDIDs."""
        devices = []

        # Real devices via idevice_id
        if _tool_available("idevice_id"):
            out = self._run(["idevice_id", "-l"])
            if out:
                devices += [d.strip() for d in out.splitlines() if d.strip()]

        # Booted simulators via xcrun simctl
        sim_out = self._run(["xcrun", "simctl", "list", "devices", "booted", "-j"], timeout=15)
        if sim_out:
            import json
            try:
                data = json.loads(sim_out)
                for runtime_devices in data.get("devices", {}).values():
                    for dev in runtime_devices:
                        if dev.get("state") == "Booted":
                            devices.append(dev["udid"])
            except (json.JSONDecodeError, KeyError):
                pass

        return devices

    # ── Shell / command execution ─────────────────────────────────────────────

    def run_command(self, cmd: list) -> "Optional[str]":
        """
        Generic command runner. For iOS most operations use dedicated
        libimobiledevice tools, but this handles ad-hoc subprocess needs.
        """
        return self._run(cmd)

    # ── App management ────────────────────────────────────────────────────────

    def list_installed_apps(self) -> list:
        """Return installed user app bundle IDs."""
        if self._sim_mode:
            # Simulators: parse the app registry
            return self._list_sim_apps()

        if not _tool_available("ideviceinstaller"):
            print("⚠  ideviceinstaller not found — run: brew install ideviceinstaller")
            return []

        out = self._run(self._base_args("ideviceinstaller") + ["-l"])
        if not out:
            return []

        bundles = []
        for line in out.splitlines():
            # Format: com.example.App, 1.0, SomeApp
            if "," in line and not line.startswith("Total"):
                bundles.append(line.split(",")[0].strip())
        return sorted(bundles)

    def _list_sim_apps(self) -> list:
        """Return bundle IDs of user apps installed in the selected simulator.

        simctl listapps outputs a GNUstep old-style property list that neither
        Python's json nor plistlib can parse.  We pipe through macOS's built-in
        `plutil -convert json` to get proper JSON first.
        """
        try:
            # Step 1: get raw plist text from simctl
            p1 = subprocess.run(
                ["xcrun", "simctl", "listapps", self.udid],
                capture_output=True, timeout=15)
            if p1.returncode != 0 or not p1.stdout:
                return []

            # Step 2: convert to JSON via plutil (always available on macOS)
            p2 = subprocess.run(
                ["plutil", "-convert", "json", "-o", "-", "-"],
                input=p1.stdout, capture_output=True, timeout=10)
            if p2.returncode != 0:
                return []

            import json
            data = json.loads(p2.stdout)
            # Filter to user-installed apps only (ApplicationType == "User")
            return sorted(
                k for k, v in data.items()
                if v.get("ApplicationType") == "User"
            )
        except Exception as e:
            print(f"iOS sim app list error: {e}")
            return []




    def get_pid(self, app_id: str) -> str:
        """
        Return PID of a running iOS app (real device only).
        For simulators the PID is not needed — syslog filtering uses the
        process name from the bundle ID instead.
        """
        if self._sim_mode:
            return ""
        # idevicesyslog doesn't expose PIDs easily so we skip this for now
        return ""

    # ── Device info ───────────────────────────────────────────────────────────

    def get_device_info(self) -> dict:
        if self._sim_mode:
            return self._sim_device_info()

        if not _tool_available("ideviceinfo"):
            return {"model": "Unknown", "os_version": "Unknown", "build": "Unknown"}

        def prop(key):
            out = self._run(self._base_args("ideviceinfo") + ["-k", key])
            return out.strip() if out else "Unknown"

        model   = prop("ProductType")          # e.g. iPhone14,3
        version = prop("ProductVersion")       # e.g. 17.2
        build   = prop("BuildVersion")         # e.g. 21C62

        return {
            "model":      model,
            "os_version": version,
            "build":      build,
            # Keep android_version alias for any code that references it
            "android_version": version,
        }

    def _sim_device_info(self) -> dict:
        """Get simulator device info from simctl."""
        out = self._run(
            ["xcrun", "simctl", "list", "devices", "-j"], timeout=15)
        if not out:
            return {"model": "iOS Simulator", "os_version": "Unknown", "build": "Unknown"}
        import json
        try:
            data = json.loads(out)
            for runtime, devs in data.get("devices", {}).items():
                for dev in devs:
                    if dev.get("udid") == self.udid:
                        version = runtime.split(".")[-2] + "." + runtime.split(".")[-1]
                        return {
                            "model":      dev.get("name", "Simulator"),
                            "os_version": version,
                            "build":      "Simulator",
                            "android_version": version,
                        }
        except (json.JSONDecodeError, KeyError, IndexError):
            pass
        return {"model": "iOS Simulator", "os_version": "Unknown", "build": "Unknown"}

    # ── Screen capture ────────────────────────────────────────────────────────

    def take_screenshot(self, local_path: str = "/tmp/screen.png") -> str:
        if self._sim_mode:
            self._run(["xcrun", "simctl", "io", self.udid,
                       "screenshot", local_path])
        else:
            if _tool_available("idevicescreenshot"):
                self._run(self._base_args("idevicescreenshot") + [local_path])
            else:
                print("⚠  idevicescreenshot not found — brew install libimobiledevice")
        return local_path

    # ── Log streaming ─────────────────────────────────────────────────────────

    def logcat_command(self, app_id: str = "", pid: str = "") -> list:
        """
        Return the command to stream iOS device logs.
        For simulators: xcrun simctl spawn (passes through system logs).
        For real devices: idevicesyslog with optional process filter.
        """
        if self._sim_mode:
            # Simulator logs go to the host via simctl
            cmd = ["xcrun", "simctl", "spawn", self.udid,
                   "log", "stream", "--style", "syslog"]
            if app_id:
                # Filter by process (bundle ID short name)
                short = app_id.split(".")[-1]
                cmd += ["--predicate", f'process CONTAINS "{short}"']
            return cmd
        else:
            # Real device
            if not _tool_available("idevicesyslog"):
                print("⚠  idevicesyslog not found — brew install libimobiledevice")
                return []
            cmd = self._base_args("idevicesyslog")
            if app_id:
                short = app_id.split(".")[-1]
                cmd += ["--process", short]
            return cmd
