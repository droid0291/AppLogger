import sys
import os
import tkinter as tk
from config import Config
from src.gemini_client import GeminiClient
from src.secure_handler import SecureHandler
from src.log_analyzer import LogAnalyzer
from src.steps_generator import StepsGenerator
from src.jira_client import JiraClient
from src.gui import SmartLoggerGUI


def _create_device_manager():
    """Instantiate the correct DeviceManager based on PLATFORM config."""
    if Config.PLATFORM == "ios":
        from src.ios_manager import IOSManager
        return IOSManager()
    else:
        from src.android_manager import AndroidManager
        return AndroidManager(
            adb_path=Config.ADB_PATH,
            device_serial=Config.DEVICE_SERIAL
        )


def _create_recorder(device_manager):
    """Instantiate the correct recorder for the active device manager."""
    if Config.PLATFORM == "ios":
        from src.ios_recorder import IOSRecorder
        return IOSRecorder(device_manager)
    else:
        from src.video_recorder import VideoRecorder
        return VideoRecorder(adb_manager=device_manager)


def main():
    print(f"Starting SmartLogger GUI... (platform: {Config.PLATFORM})")
    Config.validate()

    device_manager = _create_device_manager()
    gemini         = GeminiClient(api_key=Config.GEMINI_API_KEY)
    secure         = SecureHandler(adb_manager=device_manager)

    recorder       = _create_recorder(device_manager)
    log_analyzer   = LogAnalyzer(adb_manager=device_manager, gemini_client=gemini)
    steps_gen      = StepsGenerator(gemini_client=gemini, video_recorder=recorder)

    jira_client = None
    if Config.JIRA_URL:
        jira_client = JiraClient(
            jira_url=Config.JIRA_URL,
            email=Config.JIRA_EMAIL,
            api_token=Config.JIRA_API_TOKEN,
            project_key=Config.JIRA_PROJECT_KEY
        )

    root = tk.Tk()
    app = SmartLoggerGUI(
        root, device_manager, gemini, secure,
        recorder, log_analyzer, steps_gen, jira_client
    )
    root.mainloop()


if __name__ == "__main__":
    main()
