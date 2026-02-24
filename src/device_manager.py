"""
Abstract base class for platform device managers.
Both AndroidManager and IOSManager implement this interface so all
higher-level code (GUI, LogAnalyzer, VideoRecorder) is platform-agnostic.
"""

from abc import ABC, abstractmethod


class DeviceManager(ABC):
    """Platform-agnostic device communication interface."""

    # ── Device discovery ──────────────────────────────────────────────────────

    @abstractmethod
    def get_connected_devices(self) -> list:
        """Return a list of connected device identifiers (serial / UDID)."""

    @abstractmethod
    def set_device(self, device_id: str):
        """Select the active device by identifier."""

    # ── Shell / command execution ─────────────────────────────────────────────

    @abstractmethod
    def run_command(self, cmd: list) -> str | None:
        """
        Run a platform command and return stdout as a string.
        Returns None on failure.
        """

    # ── App management ────────────────────────────────────────────────────────

    @abstractmethod
    def list_installed_apps(self) -> list:
        """Return installed third-party app identifiers (package / bundle ID)."""

    @abstractmethod
    def get_pid(self, app_id: str) -> str:
        """Return the PID of a running app, or '' if not found."""

    # ── Device info ───────────────────────────────────────────────────────────

    @abstractmethod
    def get_device_info(self) -> dict:
        """
        Return a dict with at least:
          model, os_version (or android_version), build
        """

    # ── Screen capture ────────────────────────────────────────────────────────

    @abstractmethod
    def take_screenshot(self, local_path: str = "/tmp/screen.png") -> str:
        """Capture a screenshot and write it to local_path. Returns the path."""

    # ── Log streaming ─────────────────────────────────────────────────────────

    @abstractmethod
    def logcat_command(self, app_id: str = "", pid: str = "") -> list:
        """
        Return the full CLI command list to start a streaming log process.
        The caller is responsible for launching and reading the subprocess.
        """

    # ── Platform identity ─────────────────────────────────────────────────────

    @property
    @abstractmethod
    def platform(self) -> str:
        """Return 'android' or 'ios'."""

    @property
    @abstractmethod
    def app_id_label(self) -> str:
        """Human label for the app identifier, e.g. 'Package' or 'Bundle ID'."""
