import sys
import os
import tkinter as tk
from config import Config
from src.adb_manager import ADBManager
from src.gemini_client import GeminiClient
from src.secure_handler import SecureHandler
from src.video_recorder import VideoRecorder
from src.log_analyzer import LogAnalyzer
from src.steps_generator import StepsGenerator
from src.jira_client import JiraClient
from src.gui import SmartLoggerGUI

def main():
    print("Starting SmartLogger GUI...")
    Config.validate()
    
    adb = ADBManager(adb_path=Config.ADB_PATH, device_serial=Config.DEVICE_SERIAL)
    gemini = GeminiClient(api_key=Config.GEMINI_API_KEY)
    secure = SecureHandler(adb_manager=adb)
    
    # Initialize bug reporting modules
    video_recorder = VideoRecorder(adb_manager=adb)
    log_analyzer = LogAnalyzer(adb_manager=adb, gemini_client=gemini)
    steps_generator = StepsGenerator(gemini_client=gemini, video_recorder=video_recorder)
    
    # Initialize JIRA client (optional - only if configured)
    jira_client = None
    if Config.JIRA_URL:
        jira_client = JiraClient(
            jira_url=Config.JIRA_URL,
            email=Config.JIRA_EMAIL,
            api_token=Config.JIRA_API_TOKEN,
            project_key=Config.JIRA_PROJECT_KEY
        )

    root = tk.Tk()
    app = SmartLoggerGUI(root, adb, gemini, secure, video_recorder, log_analyzer, steps_generator, jira_client)
    root.mainloop()

if __name__ == "__main__":
    main()

