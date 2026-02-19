import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    ADB_PATH = os.getenv("ADB_PATH", "adb") # Default to system adb
    DEVICE_SERIAL = os.getenv("DEVICE_SERIAL")
    
    # JIRA Configuration
    JIRA_URL = os.getenv("JIRA_URL")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
    JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            print("Warning: GEMINI_API_KEY not found in environment variables.")
        if not cls.JIRA_URL:
            print("Warning: JIRA credentials not configured. Auto-logging disabled.")
