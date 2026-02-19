import subprocess
import os
from datetime import datetime

class VideoRecorder:
    def __init__(self, adb_manager):
        self.adb = adb_manager
        self.recording = False
        self.current_recording_path = None

    def start_recording(self, output_dir="recordings"):
        """Start screen recording on the connected device."""
        if self.recording:
            print("Recording already in progress")
            return False
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        device_path = f"/sdcard/smartlogger_{timestamp}.mp4"
        self.current_recording_path = os.path.join(output_dir, f"recording_{timestamp}.mp4")
        
        # Build the full ADB command
        base_cmd = [self.adb.adb_path]
        if self.adb.device_serial:
            base_cmd.extend(["-s", self.adb.device_serial])
        
        full_cmd = base_cmd + ["shell", "screenrecord", "--time-limit", "180", device_path]
        
        try:
            # Start recording in background (non-blocking)
            self.recording_process = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.recording = True
            self.device_recording_path = device_path
            print(f"Recording started: {device_path}")
            return True
        except Exception as e:
            print(f"Failed to start recording: {e}")
            return False

    def stop_recording(self):
        """Stop the current recording and pull it from device."""
        if not self.recording:
            print("No recording in progress")
            return None
        
        # Terminate the recording process
        if hasattr(self, 'recording_process') and self.recording_process:
            self.recording_process.terminate()
            self.recording_process.wait(timeout=5)  # Wait for process to finish
        
        # Wait a moment for file to finalize on device
        import time
        time.sleep(2)
        
        # Pull the recording from device
        try:
            pull_cmd = ["pull", self.device_recording_path, self.current_recording_path]
            self.adb.run_command(pull_cmd)
            
            # Cleanup device
            self.adb.run_command(["shell", "rm", self.device_recording_path])
            
            self.recording = False
            print(f"Recording saved: {self.current_recording_path}")
            return self.current_recording_path
        except Exception as e:
            print(f"Failed to pull recording: {e}")
            self.recording = False
            return None

    def extract_frames(self, video_path, output_dir="frames", interval=1):
        """Extract frames from video using FFmpeg (requires FFmpeg installed)."""
        os.makedirs(output_dir, exist_ok=True)
        
        # FFmpeg command to extract frames
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"fps=1/{interval}",  # Extract 1 frame per interval seconds
            f"{output_dir}/frame_%04d.png"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Frames extracted to {output_dir}")
                return output_dir
            else:
                print(f"FFmpeg error: {result.stderr}")
                return None
        except FileNotFoundError:
            print("FFmpeg not installed. Please install FFmpeg for video processing.")
            return None
