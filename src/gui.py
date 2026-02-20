import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import threading
import os

class SmartLoggerGUI:
    def __init__(self, root, adb_manager, gemini_client, secure_handler, video_recorder=None, log_analyzer=None, steps_generator=None, jira_client=None):
        self.root = root
        self.adb = adb_manager
        self.gemini = gemini_client
        self.secure = secure_handler
        self.video_recorder = video_recorder
        self.log_analyzer = log_analyzer
        self.steps_generator = steps_generator
        self.jira_client = jira_client
        
        self.recording = False
        
        self.root.title("SmartLogger - Android QA Tool")
        self.root.geometry("1000x700")
        
        self.create_widgets()
        self.refresh_devices()

    def create_widgets(self):
        # --- Left Panel: Controls ---
        left_panel = ttk.Frame(self.root, width=200, padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        ttk.Label(left_panel, text="Devices").pack(anchor=tk.W)
        self.device_combo = ttk.Combobox(left_panel)
        self.device_combo.pack(fill=tk.X, pady=5)
        self.device_combo.bind("<<ComboboxSelected>>", self.on_device_select)
        
        ttk.Button(left_panel, text="Refresh Devices", command=self.refresh_devices).pack(fill=tk.X, pady=2)
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        ttk.Label(left_panel, text="Actions").pack(anchor=tk.W)
        ttk.Button(left_panel, text="Capture Screen", command=self.capture_screen).pack(fill=tk.X, pady=2)
        ttk.Button(left_panel, text="Check Secure", command=self.check_secure).pack(fill=tk.X, pady=2)
        
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(left_panel, text="Input Text").pack(anchor=tk.W)
        self.input_entry = ttk.Entry(left_panel)
        self.input_entry.pack(fill=tk.X, pady=2)
        ttk.Button(left_panel, text="Send Text", command=self.send_text).pack(fill=tk.X, pady=2)
        
        # --- Bug Reporting Section ---
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(left_panel, text="Bug Reporting", font=('', 10, 'bold')).pack(anchor=tk.W)
        
        self.record_button = ttk.Button(left_panel, text="▶ Start Recording", command=self.toggle_recording)
        self.record_button.pack(fill=tk.X, pady=2)
        
        # Analysis options checkboxes
        self.steps_var = tk.BooleanVar(value=True)
        self.logs_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(left_panel, text="📹 Generate Steps to Reproduce", variable=self.steps_var).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(left_panel, text="📋 Analyse Logs", variable=self.logs_var).pack(anchor=tk.W, pady=2)
        
        ttk.Button(left_panel, text="📋 Create Bug Report", command=self.create_bug_report).pack(fill=tk.X, pady=2)
        
        ttk.Button(left_panel, text="🗑️ Clear All Data", command=self.clear_all_data).pack(fill=tk.X, pady=2)

        # --- Center Panel: Screenshot ---
        center_panel = ttk.Frame(self.root, padding=10, relief=tk.SUNKEN)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.image_label = ttk.Label(center_panel, text="No Screenshot")
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # --- Right Panel: Analysis ---
        right_panel = ttk.Frame(self.root, width=300, padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Label(right_panel, text="Gemini Analysis").pack(anchor=tk.W)
        self.analysis_text = scrolledtext.ScrolledText(right_panel, wrap=tk.WORD, height=30, width=40)
        self.analysis_text.pack(fill=tk.BOTH, expand=True)
        
        # --- Bottom Status ---
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def refresh_devices(self):
        devices = self.adb.get_connected_devices()
        self.device_combo['values'] = devices
        if devices:
            self.device_combo.current(0)
            self.on_device_select(None)
        self.status_var.set(f"Found {len(devices)} devices")

    def on_device_select(self, event):
        serial = self.device_combo.get()
        if serial:
            self.adb.device_serial = serial
            self.status_var.set(f"Selected: {serial}")

    def capture_screen(self):
        def task():
            self.status_var.set("Capturing screenshot...")
            local_path = "screen_capture.png"
            try:
                self.adb.take_screenshot(local_path)
                
                # Display Image
                img = Image.open(local_path)
                # Resize to fit (maintain aspect ratio simplified)
                img.thumbnail((400, 800)) 
                photo = ImageTk.PhotoImage(img)
                
                # Update UI in main thread
                self.root.after(0, lambda: self.update_image(photo, local_path))
                
            except Exception as e:
                self.status_var.set(f"Error: {e}")

        threading.Thread(target=task).start()

    def update_image(self, photo, img_path):
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo # Keep reference
        self.status_var.set("Screenshot captured. Analyzing...")
        self.analyze_screen(img_path)

    def analyze_screen(self, img_path):
        def task():
            prompt = "Analyze this UI and identify potential bugs or improvements."
            response = self.gemini.analyze_image(img_path, prompt)
            self.root.after(0, lambda: self.update_analysis(response))
        
        threading.Thread(target=task).start()

    def update_analysis(self, text):
        self.analysis_text.delete(1.0, tk.END)
        if text:
            self.analysis_text.insert(tk.INSERT, text)
            self.status_var.set("Analysis complete.")
        else:
             self.analysis_text.insert(tk.INSERT, "Analysis failed.")
             self.status_var.set("Analysis failed.")

    def check_secure(self):
        suggestion = self.secure.suggest_bypass_strategy()
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.INSERT, suggestion)
        self.status_var.set("Displayed secure bypass strategies.")

    def send_text(self):
        text = self.input_entry.get()
        if text:
            self.adb.input_text(text)
            self.status_var.set(f"Sent: {text}")

    def toggle_recording(self):
        """Toggle video recording on/off, and start/stop log capture."""
        if not self.video_recorder:
            self.status_var.set("Video recorder not initialized")
            return
        
        if not self.recording:
            # Start recording
            success = self.video_recorder.start_recording()
            if success:
                self.recording = True
                self.record_button.config(text="⏹ Stop Recording")
                self.status_var.set("Recording video and logs...")
                
                # Start log capture in background
                if self.log_analyzer:
                    import subprocess
                    import datetime
                    
                    # Create logs directory if it doesn't exist
                    os.makedirs("logs", exist_ok=True)

                    # Clear existing device logs first to reduce token usage
                    logcat_cmd = self.log_analyzer.adb.adb_path
                    if self.log_analyzer.adb.device_serial:
                        clear_cmd = [logcat_cmd, "-s", self.log_analyzer.adb.device_serial, "logcat", "-c"]
                    else:
                        clear_cmd = [logcat_cmd, "logcat", "-c"]
                    subprocess.run(clear_cmd, timeout=5)
                    print("Cleared device logs")

                    # Create log file with timestamp
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    self.current_log_file = f"logs/recording_{timestamp}.txt"
                    
                    # Start continuous log capture: adb logcat > file
                    if self.log_analyzer.adb.device_serial:
                        full_cmd = [logcat_cmd, "-s", self.log_analyzer.adb.device_serial, "logcat"]
                    else:
                        full_cmd = [logcat_cmd, "logcat"]
                    
                    # Open log file and start writing
                    self.log_file_handle = open(self.current_log_file, 'w')
                    self.log_process = subprocess.Popen(
                        full_cmd,
                        stdout=self.log_file_handle,
                        stderr=subprocess.DEVNULL
                    )
                    print(f"Started log capture: {self.current_log_file}")
            else:
                self.status_var.set("Failed to start recording")
        else:
            # Stop recording
            video_path = self.video_recorder.stop_recording()
            self.recording = False
            self.record_button.config(text="▶ Start Recording")
            
            # Stop log capture
            if self.log_process:
                self.log_process.terminate()
                self.log_process.wait() # Wait for the process to terminate
                self.log_process = None
                print(f"Stopped log capture: {self.current_log_file}")
            if self.log_file_handle:
                self.log_file_handle.close()
                self.log_file_handle = None
                self.last_log_file = self.current_log_file # Store for bug report
                self.current_log_file = None

            if video_path:
                self.status_var.set(f"Recording saved: {video_path}")
                self.last_video_path = video_path
            else:
                self.status_var.set("Failed to save recording")

    def create_bug_report(self):
        """Create bug report based on selected analysis options."""
        generate_steps = self.steps_var.get()
        analyse_logs = self.logs_var.get()
        
        if not generate_steps and not analyse_logs:
            self.status_var.set("Please select at least one analysis option")
            return
        
        def task():
            self.status_var.set("Generating bug report...")
            
            try:
                device_info = {}
                if self.log_analyzer:
                    device_info = self.log_analyzer.get_device_info()
                
                steps = "Not requested"
                logs_analysis = "Not requested"
                severity = "N/A"
                
                # --- STEP 1: Generate Steps to Reproduce (from video) ---
                if generate_steps:
                    video_path = getattr(self, 'last_video_path', None)
                    if video_path and os.path.exists(video_path):
                        self.status_var.set("Uploading video for steps analysis...")
                        print(f"Analyzing video for steps: {video_path}")
                        
                        prompt = """Analyze this mobile app screen recording and generate clear, numbered reproduction steps.

Focus on:
1. What screens/pages are shown
2. What UI elements the user interacts with (buttons, fields, toggles, etc.)
3. The sequence of user actions
4. What happens at the end (crash, error, unexpected behavior)

Generate ONLY numbered reproduction steps that a QA engineer can follow, nothing else."""
                        
                        result = self.gemini.analyze_video(video_path, prompt)
                        steps = result if result else "Video analysis failed - check API quota"
                    else:
                        steps = "No video recording found. Record a session first."
                
                # --- STEP 2: Analyse Logs (from log file) ---
                if analyse_logs:
                    log_content = None
                    
                    # Try pre-captured log file first
                    if hasattr(self, 'last_log_file') and self.last_log_file and os.path.exists(self.last_log_file):
                        print(f"Using pre-captured logs: {self.last_log_file}")
                        with open(self.last_log_file, 'r') as f:
                            log_content = f.read()
                    elif self.log_analyzer:
                        # Fallback: extract logs now
                        print("Extracting logs from device...")
                        log_file = self.log_analyzer.extract_crash_logs()
                        if log_file:
                            with open(log_file, 'r') as f:
                                log_content = f.read()
                    
                    if log_content:
                        self.status_var.set("Analyzing logs with AI...")
                        print(f"Sending {len(log_content)} chars of logs to Gemini")
                        
                        prompt = f"""Analyze the following Android crash log and provide:
1. Root cause of the crash
2. Specific line/method where it occurred
3. Suggested fix for the developer
4. Severity assessment (Critical/High/Medium/Low)

Logs:
{log_content[-3000:]}"""
                        
                        result = self.gemini.analyze_text(prompt)
                        if result:
                            logs_analysis = result
                            # Extract severity from response
                            for level in ['Critical', 'High', 'Medium', 'Low']:
                                if level in result:
                                    severity = level
                                    break
                        else:
                            logs_analysis = "Log analysis failed - check API quota"
                    else:
                        logs_analysis = "No logs found. Record a session first."
                
                # --- Build Report ---
                report = f"""
=== BUG REPORT ===

Device: {device_info.get('model', 'N/A')}
Android: {device_info.get('android_version', 'N/A')}
Severity: {severity}

STEPS TO REPRODUCE:
{steps}

CRASH ANALYSIS:
{logs_analysis}
"""
                self.root.after(0, lambda: self.update_analysis(report))
                
                # 4. Auto-create JIRA ticket (if configured)
                if self.jira_client:
                    self.status_var.set("Creating JIRA ticket...")
                    
                    summary = "App Crash - Auto-reported by SmartLogger"
                    description = self.jira_client.format_bug_description(
                        steps, 
                        logs_analysis, 
                        device_info,
                        getattr(self, 'last_video_path', None)
                    )
                    
                    attachments = []
                    if hasattr(self, 'last_video_path'):
                        attachments.append(self.last_video_path)
                    if log_file:
                        attachments.append(log_file)
                    
                    issue_key = self.jira_client.create_bug(
                        summary=summary,
                        description=description,
                        priority="High",
                        labels=["auto-reported", "smartlogger"],
                        attachments=attachments
                    )
                    
                    if issue_key:
                        self.status_var.set(f"Bug report created: {issue_key}")
                    else:
                        self.status_var.set("JIRA ticket creation failed")
                else:
                    self.status_var.set("Bug report generated (JIRA not configured)")
                    
            except Exception as e:
                import traceback
                print(f"Error creating bug report: {e}")
                traceback.print_exc()
                self.status_var.set(f"Error creating bug report: {e}")
        
        threading.Thread(target=task).start()

    def clear_all_data(self):
        """Delete all saved recordings and logs."""
        import shutil
        from tkinter import messagebox
        
        # Confirm with user
        if not messagebox.askyesno("Clear All Data", 
                                   "This will delete all saved recordings and logs. Continue?"):
            return
        
        deleted_items = []
        
        # Delete recordings directory
        recordings_dir = "recordings"
        if os.path.exists(recordings_dir):
            try:
                shutil.rmtree(recordings_dir)
                os.makedirs(recordings_dir, exist_ok=True)
                deleted_items.append("recordings")
            except Exception as e:
                print(f"Error deleting recordings: {e}")
        
        # Delete logs directory
        logs_dir = "logs"
        if os.path.exists(logs_dir):
            try:
                shutil.rmtree(logs_dir)
                os.makedirs(logs_dir, exist_ok=True)
                deleted_items.append("logs")
            except Exception as e:
                print(f"Error deleting logs: {e}")
        
        # Clear last video path
        if hasattr(self, 'last_video_path'):
            delattr(self, 'last_video_path')
        
        # Update status
        if deleted_items:
            self.status_var.set(f"Cleared: {', '.join(deleted_items)}")
            messagebox.showinfo("Success", "All data cleared successfully!")
        else:
            self.status_var.set("No data to clear")
