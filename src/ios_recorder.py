"""
iOS screen recorder.
Supports:
  • iOS Simulator  — xcrun simctl io <udid> recordVideo
  • Real device    — irecord CLI (if available), else screenshot-stitch fallback
"""

import os
import subprocess
import threading
import time
from datetime import datetime


class IOSRecorder:
    """Records iOS device/simulator screen to an MP4 file."""

    def __init__(self, ios_manager):
        self.ios = ios_manager
        self.recording = False
        self.current_recording_path = None
        self._proc = None
        self._stitch_thread = None

    # ─────────────────────────────────────────────────────────────────────────

    def start_recording(self, output_dir: str = "recordings") -> bool:
        if self.recording:
            print("Recording already in progress")
            return False

        os.makedirs(output_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_recording_path = os.path.join(
            output_dir, f"recording_ios_{ts}.mp4")

        if self.ios._sim_mode:
            return self._start_sim_recording()
        else:
            return self._start_device_recording()

    def stop_recording(self) -> "Optional[str]":
        if not self.recording:
            print("No recording in progress")
            return None

        if self.ios._sim_mode:
            return self._stop_sim_recording()
        else:
            return self._stop_device_recording()

    # ─────────────────────────────────────────────────────────────────────────
    # Simulator recording (xcrun simctl)
    # ─────────────────────────────────────────────────────────────────────────

    def _start_sim_recording(self) -> bool:
        cmd = [
            "xcrun", "simctl", "io",
            self.ios.udid, "recordVideo",
            "--codec", "h264",
            "--force",
            self.current_recording_path
        ]
        try:
            self._proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.recording = True
            print(f"[iOS Sim] Recording started → {self.current_recording_path}")
            return True
        except Exception as e:
            print(f"[iOS Sim] Failed to start recording: {e}")
            return False

    def _stop_sim_recording(self) -> "Optional[str]":
        if self._proc:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        self.recording = False
        if os.path.exists(self.current_recording_path):
            print(f"[iOS Sim] Recording saved → {self.current_recording_path}")
            return self.current_recording_path
        print("[iOS Sim] Recording file not found after stop")
        return None

    # ─────────────────────────────────────────────────────────────────────────
    # Real device recording
    # ─────────────────────────────────────────────────────────────────────────

    def _start_device_recording(self) -> bool:
        import shutil
        if shutil.which("irecord"):
            return self._start_irecord()
        else:
            print("⚠  irecord not found — falling back to screenshot-stitch recording")
            return self._start_screenshot_stitch()

    def _start_irecord(self) -> bool:
        cmd = ["irecord"]
        if self.ios.udid:
            cmd += ["-u", self.ios.udid]
        cmd += ["-o", self.current_recording_path]
        try:
            self._proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.recording = True
            print(f"[iOS Real] Recording via irecord → {self.current_recording_path}")
            return True
        except Exception as e:
            print(f"[iOS Real] irecord failed: {e}")
            return False

    def _stop_device_recording(self) -> "Optional[str]":
        if self._proc:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        if self._stitch_thread and self._stitch_thread.is_alive():
            self.recording = False          # signals the stitch loop to stop
            self._stitch_thread.join(timeout=10)
        else:
            self.recording = False
        if os.path.exists(self.current_recording_path):
            print(f"[iOS Real] Recording saved → {self.current_recording_path}")
            return self.current_recording_path
        return None

    # ─── Screenshot-stitch fallback ───────────────────────────────────────────

    def _start_screenshot_stitch(self) -> bool:
        """
        Capture screenshots at ~2fps while recording flag is True,
        then stitch with FFmpeg when stopped.
        """
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._frame_dir = os.path.join("recordings", f"frames_{ts}")
        os.makedirs(self._frame_dir, exist_ok=True)
        self.recording = True

        def capture_loop():
            idx = 0
            while self.recording:
                path = os.path.join(self._frame_dir, f"frame_{idx:05d}.png")
                self.ios.take_screenshot(path)
                idx += 1
                time.sleep(0.5)   # ~2fps

        self._stitch_thread = threading.Thread(
            target=capture_loop, daemon=True)
        self._stitch_thread.start()
        print(f"[iOS Real] Screenshot-stitch recording started (frames → {self._frame_dir})")
        return True

    def _stitch_frames_to_video(self) -> "Optional[str]":
        """Use FFmpeg to stitch PNG frames into MP4."""
        import shutil
        if not shutil.which("ffmpeg"):
            print("⚠  FFmpeg not found — cannot stitch frames into video")
            return None
        cmd = [
            "ffmpeg", "-y",
            "-framerate", "2",
            "-i", os.path.join(self._frame_dir, "frame_%05d.png"),
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            self.current_recording_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            shutil.rmtree(self._frame_dir, ignore_errors=True)
            return self.current_recording_path
        print(f"FFmpeg stitch error: {result.stderr}")
        return None

    # ── Convenience ───────────────────────────────────────────────────────────

    def extract_frames(self, video_path: str,
                       output_dir: str = "frames", interval: int = 1):
        """Shared FFmpeg frame extraction (same as Android)."""
        os.makedirs(output_dir, exist_ok=True)
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"fps=1/{interval}",
            f"{output_dir}/frame_%04d.png"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return output_dir if result.returncode == 0 else None
