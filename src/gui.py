import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
import threading
import os
import datetime
import subprocess

# ── Colour tokens ────────────────────────────────────────────────────────────
C_SIDEBAR_BG    = "#1C1C2E"   # deep indigo-black sidebar
C_SIDEBAR_HOVER = "#2A2A40"
C_TAB_ACTIVE    = "#0071E3"   # Apple blue
C_TAB_INACTIVE  = "#1C1C2E"
C_TAB_TEXT      = "#FFFFFF"
C_TAB_TEXT_DIM  = "#8E8EA0"
C_MAIN_BG       = "#F2F2F7"   # Apple light grey
C_CARD_BG       = "#FFFFFF"
C_BORDER        = "#D1D1D6"
C_ACCENT        = "#0071E3"
C_DANGER        = "#FF3B30"
C_SUCCESS       = "#34C759"
C_TEXT_PRIMARY  = "#1C1C1E"
C_TEXT_SEC      = "#6E6E73"
C_LOG_BG        = "#0D1117"
C_LOG_FG        = "#C9D1D9"
C_LOG_ERROR     = "#FF7B72"
C_LOG_WARN      = "#E3B341"
C_LOG_OK        = "#7EE787"

FONT_FAMILY     = "Helvetica Neue"
FONT_SIZE_SM    = 11
FONT_SIZE_MD    = 13
FONT_SIZE_LG    = 17
FONT_SIZE_XL    = 22


class SmartLoggerGUI:
    def __init__(self, root, adb_manager, gemini_client, secure_handler,
                 video_recorder=None, log_analyzer=None,
                 steps_generator=None, jira_client=None):
        self.root           = root
        self.adb            = adb_manager
        self.gemini         = gemini_client
        self.secure         = secure_handler
        self.video_recorder = video_recorder
        self.log_analyzer   = log_analyzer
        self.steps_generator = steps_generator
        self.jira_client    = jira_client

        # state
        self.recording          = False
        self.log_process        = None
        self.log_file_handle    = None
        self.current_log_file   = None
        self.last_log_file      = None
        self.last_video_path    = None
        self._active_tab        = None
        self._tab_buttons       = {}
        self._tab_frames        = {}
        self._session_timer     = None
        self._elapsed_seconds   = 0

        self.root.title("SmartLogger")
        self.root.geometry("1120x700")
        self.root.minsize(900, 600)
        self.root.configure(bg=C_SIDEBAR_BG)

        self._apply_theme()
        self._build_ui()
        self.refresh_devices()

    # ─────────────────────────────────────────────────────────────────────────
    # Theme
    # ─────────────────────────────────────────────────────────────────────────

    def _apply_theme(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(".",
            background=C_MAIN_BG,
            foreground=C_TEXT_PRIMARY,
            font=(FONT_FAMILY, FONT_SIZE_MD))

        # Flat combobox
        style.configure("Selector.TCombobox",
            fieldbackground=C_CARD_BG,
            background=C_CARD_BG,
            foreground=C_TEXT_PRIMARY,
            arrowcolor=C_TEXT_SEC,
            relief="flat",
            padding=4)

        # Primary button (Apple blue)
        style.configure("Primary.TButton",
            background=C_ACCENT,
            foreground="#FFFFFF",
            relief="flat",
            padding=(14, 8),
            font=(FONT_FAMILY, FONT_SIZE_MD, "bold"))
        style.map("Primary.TButton",
            background=[("active", "#005BBD"), ("disabled", "#A8C8F5")])

        # Danger button (red stop)
        style.configure("Danger.TButton",
            background=C_DANGER,
            foreground="#FFFFFF",
            relief="flat",
            padding=(14, 8),
            font=(FONT_FAMILY, FONT_SIZE_MD, "bold"))
        style.map("Danger.TButton",
            background=[("active", "#CC2A22")])

        # Ghost button (secondary)
        style.configure("Ghost.TButton",
            background=C_CARD_BG,
            foreground=C_ACCENT,
            relief="flat",
            padding=(10, 6),
            font=(FONT_FAMILY, FONT_SIZE_SM))
        style.map("Ghost.TButton",
            background=[("active", "#EAF2FF")])

        # Sidebar tab button
        style.configure("Tab.TButton",
            background=C_TAB_INACTIVE,
            foreground=C_TAB_TEXT_DIM,
            relief="flat",
            padding=(14, 11),
            anchor="w",
            font=(FONT_FAMILY, FONT_SIZE_SM))
        style.map("Tab.TButton",
            background=[("active", C_SIDEBAR_HOVER)])

        style.configure("TabActive.TButton",
            background=C_TAB_ACTIVE,
            foreground=C_TAB_TEXT,
            relief="flat",
            padding=(14, 11),
            anchor="w",
            font=(FONT_FAMILY, FONT_SIZE_SM, "bold"))
        style.map("TabActive.TButton",
            background=[("active", "#005BBD")])

        # Card frame
        style.configure("Card.TFrame",
            background=C_CARD_BG,
            relief="flat")

        style.configure("Main.TFrame", background=C_MAIN_BG)
        style.configure("Sidebar.TFrame", background=C_SIDEBAR_BG)
        style.configure("Header.TFrame", background=C_SIDEBAR_BG)

        style.configure("Sidebar.TLabel",
            background=C_SIDEBAR_BG,
            foreground=C_TAB_TEXT_DIM,
            font=(FONT_FAMILY, FONT_SIZE_SM - 1))
        style.configure("SidebarVal.TLabel",
            background=C_SIDEBAR_BG,
            foreground="#FFFFFF",
            font=(FONT_FAMILY, FONT_SIZE_SM))
        style.configure("Main.TLabel",
            background=C_MAIN_BG,
            foreground=C_TEXT_PRIMARY)
        style.configure("Card.TLabel",
            background=C_CARD_BG,
            foreground=C_TEXT_PRIMARY)
        style.configure("Status.TLabel",
            background="#0D0D1A",
            foreground="#8E8EA0",
            font=(FONT_FAMILY, FONT_SIZE_SM - 1),
            padding=(8, 4))
        style.configure("TSeparator", background=C_BORDER)

    # ─────────────────────────────────────────────────────────────────────────
    # Top-level layout skeleton
    # ─────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Root grid: sidebar | main
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)

        self._build_sidebar()
        self._build_main_area()
        self._build_statusbar()

        # Show first tab
        self._switch_tab("crash")

    # ─────────────────────────────────────────────────────────────────────────
    # Sidebar
    # ─────────────────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", width=190)
        sidebar.grid(row=0, column=0, sticky="ns", rowspan=2)
        sidebar.grid_propagate(False)
        sidebar.columnconfigure(0, weight=1)

        # ── App logo / name ─────────────────────────────────────────────────
        logo_frame = ttk.Frame(sidebar, style="Sidebar.TFrame", padding=(16, 20, 16, 8))
        logo_frame.grid(row=0, column=0, sticky="ew")

        tk.Label(logo_frame,
            text="SmartLogger",
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
            bg=C_SIDEBAR_BG, fg="#FFFFFF").pack(anchor="w")
        tk.Label(logo_frame,
            text="Android QA Tool",
            font=(FONT_FAMILY, FONT_SIZE_SM - 1),
            bg=C_SIDEBAR_BG, fg=C_TAB_TEXT_DIM).pack(anchor="w")

        # ── Divider ──────────────────────────────────────────────────────────
        tk.Frame(sidebar, bg="#2E2E44", height=1).grid(row=1, column=0, sticky="ew", pady=(4, 0))

        # ── Device / App selectors ───────────────────────────────────────────
        sel_frame = ttk.Frame(sidebar, style="Sidebar.TFrame", padding=(14, 14, 14, 4))
        sel_frame.grid(row=2, column=0, sticky="ew")
        sel_frame.columnconfigure(0, weight=1)

        ttk.Label(sel_frame, text="DEVICE", style="Sidebar.TLabel").grid(row=0, column=0, sticky="w")

        self.device_combo = tk.StringVar()
        self._device_combo_widget = ttk.Combobox(sel_frame, textvariable=self.device_combo,
            style="Selector.TCombobox", state="readonly", height=8)
        self._device_combo_widget.grid(row=1, column=0, sticky="ew", pady=(2, 4))
        self._device_combo_widget.bind("<<ComboboxSelected>>", self.on_device_select)

        ttk.Button(sel_frame, text="↺  Refresh", style="Ghost.TButton",
            command=self.refresh_devices).grid(row=2, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(sel_frame, text="APP", style="Sidebar.TLabel").grid(row=3, column=0, sticky="w")

        self.package_var = tk.StringVar()
        self.package_combo = ttk.Combobox(sel_frame, textvariable=self.package_var,
            style="Selector.TCombobox", state="readonly", height=12)
        self.package_combo.grid(row=4, column=0, sticky="ew", pady=(2, 4))

        ttk.Button(sel_frame, text="↺  Refresh Apps", style="Ghost.TButton",
            command=self.refresh_packages).grid(row=5, column=0, sticky="ew")

        # ── Divider ──────────────────────────────────────────────────────────
        tk.Frame(sidebar, bg="#2E2E44", height=1).grid(row=3, column=0, sticky="ew", pady=(12, 4))

        # ── Tab buttons ───────────────────────────────────────────────────────
        tabs_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
        tabs_frame.grid(row=4, column=0, sticky="nsew")
        tabs_frame.columnconfigure(0, weight=1)

        tab_defs = [
            ("crash",   "💥  Report Crash"),
            ("network", "🌐  Report Network Failure"),
            ("ui",      "🎨  Report UI Bug"),
            ("verify",  "✅  Verify Content"),
        ]
        for i, (key, label) in enumerate(tab_defs):
            btn = ttk.Button(tabs_frame, text=label, style="Tab.TButton",
                command=lambda k=key: self._switch_tab(k))
            btn.grid(row=i, column=0, sticky="ew")
            self._tab_buttons[key] = btn

        # push everything up
        sidebar.rowconfigure(5, weight=1)

    # ─────────────────────────────────────────────────────────────────────────
    # Main content area
    # ─────────────────────────────────────────────────────────────────────────

    def _build_main_area(self):
        self._main_container = ttk.Frame(self.root, style="Main.TFrame")
        self._main_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self._main_container.columnconfigure(0, weight=1)
        self._main_container.rowconfigure(0, weight=1)

        # Build all tab frames (only one visible at a time)
        self._tab_frames["crash"]   = self._build_crash_tab(self._main_container)
        self._tab_frames["network"] = self._build_placeholder_tab(self._main_container, "🌐", "Report Network Failure", "Coming soon")
        self._tab_frames["ui"]      = self._build_placeholder_tab(self._main_container, "🎨", "Report UI Bug", "Coming soon")
        self._tab_frames["verify"]  = self._build_placeholder_tab(self._main_container, "✅", "Verify Content", "Coming soon")

        for frame in self._tab_frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

    # ─────────────────────────────────────────────────────────────────────────
    # Status bar
    # ─────────────────────────────────────────────────────────────────────────

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg="#0D0D1A", height=28)
        bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        bar.grid_propagate(False)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(bar, textvariable=self.status_var,
            font=(FONT_FAMILY, FONT_SIZE_SM - 1),
            bg="#0D0D1A", fg="#8E8EA0",
            anchor="w", padx=10).pack(side="left", fill="y")

        self._timer_var = tk.StringVar(value="")
        tk.Label(bar, textvariable=self._timer_var,
            font=(FONT_FAMILY, FONT_SIZE_SM - 1),
            bg="#0D0D1A", fg=C_DANGER,
            anchor="e", padx=10).pack(side="right", fill="y")

    # ─────────────────────────────────────────────────────────────────────────
    # Tab switching
    # ─────────────────────────────────────────────────────────────────────────

    def _switch_tab(self, key):
        self._active_tab = key
        for k, btn in self._tab_buttons.items():
            btn.configure(style="TabActive.TButton" if k == key else "Tab.TButton")
        for k, frame in self._tab_frames.items():
            if k == key:
                frame.tkraise()

    # ─────────────────────────────────────────────────────────────────────────
    # ── TAB: Report Crash ────────────────────────────────────────────────────
    # ─────────────────────────────────────────────────────────────────────────

    def _build_crash_tab(self, parent):
        frame = ttk.Frame(parent, style="Main.TFrame")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)  # logcat expands

        # ── Page header ──────────────────────────────────────────────────────
        header = ttk.Frame(frame, style="Main.TFrame", padding=(28, 24, 28, 0))
        header.grid(row=0, column=0, sticky="ew")

        tk.Label(header,
            text="Report Crash",
            font=(FONT_FAMILY, FONT_SIZE_XL, "bold"),
            bg=C_MAIN_BG, fg=C_TEXT_PRIMARY).pack(anchor="w")
        tk.Label(header,
            text="Start a session to record screen and capture logcat. Stop when the crash occurs.",
            font=(FONT_FAMILY, FONT_SIZE_SM),
            bg=C_MAIN_BG, fg=C_TEXT_SEC).pack(anchor="w", pady=(2, 0))

        # ── Session info card ────────────────────────────────────────────────
        info_card = tk.Frame(frame, bg=C_CARD_BG,
            highlightbackground=C_BORDER, highlightthickness=1)
        info_card.grid(row=1, column=0, sticky="ew", padx=28, pady=16)

        inner = tk.Frame(info_card, bg=C_CARD_BG)
        inner.pack(fill="x", padx=16, pady=12)

        # Device info
        dev_col = tk.Frame(inner, bg=C_CARD_BG)
        dev_col.pack(side="left", fill="x", expand=True)

        tk.Label(dev_col, text="DEVICE",
            font=(FONT_FAMILY, FONT_SIZE_SM - 2, "bold"),
            bg=C_CARD_BG, fg=C_TEXT_SEC).pack(anchor="w")
        self._crash_device_label = tk.Label(dev_col, text="—",
            font=(FONT_FAMILY, FONT_SIZE_MD, "bold"),
            bg=C_CARD_BG, fg=C_TEXT_PRIMARY)
        self._crash_device_label.pack(anchor="w")

        # App info
        app_col = tk.Frame(inner, bg=C_CARD_BG)
        app_col.pack(side="left", fill="x", expand=True)

        tk.Label(app_col, text="APP",
            font=(FONT_FAMILY, FONT_SIZE_SM - 2, "bold"),
            bg=C_CARD_BG, fg=C_TEXT_SEC).pack(anchor="w")
        self._crash_app_label = tk.Label(app_col, text="—",
            font=(FONT_FAMILY, FONT_SIZE_MD, "bold"),
            bg=C_CARD_BG, fg=C_TEXT_PRIMARY)
        self._crash_app_label.pack(anchor="w")

        # Session status dot + label
        status_col = tk.Frame(inner, bg=C_CARD_BG)
        status_col.pack(side="right")

        self._session_dot = tk.Label(status_col, text="⬤",
            font=(FONT_FAMILY, 10),
            bg=C_CARD_BG, fg=C_BORDER)
        self._session_dot.pack(side="left", padx=(0, 4))
        self._session_status_label = tk.Label(status_col, text="No active session",
            font=(FONT_FAMILY, FONT_SIZE_SM),
            bg=C_CARD_BG, fg=C_TEXT_SEC)
        self._session_status_label.pack(side="left")

        # ── Live logcat panel ────────────────────────────────────────────────
        log_wrapper = tk.Frame(frame, bg=C_CARD_BG,
            highlightbackground=C_BORDER, highlightthickness=1)
        log_wrapper.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 0))
        log_wrapper.columnconfigure(0, weight=1)
        log_wrapper.rowconfigure(1, weight=1)

        log_header = tk.Frame(log_wrapper, bg="#161B22")
        log_header.grid(row=0, column=0, sticky="ew")

        tk.Label(log_header, text="🔴  Live Logcat",
            font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
            bg="#161B22", fg=C_LOG_FG,
            padx=12, pady=6).pack(side="left")

        self._log_filter_label = tk.Label(log_header, text="",
            font=(FONT_FAMILY, FONT_SIZE_SM - 1),
            bg="#161B22", fg=C_TAB_TEXT_DIM,
            padx=12, pady=6)
        self._log_filter_label.pack(side="right")

        self._logcat_text = scrolledtext.ScrolledText(log_wrapper,
            wrap=tk.WORD,
            font=("Menlo", FONT_SIZE_SM - 1),
            bg=C_LOG_BG, fg=C_LOG_FG,
            insertbackground=C_LOG_FG,
            selectbackground=C_TAB_ACTIVE,
            relief="flat", bd=0,
            padx=8, pady=6)
        self._logcat_text.grid(row=1, column=0, sticky="nsew")
        self._logcat_text.configure(state="disabled")

        # Tag colours for log levels
        self._logcat_text.tag_config("error", foreground=C_LOG_ERROR)
        self._logcat_text.tag_config("warn",  foreground=C_LOG_WARN)
        self._logcat_text.tag_config("ok",    foreground=C_LOG_OK)
        self._logcat_text.tag_config("dim",   foreground="#555C6A")

        # ── Bottom action bar ────────────────────────────────────────────────
        action_bar = tk.Frame(frame, bg=C_MAIN_BG)
        action_bar.grid(row=3, column=0, sticky="ew", padx=28, pady=16)

        self._session_btn = ttk.Button(action_bar,
            text="▶   Start Session",
            style="Primary.TButton",
            command=self.toggle_recording)
        self._session_btn.pack(side="left")

        # Post-session panel (hidden until recording stops)
        self._post_session_frame = tk.Frame(action_bar, bg=C_MAIN_BG)
        self._post_session_frame.pack(side="left", padx=(16, 0))
        # hidden initially
        self._post_session_frame.pack_forget()

        ttk.Button(self._post_session_frame,
            text="✨  Analyse with AI",
            style="Ghost.TButton",
            command=self.create_bug_report).pack(side="left", padx=(0, 8))

        self._jira_btn = ttk.Button(self._post_session_frame,
            text="📋  File Jira Ticket",
            style="Ghost.TButton",
            command=self.file_jira_ticket)
        self._jira_btn.pack(side="left", padx=(0, 8))
        # Hide Jira button if Jira not configured
        if not self.jira_client:
            self._jira_btn.pack_forget()

        ttk.Button(self._post_session_frame,
            text="🗑  Clear Session",
            style="Ghost.TButton",
            command=self._clear_crash_session).pack(side="left")

        # ── AI Analysis output (collapsed until analysis runs) ────────────────
        self._analysis_card = tk.Frame(frame, bg=C_CARD_BG,
            highlightbackground=C_BORDER, highlightthickness=1)
        # not gridded until needed

        self._analysis_text = scrolledtext.ScrolledText(self._analysis_card,
            wrap=tk.WORD,
            font=(FONT_FAMILY, FONT_SIZE_SM),
            bg=C_CARD_BG, fg=C_TEXT_PRIMARY,
            relief="flat", bd=0, padx=12, pady=10,
            height=10)
        self._analysis_text.pack(fill="both", expand=True)

        return frame

    # ─────────────────────────────────────────────────────────────────────────
    # Placeholder tabs
    # ─────────────────────────────────────────────────────────────────────────

    def _build_placeholder_tab(self, parent, icon, title, subtitle):
        frame = ttk.Frame(parent, style="Main.TFrame")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        center = tk.Frame(frame, bg=C_MAIN_BG)
        center.grid(row=0, column=0)

        tk.Label(center, text=icon,
            font=(FONT_FAMILY, 48),
            bg=C_MAIN_BG).pack(pady=(0, 8))
        tk.Label(center, text=title,
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
            bg=C_MAIN_BG, fg=C_TEXT_PRIMARY).pack()
        tk.Label(center, text=subtitle,
            font=(FONT_FAMILY, FONT_SIZE_MD),
            bg=C_MAIN_BG, fg=C_TEXT_SEC).pack(pady=(4, 0))

        return frame

    # ─────────────────────────────────────────────────────────────────────────
    # Device / App selectors
    # ─────────────────────────────────────────────────────────────────────────

    def refresh_devices(self):
        devices = self.adb.get_connected_devices()
        self._device_combo_widget['values'] = devices
        if devices:
            self._device_combo_widget.current(0)
            self.on_device_select(None)
            self.status_var.set(f"Found {len(devices)} device(s)")
        else:
            self.status_var.set("No devices connected — connect via USB and enable ADB")

    def on_device_select(self, event):
        serial = self.device_combo.get()
        if serial:
            self.adb.device_serial = serial
            self._crash_device_label.configure(text=serial)
            self.status_var.set(f"Device: {serial}")

    def refresh_packages(self):
        def task():
            self.status_var.set("Fetching installed apps…")
            try:
                cmd = [self.adb.adb_path]
                if self.adb.device_serial:
                    cmd += ["-s", self.adb.device_serial]
                cmd += ["shell", "pm", "list", "packages", "-3"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                packages = sorted([
                    line.replace("package:", "")
                    for line in result.stdout.strip().split("\n")
                    if line.startswith("package:")
                ])
                self.root.after(0, lambda: self._update_packages(packages))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Error fetching apps: {e}"))

        threading.Thread(target=task, daemon=True).start()

    def _update_packages(self, packages):
        self.package_combo['values'] = packages
        if packages:
            self.package_combo.current(0)
            self._crash_app_label.configure(text=packages[0])
        self.status_var.set(f"Found {len(packages)} app(s)")

    # ─────────────────────────────────────────────────────────────────────────
    # Recording toggle (crash tab)
    # ─────────────────────────────────────────────────────────────────────────

    def toggle_recording(self):
        if not self.video_recorder:
            self.status_var.set("Video recorder not initialised")
            return

        if not self.recording:
            self._start_session()
        else:
            self._stop_session()

    def _start_session(self):
        success = self.video_recorder.start_recording()
        if not success:
            self.status_var.set("Failed to start screen recording")
            return

        self.recording = True

        # Update device/app info labels
        device = self.device_combo.get() or "—"
        app    = self.package_var.get() or "All packages"
        self._crash_device_label.configure(text=device)
        self._crash_app_label.configure(text=app)
        self._log_filter_label.configure(text=f"filter: {app}")

        # UI state
        self._session_btn.configure(text="⏹   Stop Session", style="Danger.TButton")
        self._session_dot.configure(fg=C_DANGER)
        self._session_status_label.configure(text="Recording…", fg=C_DANGER)
        self._post_session_frame.pack_forget()

        # Hide analysis card if visible
        self._analysis_card.grid_forget()

        # Clear logcat pane
        self._logcat_text.configure(state="normal")
        self._logcat_text.delete("1.0", "end")
        self._logcat_text.configure(state="disabled")
        self._append_log("── Session started ──\n", tag="dim")

        # Start log capture
        self._start_logcat(self.package_var.get().strip())

        # Timer
        self._elapsed_seconds = 0
        self._tick_timer()

        self.status_var.set("Recording session — screen + logcat active")

    def _stop_session(self):
        video_path = self.video_recorder.stop_recording()
        self.recording = False

        # Stop logcat
        if self.log_process:
            self.log_process.terminate()
            try:
                self.log_process.wait(timeout=3)
            except Exception:
                pass
            self.log_process = None
        if self.log_file_handle:
            self.log_file_handle.close()
            self.log_file_handle = None
            self.last_log_file = self.current_log_file
            self.current_log_file = None

        # Stop timer
        if self._session_timer:
            self.root.after_cancel(self._session_timer)
            self._session_timer = None
        self._timer_var.set("")

        # Store video path
        if video_path:
            self.last_video_path = video_path

        # UI state
        self._session_btn.configure(text="▶   Start Session", style="Primary.TButton")
        self._session_dot.configure(fg=C_SUCCESS)
        self._session_status_label.configure(text="Session complete", fg=C_SUCCESS)

        self._append_log("\n── Session stopped ──\n", tag="dim")

        # Show post-session actions
        self._post_session_frame.pack(side="left", padx=(16, 0))
        self.status_var.set(
            f"Session saved — tap ✨ Analyse with AI to generate bug report")

    # ─────────────────────────────────────────────────────────────────────────
    # Logcat streaming
    # ─────────────────────────────────────────────────────────────────────────

    def _get_pid(self, logcat_bin, selected_package):
        """Return PID string for selected_package, or '' if not running."""
        pid_cmd = [logcat_bin]
        if self.adb.device_serial:
            pid_cmd += ["-s", self.adb.device_serial]
        pid_cmd += ["shell", "pidof", "-s", selected_package]
        try:
            result = subprocess.run(pid_cmd, capture_output=True, text=True, timeout=5)
            return result.stdout.strip()
        except Exception:
            return ""

    def _start_logcat(self, selected_package=""):
        try:
            os.makedirs("logs", exist_ok=True)
            logcat_bin = self.log_analyzer.adb.adb_path if self.log_analyzer else self.adb.adb_path

            # Clear existing logs
            clear_cmd = [logcat_bin]
            if self.adb.device_serial:
                clear_cmd += ["-s", self.adb.device_serial]
            clear_cmd += ["logcat", "-c"]
            subprocess.run(clear_cmd, timeout=5)

            # Build logcat command
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_log_file = f"logs/recording_{timestamp}.txt"
            self._logcat_package = selected_package  # stored for stream filter

            full_cmd = [logcat_bin]
            if self.adb.device_serial:
                full_cmd += ["-s", self.adb.device_serial]
            full_cmd += ["logcat"]

            if selected_package:
                # Try to get PID immediately
                app_pid = self._get_pid(logcat_bin, selected_package)

                if app_pid:
                    full_cmd += [f"--pid={app_pid}"]
                    self._logcat_app_pid = app_pid
                    self._append_log(
                        f"── Filtering logs for {selected_package} (PID: {app_pid}) ──\n",
                        tag="ok")
                else:
                    # App not running yet — start watcher and inform user
                    self._logcat_app_pid = None
                    self._append_log(
                        f"⚠ App '{selected_package}' not running.\n"
                        f"  Open the app on your device — logs will auto-filter when detected.\n"
                        f"  Until then, only app logs will be shown once PID is found.\n",
                        tag="warn")
                    # Start PID watcher thread
                    threading.Thread(
                        target=self._wait_for_pid,
                        args=(logcat_bin, selected_package),
                        daemon=True).start()
            else:
                self._logcat_app_pid = None
                self._append_log("── No app filter — capturing all logs ──\n", tag="dim")

            self.log_file_handle = open(self.current_log_file, "w")
            self.log_process = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1
            )

            # Stream lines to UI
            threading.Thread(target=self._stream_logcat, daemon=True).start()

        except Exception as e:
            self._append_log(f"Logcat error: {e}\n", tag="error")

    def _wait_for_pid(self, logcat_bin, package):
        """Retry getting PID every 2 s; once found, restart logcat with filter."""
        import time
        while self.recording:
            time.sleep(2)
            pid = self._get_pid(logcat_bin, package)
            if pid:
                self._logcat_app_pid = pid
                self.root.after(0, lambda p=pid: self._append_log(
                    f"── App detected (PID: {p}) — filtering logs for {package} ──\n",
                    tag="ok"))
                # Kill current unfiltered logcat and restart with PID filter
                if self.log_process:
                    self.log_process.terminate()
                import time as _t; _t.sleep(0.5)

                new_cmd = [logcat_bin]
                if self.adb.device_serial:
                    new_cmd += ["-s", self.adb.device_serial]
                new_cmd += ["logcat", f"--pid={pid}"]

                try:
                    self.log_process = subprocess.Popen(
                        new_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                        text=True,
                        bufsize=1
                    )
                    threading.Thread(target=self._stream_logcat, daemon=True).start()
                except Exception as e:
                    self.root.after(0, lambda: self._append_log(
                        f"Failed to restart filtered logcat: {e}\n", tag="error"))
                return  # done watching

    def _stream_logcat(self):
        """Background thread: read logcat stdout line-by-line, emit to UI."""
        MAX_LINES = 500
        line_count = 0

        try:
            for line in self.log_process.stdout:
                if not self.recording:
                    break

                # Python-side package filter — belt-and-suspenders
                pkg = getattr(self, "_logcat_package", "")
                if pkg and pkg not in line:
                    # Also allow lines that contain the PID we know about
                    pid = getattr(self, "_logcat_app_pid", None)
                    if pid and f" {pid} " not in line and f"({pid})" not in line:
                        continue

                if self.log_file_handle:
                    self.log_file_handle.write(line)

                tag = self._classify_log_line(line)
                self.root.after(0, lambda l=line, t=tag: self._append_log(l, tag=t))

                line_count += 1
                if line_count > MAX_LINES:
                    self.root.after(0, self._trim_logcat)
                    line_count = 0
        except Exception:
            pass


    def _classify_log_line(self, line):
        u = line.upper()
        if any(k in u for k in ("FATAL", "E ANDROIDRUNTIME", " E/", "EXCEPTION", "ANR IN")):
            return "error"
        if any(k in u for k in (" W/", "WARN")):
            return "warn"
        if any(k in u for k in (" I/", " D/")):
            return "ok"
        return None

    def _append_log(self, text, tag=None):
        self._logcat_text.configure(state="normal")
        if tag:
            self._logcat_text.insert("end", text, tag)
        else:
            self._logcat_text.insert("end", text)
        self._logcat_text.see("end")
        self._logcat_text.configure(state="disabled")

    def _trim_logcat(self):
        """Keep last 400 lines to avoid memory bloat."""
        self._logcat_text.configure(state="normal")
        lines = int(self._logcat_text.index("end-1c").split(".")[0])
        if lines > 450:
            self._logcat_text.delete("1.0", f"{lines - 400}.0")
        self._logcat_text.configure(state="disabled")

    # ─────────────────────────────────────────────────────────────────────────
    # Session timer
    # ─────────────────────────────────────────────────────────────────────────

    def _tick_timer(self):
        if not self.recording:
            return
        m, s = divmod(self._elapsed_seconds, 60)
        self._timer_var.set(f"⏺  {m:02d}:{s:02d}")
        self._elapsed_seconds += 1
        self._session_timer = self.root.after(1000, self._tick_timer)

    # ─────────────────────────────────────────────────────────────────────────
    # Bug report / AI analysis
    # ─────────────────────────────────────────────────────────────────────────

    def create_bug_report(self):
        def task():
            self.status_var.set("Generating bug report…")
            try:
                device_info = {}
                if self.log_analyzer:
                    device_info = self.log_analyzer.get_device_info()

                steps        = "Not requested"
                logs_analysis = "Not requested"
                severity     = "N/A"

                # Video → steps
                video_path = getattr(self, "last_video_path", None)
                if video_path and os.path.exists(video_path):
                    self.root.after(0, lambda: self.status_var.set("Uploading video for step analysis…"))
                    prompt = (
                        "Analyse this mobile app screen recording and generate clear, "
                        "numbered reproduction steps. Focus on: screens shown, UI elements "
                        "interacted with, user action sequence, what happens at the end "
                        "(crash/error/unexpected behaviour). Output ONLY numbered steps."
                    )
                    result = self.gemini.analyze_video(video_path, prompt)
                    steps = result if result else "Video analysis failed – check API quota"
                else:
                    steps = "No video recording found. Record a session first."

                # Logs → analysis
                log_content = None
                if hasattr(self, "last_log_file") and self.last_log_file and os.path.exists(self.last_log_file):
                    with open(self.last_log_file) as f:
                        log_content = f.read()
                elif self.log_analyzer:
                    log_file = self.log_analyzer.extract_crash_logs()
                    if log_file:
                        with open(log_file) as f:
                            log_content = f.read()

                if log_content:
                    self.root.after(0, lambda: self.status_var.set("Analysing logs with AI…"))
                    prompt = (
                        "Analyse the following Android crash log and provide:\n"
                        "1. Root cause\n2. Specific line/method where it occurred\n"
                        "3. Suggested fix\n4. Severity (Critical/High/Medium/Low)\n\n"
                        f"Logs:\n{log_content[-3000:]}"
                    )
                    result = self.gemini.analyze_text(prompt)
                    if result:
                        logs_analysis = result
                        for level in ("Critical", "High", "Medium", "Low"):
                            if level in result:
                                severity = level
                                break
                    else:
                        logs_analysis = "Log analysis failed – check API quota"
                else:
                    logs_analysis = "No logs found. Record a session first."

                report = (
                    f"=== BUG REPORT ===\n\n"
                    f"Device:   {device_info.get('model', 'N/A')}\n"
                    f"Android:  {device_info.get('android_version', 'N/A')}\n"
                    f"Severity: {severity}\n\n"
                    f"STEPS TO REPRODUCE:\n{steps}\n\n"
                    f"CRASH ANALYSIS:\n{logs_analysis}\n"
                )

                self.root.after(0, lambda: self._show_analysis(report))
                self.root.after(0, lambda: self.status_var.set(
                    "Analysis complete — click 📋 File Jira Ticket to log the bug"))

            except Exception as e:
                import traceback
                traceback.print_exc()
                self.root.after(0, lambda: self.status_var.set(f"Error: {e}"))

        threading.Thread(target=task, daemon=True).start()

    def file_jira_ticket(self):
        """Standalone Jira ticket creation — called only when user clicks the button."""
        if not self.jira_client:
            self.status_var.set("Jira not configured — check your .env file")
            return

        # Grab report text from the analysis card if available
        try:
            report_text = self._analysis_text.get("1.0", "end").strip()
        except Exception:
            report_text = ""

        def task():
            self.root.after(0, lambda: self.status_var.set("Creating Jira ticket…"))
            try:
                device_info = self.log_analyzer.get_device_info() if self.log_analyzer else {}
                summary = "App Crash – Reported by SmartLogger"
                description = self.jira_client.format_bug_description(
                    report_text or "See attached logs and recording.",
                    "",
                    device_info,
                    getattr(self, "last_video_path", None)
                )
                attachments = []
                if getattr(self, "last_video_path", None) and os.path.exists(self.last_video_path):
                    attachments.append(self.last_video_path)
                if getattr(self, "last_log_file", None) and os.path.exists(self.last_log_file):
                    attachments.append(self.last_log_file)

                issue_key = self.jira_client.create_bug(
                    summary=summary,
                    description=description,
                    priority="High",
                    labels=["smartlogger"],
                    attachments=attachments
                )
                if issue_key:
                    msg = f"✅ Jira ticket created: {issue_key}"
                else:
                    msg = "❌ Jira ticket creation failed — check credentials"
                self.root.after(0, lambda m=msg: self.status_var.set(m))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Jira error: {e}"))

        threading.Thread(target=task, daemon=True).start()

    def _show_analysis(self, text):
        # Show the analysis card below the action bar
        self._analysis_card.grid(row=4, column=0, sticky="ew",
            padx=28, pady=(0, 20))
        self._analysis_text.configure(state="normal")
        self._analysis_text.delete("1.0", "end")
        self._analysis_text.insert("end", text)
        self._analysis_text.configure(state="disabled")
        self.status_var.set("Analysis complete")

    def _clear_crash_session(self):
        if messagebox.askyesno("Clear Session",
                               "Delete this session's recordings and logs?"):
            import shutil
            for path in (getattr(self, "last_video_path", None),
                         getattr(self, "last_log_file", None)):
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception:
                        pass
            self.last_video_path = None
            self.last_log_file   = None

            self._logcat_text.configure(state="normal")
            self._logcat_text.delete("1.0", "end")
            self._logcat_text.configure(state="disabled")

            self._analysis_card.grid_forget()
            self._post_session_frame.pack_forget()
            self._session_dot.configure(fg=C_BORDER)
            self._session_status_label.configure(text="No active session", fg=C_TEXT_SEC)
            self.status_var.set("Session cleared")

    # ─────────────────────────────────────────────────────────────────────────
    # Legacy stubs (keep compatibility with main.py callers)
    # ─────────────────────────────────────────────────────────────────────────

    def capture_screen(self):
        """Legacy – no longer in sidebar but kept for external callers."""
        def task():
            self.status_var.set("Capturing screenshot…")
            local_path = "screen_capture.png"
            try:
                self.adb.take_screenshot(local_path)
                img = Image.open(local_path)
                img.thumbnail((400, 800))
                photo = ImageTk.PhotoImage(img)
                self.root.after(0, lambda: self.status_var.set("Screenshot captured"))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Screenshot error: {e}"))
        threading.Thread(target=task, daemon=True).start()

    def check_secure(self):
        suggestion = self.secure.suggest_bypass_strategy()
        print(suggestion)

    def send_text(self, text=""):
        if text:
            self.adb.input_text(text)

    def clear_all_data(self):
        import shutil
        for d in ("recordings", "logs"):
            if os.path.exists(d):
                shutil.rmtree(d)
                os.makedirs(d, exist_ok=True)
        self.status_var.set("All data cleared")
