# SmartLoggerTestApp — iOS

Native SwiftUI test app for the **SmartLogger iOS QA tool**.  
Mirrors the Android `SmartLoggerTestApp` with 6 bug-simulation screens.

## Screens

| Screen | Bugs simulated |
|---|---|
| 💥 **Crash Demo** | Force-unwrap nil, OOM, stack overflow, index out of bounds |
| 🥶 **Hang Demo** | Main-thread sleep (5 s / 15 s) + CPU busy loop — iOS equivalent of Android ANR |
| 🎨 **UI Bug Demo** | Overlapping views, text truncation, low-contrast button, missing image |
| 🌐 **Network Demo** | Connection timeout, HTTP 500, offline API call |
| 🔥 **Performance Demo** | Memory leak (static array), 15-second CPU spike |
| 🔐 **Security Demo** | Hardcoded credentials logged, cleartext HTTP, token in UserDefaults |

## Setup

1. **Open Xcode** → File → New → Project → iOS → App
   - Product Name: `SmartLoggerTestApp_iOS`
   - Bundle ID: `com.example.SmartLoggerTestApp`
   - Interface: **SwiftUI** · Language: **Swift**

2. **Replace the generated files** with the files in `SmartLoggerTestApp_iOS/`:
   ```
   SmartLoggerTestApp_iOSApp.swift
   ContentView.swift
   SharedComponents.swift
   CrashDemoView.swift
   HangDemoView.swift
   UIBugDemoView.swift
   NetworkDemoView.swift
   PerformanceDemoView.swift
   SecurityDemoView.swift
   ```

3. **Run** on any iOS Simulator (iPhone 16, iOS 16+).

## Using with SmartLogger

1. Boot the simulator, install and open this app.
2. In SmartLogger: flip the sidebar toggle to **iOS**.
3. Select the simulator from the device dropdown.
4. Select `com.example.SmartLoggerTestApp` as the app.
5. Click **Start Session** — logs from all bug triggers appear live in the log panel.
