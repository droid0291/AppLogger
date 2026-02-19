# SmartLogger Test App

This is a minimal Android application designed to test the features of SmartLogger.

## Features
- **FLAG_SECURE Toggle**: Enable/Disable the secure flag to test screenshot capabilities.
- **Test Data**: Static text fields to verify OCR/Gemini analysis.
- **Input Field**: A text field to test ADB input commands.

## How to Run

### Method 1: Android Studio (Recommended)
1.  Open **Android Studio**.
2.  Select **Open** and navigate to this folder:
    `/Users/shaship/Documents/Projects/SmartLogger/SmartLoggerTestApp`
3.  Wait for Gradle to sync (it will download necessary build tools).
4.  Connect your Android device via USB (ensure USB Debugging is on).
5.  Click the **Run** button (Green Play icon) in the toolbar.

### Method 2: Command Line (Requires Gradle)
If you have Gradle installed:
```bash
gradle installDebug
```
Then launch the app on your device.
