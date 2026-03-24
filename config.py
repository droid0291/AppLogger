import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # LLM Configuration (default to gemini)
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    # Gemini Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # AWS Bedrock Configuration
    AWS_REGION     = os.getenv("AWS_REGION", "us-east-1")
    AWS_PROFILE    = os.getenv("AWS_PROFILE") # Optional, defaults to standard boto3 resolution

    ADB_PATH       = os.getenv("ADB_PATH", "adb")
    DEVICE_SERIAL  = os.getenv("DEVICE_SERIAL")

    # Platform: 'android' (default) or 'ios'
    PLATFORM       = os.getenv("PLATFORM", "android").lower()

    # JIRA Configuration
    JIRA_URL         = os.getenv("JIRA_URL")
    JIRA_EMAIL       = os.getenv("JIRA_EMAIL")
    JIRA_API_TOKEN   = os.getenv("JIRA_API_TOKEN")
    JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

    @classmethod
    def validate(cls):
        if cls.LLM_PROVIDER not in ("gemini", "bedrock"):
            print(f"Warning: Unknown LLM_PROVIDER '{cls.LLM_PROVIDER}'. Defaulting to gemini.")
            cls.LLM_PROVIDER = "gemini"
            
        if cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            print("Warning: GEMINI_API_KEY not found in environment variables.")
            
        if not cls.JIRA_URL:
            print("Warning: JIRA credentials not configured. Auto-logging disabled.")
        if cls.PLATFORM not in ("android", "ios"):
            print(f"Warning: Unknown PLATFORM '{cls.PLATFORM}'. Defaulting to android.")
            cls.PLATFORM = "android"

