import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
import requests
from requests.exceptions import RequestException
import textwrap
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
import io
import re
import random
import threading
from collections import deque
import json
import os
import time
import ctypes
from ctypes import wintypes
import comtypes
from comtypes import GUID
import sys
import pythoncom
import winreg
import piexif
from ttkthemes import ThemedTk
import subprocess

# Define HRESULT
HRESULT = ctypes.HRESULT

# IDesktopWallpaper interface GUID
CLSID_DesktopWallpaper = GUID('{C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD}')
IID_IDesktopWallpaper = GUID('{B92B56A9-8B55-4E14-9A89-0199BBB6F93B}')

# Wallpaper position enum
class DESKTOP_WALLPAPER_POSITION(ctypes.c_int):
    DWPOS_CENTER = 0
    DWPOS_TILE = 1
    DWPOS_STRETCH = 2
    DWPOS_FIT = 6
    DWPOS_FILL = 10
    DWPOS_SPAN = 5  # Changed from 22 to 5

class IDesktopWallpaper(comtypes.IUnknown):
    _iid_ = IID_IDesktopWallpaper
    _methods_ = [
        comtypes.COMMETHOD([], HRESULT, 'SetWallpaper',
            (['in'], wintypes.LPCWSTR, 'monitorID'),
            (['in'], wintypes.LPCWSTR, 'wallpaper')),
        comtypes.COMMETHOD([], HRESULT, 'GetWallpaper'),
        comtypes.COMMETHOD([], HRESULT, 'GetMonitorDevicePathAt'),
        comtypes.COMMETHOD([], HRESULT, 'GetMonitorDevicePathCount'),
        comtypes.COMMETHOD([], HRESULT, 'GetMonitorRECT'),
        comtypes.COMMETHOD([], HRESULT, 'SetBackgroundColor'),
        comtypes.COMMETHOD([], HRESULT, 'GetBackgroundColor'),
        comtypes.COMMETHOD([], HRESULT, 'SetPosition',
            (['in'], DESKTOP_WALLPAPER_POSITION, 'position')),
        comtypes.COMMETHOD([], HRESULT, 'GetPosition',
            (['out'], ctypes.POINTER(DESKTOP_WALLPAPER_POSITION), 'position')),
        comtypes.COMMETHOD([], HRESULT, 'SetSlideshow'),
        comtypes.COMMETHOD([], HRESULT, 'GetSlideshow'),
        comtypes.COMMETHOD([], HRESULT, 'SetStatus'),
        comtypes.COMMETHOD([], HRESULT, 'Enable')
    ]

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]



class DevsystBackgroundSetter:

    def __init__(self):
        self.master = ThemedTk(theme="arc")  # Modern flat theme
        self.master.title("WallifyAI - Professional Wallpaper Generator")

        # Attempt to set the application icon
        try:
            # Get the correct path for the icon file (works for both script and executable)
            if hasattr(sys, '_MEIPASS'):
                # Running as PyInstaller executable
                icon_path = os.path.join(sys._MEIPASS, "WallifyAI-logo.ico")
            else:
                # Running as script
                icon_path = "WallifyAI-logo.ico"
            
            # Check if icon file exists and set it
            if os.path.exists(icon_path):
                self.master.iconbitmap(icon_path)
                print(f"Icon loaded successfully from: {icon_path}")
            else:
                print(f"Icon file not found at: {icon_path}")
        except tk.TclError as e:
            print(f"Error loading icon: {e}. Using default icon.")

        self.master.geometry("650x810")  # Optimized height for better spacing
        self.master.minsize(650, 780)  # Set minimum size
        
        # Professional color scheme
        self.colors = {
            'bg_primary': '#2c3e50',      # Dark blue-gray
            'bg_secondary': '#34495e',     # Lighter blue-gray
            'bg_tertiary': '#ecf0f1',     # Light gray
            'accent': '#3498db',          # Professional blue
            'accent_hover': '#2980b9',    # Darker blue for hover
            'text_primary': '#2c3e50',    # Dark text
            'text_secondary': "#17142C",  # Blue text
            'success': '#27ae60',         # Green
            'warning': '#f39c12',         # Orange
            'danger': '#e74c3c',          # Red
            'white': '#ffffff',
            'light_gray': '#f8f9fa'
        }

        # Configure main window
        self.master.configure(bg=self.colors['bg_tertiary'])

        # Create professional styling
        style = ttk.Style()
        
        # Configure button styles - Modern flat design
        style.configure("Primary.TButton", 
                       font=("Segoe UI", 10, "bold"),
                       padding=(12, 8),
                       relief="flat",
                       borderwidth=0,
                       background=self.colors['accent'],
                       foreground=self.colors['text_primary'])
        style.map("Primary.TButton", 
                 background=[("active", self.colors['accent_hover']),
                            ("pressed", self.colors['accent_hover'])],
                 foreground=[("active", self.colors['text_primary']),
                            ("pressed", self.colors['text_primary']),
                            ("!disabled", self.colors['text_primary'])])

        style.configure("Secondary.TButton",
                       font=("Segoe UI", 9),
                       padding=(10, 6),
                       relief="flat",
                       borderwidth=1,
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'])
        style.map("Secondary.TButton",
                 background=[("active", self.colors['light_gray']),
                            ("pressed", self.colors['light_gray'])])

        # Configure frame styles - Clean and minimal
        style.configure("Card.TFrame",
                       background=self.colors['white'],
                       relief="flat",
                       borderwidth=1)
        
        style.configure("Main.TFrame",
                       background=self.colors['bg_tertiary'],
                       relief="flat",
                       borderwidth=0)

        # Configure label styles - Typography hierarchy
        style.configure("Heading.TLabel",
                       font=("Segoe UI", 12, "bold"),
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'])
        
        style.configure("Body.TLabel",
                       font=("Segoe UI", 9),
                       background=self.colors['white'],
                       foreground=self.colors['text_secondary'])
        
        style.configure("Small.TLabel",
                       font=("Segoe UI", 8),
                       background=self.colors['white'],
                       foreground=self.colors['text_secondary'])

        # Configure input styles
        style.configure("Modern.TCombobox",
                       font=("Segoe UI", 9),
                       padding=8,
                       fieldbackground=self.colors['white'],
                       borderwidth=1,
                       relief="solid")
        
        style.configure("Modern.TCheckbutton",
                       font=("Segoe UI", 9),
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'])
        
        # Configure LabelFrame for cards
        style.configure("Card.TLabelframe",
                       background=self.colors['white'],
                       relief="flat",
                       borderwidth=1,
                       labeloutside=False)
        
        style.configure("Card.TLabelframe.Label",
                       font=("Segoe UI", 10, "bold"),
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'])

        # Create main container with professional styling
        self.main_frame = ttk.Frame(self.master, padding="20", style="Main.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.enhance = tk.BooleanVar()
        self.wallpaper_style = tk.StringVar(value="fill")

        self.interval = max(300, 60 * 5)  # Minimum 5 minutes
        self.always_on_top = tk.BooleanVar(value=False)
        
        self.model = tk.StringVar(value="flux")
        
        self.overlay_opacity = tk.IntVar(value=128)  # 0-255 for opacity
        self.overlay_position = tk.StringVar(value="top_right")
        self.use_drop_shadow = tk.BooleanVar(value=False)
        self.overlay_color = tk.StringVar(value="#000000")
        self.submitted_prompt = tk.StringVar()
        self.returned_prompt = tk.StringVar()
        self.negative_prompt = tk.StringVar()
        self.nsfw_status = tk.StringVar()

        self.is_running = False  # Initialize is_running before calling setup_ui and load_settings
        self.setter_thread = None
        self.current_request_id = None

        self.setup_ui()
        self.load_settings()
        self.update_position_options()
        self.prompt_history = deque(maxlen=20)
        self.load_history()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.image_dir = "WALLIFYAI_BACKGROUNDS"
        os.makedirs(self.image_dir, exist_ok=True)

        self.style_dimensions = {
            "center": (1920, 1080),
            "tile": (1920, 1080),
            "stretch": (1920, 1080),
            "fit": (1920, 1080),
            "fill": (1920, 1080),
            "span": (3840, 1080)
        }
        self.wallpaper_style.trace_add('write', self.update_position_options)
        

    def setup_ui(self):
        # Header section with title and main action
        header_frame = ttk.Frame(self.main_frame, style="Card.TFrame", padding="15")
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text="AI Wallpaper Generator", style="Heading.TLabel")
        title_label.pack(side=tk.LEFT)
        
        self.start_stop_button = ttk.Button(header_frame, text="Start Generation", 
                                          command=self.toggle_start_stop, style="Primary.TButton")
        self.start_stop_button.pack(side=tk.RIGHT)

        # Prompt input card
        prompt_card = ttk.LabelFrame(self.main_frame, text="Prompt Configuration", 
                                   style="Card.TLabelframe", padding="15")
        prompt_card.pack(fill=tk.X, pady=(0, 15))

        # Prompt input with modern styling
        prompt_label = ttk.Label(prompt_card, text="Describe your wallpaper:", style="Body.TLabel")
        prompt_label.pack(anchor=tk.W, pady=(0, 5))

        prompt_frame = ttk.Frame(prompt_card, style="Card.TFrame")
        prompt_frame.pack(fill=tk.X, pady=(0, 10))

        self.prompt_entry = tk.Text(prompt_frame, wrap=tk.WORD, height=4, 
                                  font=("Segoe UI", 10), relief="flat", borderwidth=1,
                                  bg=self.colors['white'], fg=self.colors['text_primary'],
                                  selectbackground=self.colors['accent'], 
                                  insertbackground=self.colors['text_primary'])
        self.prompt_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        prompt_scrollbar = ttk.Scrollbar(prompt_frame, orient="vertical", command=self.prompt_entry.yview)
        prompt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.prompt_entry.config(yscrollcommand=prompt_scrollbar.set)

        # History section
        history_frame = ttk.Frame(prompt_card, style="Card.TFrame")
        history_frame.pack(fill=tk.X, pady=(0, 10))
        
        history_label = ttk.Label(history_frame, text="Recent prompts:", style="Body.TLabel")
        history_label.pack(side=tk.LEFT)
        
        remove_button = ttk.Button(history_frame, text="Remove Selected", 
                                 command=self.remove_selected_from_history, style="Secondary.TButton")
        remove_button.pack(side=tk.RIGHT)

        self.history_var = tk.StringVar()
        self.history_dropdown = ttk.Combobox(prompt_card, textvariable=self.history_var, 
                                           style="Modern.TCombobox", state="readonly")
        self.history_dropdown.pack(fill=tk.X)
        self.history_dropdown.bind('<<ComboboxSelected>>', self.on_history_select)

        # Generation settings card
        settings_card = ttk.LabelFrame(self.main_frame, text="Generation Settings", 
                                     style="Card.TLabelframe", padding="15")
        settings_card.pack(fill=tk.X, pady=(0, 15))

        # First row - Primary settings
        settings_row1 = ttk.Frame(settings_card, style="Card.TFrame")
        settings_row1.pack(fill=tk.X, pady=(0, 10))

        # Enhance checkbox with better styling
        self.enhance_check = ttk.Checkbutton(settings_row1, text="Enhance Prompt with AI", 
                                           variable=self.enhance, style="Modern.TCheckbutton")
        self.enhance_check.pack(side=tk.LEFT, padx=(0, 20))

        # Model selection
        model_frame = ttk.Frame(settings_row1, style="Card.TFrame")
        model_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(model_frame, text="AI Model:", style="Body.TLabel").pack(anchor=tk.W)
        model_options = [
            "flux", "flux-realism", "flux-anime", "flux-3d", "any-dark", "turbo",
            "gpt-image-1", "pixel-art", "midjourney", "flux-pro", "dreamshaper-7", 
            "stable-diffusion", "vqgan-clip"
        ]
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model, values=model_options, 
                                      width=15, style="Modern.TCombobox", state="readonly")
        self.model_combo.pack()

        # Wallpaper style
        style_frame = ttk.Frame(settings_row1, style="Card.TFrame")
        style_frame.pack(side=tk.LEFT)
        
        ttk.Label(style_frame, text="Display Style:", style="Body.TLabel").pack(anchor=tk.W)
        style_options = ["fill", "fit", "stretch", "tile", "center", "span"]
        self.style_combo = ttk.Combobox(style_frame, textvariable=self.wallpaper_style, 
                                      values=style_options, width=10, 
                                      style="Modern.TCombobox", state="readonly")
        self.style_combo.pack()

        # Overlay settings card
        overlay_card = ttk.LabelFrame(self.main_frame, text="Overlay Settings", 
                                    style="Card.TLabelframe", padding="15")
        overlay_card.pack(fill=tk.X, pady=(0, 15))

        overlay_row = ttk.Frame(overlay_card, style="Card.TFrame")
        overlay_row.pack(fill=tk.X)

        # Opacity control
        opacity_frame = ttk.Frame(overlay_row, style="Card.TFrame")
        opacity_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(opacity_frame, text="Opacity:", style="Body.TLabel").pack(anchor=tk.W)
        self.opacity_scale = ttk.Scale(opacity_frame, from_=0, to=255, variable=self.overlay_opacity, 
                                     orient=tk.HORIZONTAL, length=120)
        self.opacity_scale.pack()

        # Position control
        position_frame = ttk.Frame(overlay_row, style="Card.TFrame")
        position_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(position_frame, text="Position:", style="Body.TLabel").pack(anchor=tk.W)
        self.position_dropdown = ttk.Combobox(position_frame, textvariable=self.overlay_position, 
                                            width=15, style="Modern.TCombobox", state="readonly")
        self.position_dropdown.pack()

        # Color and shadow controls
        color_frame = ttk.Frame(overlay_row, style="Card.TFrame")
        color_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(color_frame, text="Color:", style="Body.TLabel").pack(anchor=tk.W)
        color_control_frame = ttk.Frame(color_frame, style="Card.TFrame")
        color_control_frame.pack()
        
        self.color_button = tk.Button(color_control_frame, width=3, height=1, 
                                    command=self.choose_overlay_color, relief="flat", 
                                    borderwidth=1, cursor="hand2")
        self.color_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.shadow_check = ttk.Checkbutton(color_control_frame, text="Drop Shadow", 
                                          variable=self.use_drop_shadow, style="Modern.TCheckbutton")
        self.shadow_check.pack(side=tk.LEFT)

        # Status and information card
        info_card = ttk.LabelFrame(self.main_frame, text="Current Status", 
                                 style="Card.TLabelframe", padding="15")
        info_card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Current prompt display
        current_frame = ttk.Frame(info_card, style="Card.TFrame")
        current_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(current_frame, text="Active Prompt:", style="Body.TLabel").pack(anchor=tk.W)
        self.current_prompt_display = tk.Text(current_frame, wrap=tk.WORD, height=2, state='disabled',
                                            font=("Segoe UI", 9), relief="flat", borderwidth=1,
                                            bg=self.colors['light_gray'], fg=self.colors['text_secondary'])
        self.current_prompt_display.pack(fill=tk.X, pady=(2, 0))

        # Prompt information tabs
        info_notebook = ttk.Notebook(info_card)
        info_notebook.pack(fill=tk.BOTH, expand=True)

        # Submitted prompt tab
        submitted_frame = ttk.Frame(info_notebook, style="Card.TFrame", padding="10")
        info_notebook.add(submitted_frame, text="Original Prompt")
        
        self.submitted_prompt_display = tk.Text(submitted_frame, wrap=tk.WORD, height=3, state='disabled',
                                              font=("Segoe UI", 9), relief="flat", borderwidth=1,
                                              bg=self.colors['white'], fg=self.colors['text_primary'])
        self.submitted_prompt_display.pack(fill=tk.BOTH, expand=True)

        # Enhanced prompt tab
        enhanced_frame = ttk.Frame(info_notebook, style="Card.TFrame", padding="10")
        info_notebook.add(enhanced_frame, text="Enhanced Prompt")
        
        self.returned_prompt_display = tk.Text(enhanced_frame, wrap=tk.WORD, height=3, state='disabled',
                                             font=("Segoe UI", 9), relief="flat", borderwidth=1,
                                             bg=self.colors['white'], fg=self.colors['text_primary'])
        self.returned_prompt_display.pack(fill=tk.BOTH, expand=True)

        # Process output tab
        output_frame = ttk.Frame(info_notebook, style="Card.TFrame", padding="10")
        info_notebook.add(output_frame, text="Process Log")
        
        self.process_output_text = tk.Text(output_frame, wrap=tk.WORD, state="disabled", height=6,
                                         font=("Consolas", 8), relief="flat", borderwidth=1,
                                         bg=self.colors['white'], fg=self.colors['text_secondary'])
        self.process_output_text.pack(fill=tk.BOTH, expand=True)

        # Setup menu
        self.setup_menu()

        # Initialize UI state
        self.update_position_options()
        self.update_color_button()

    def setup_menu(self):
        """Setup the application menu with modern styling"""
        menubar = tk.Menu(self.master, bg=self.colors['white'], fg=self.colors['text_primary'],
                         activebackground=self.colors['accent'], activeforeground=self.colors['white'])
        
        # Options menu
        options_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['white'], fg=self.colors['text_primary'],
                              activebackground=self.colors['accent'], activeforeground=self.colors['white'])
        options_menu.add_checkbutton(label="Always on Top", variable=self.always_on_top, 
                                   command=self.toggle_always_on_top)
        options_menu.add_separator()
        options_menu.add_command(label="Set Generation Interval...", command=self.set_interval)
        menubar.add_cascade(label="Options", menu=options_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['white'], fg=self.colors['text_primary'],
                           activebackground=self.colors['accent'], activeforeground=self.colors['white'])
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="License", command=self.show_license)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.master.config(menu=menubar)


    def show_about(self):
        """Show compact professional about dialog"""
        about_window = tk.Toplevel(self.master)
        about_window.title("About WallifyAI")
        about_window.geometry("420x600")  # Increased height for separate feature lines
        about_window.configure(bg='#f8f9fa')
        about_window.resizable(False, False)
        
        # Set the icon for the about window
        try:
            # Get the correct path for the icon file (works for both script and executable)
            if hasattr(sys, '_MEIPASS'):
                # Running as PyInstaller executable
                icon_path = os.path.join(sys._MEIPASS, "WallifyAI-logo.ico")
            else:
                # Running as script
                icon_path = "WallifyAI-logo.ico"
            
            if os.path.exists(icon_path):
                about_window.iconbitmap(icon_path)
        except tk.TclError:
            pass
        
        # Create a clean card container
        card_frame = tk.Frame(about_window, bg='white', relief='solid', bd=1)
        card_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Main content area
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Title section - compact
        title_label = tk.Label(content_frame, text="WallifyAI", 
                            font=("Segoe UI", 16, "bold"),
                            bg='white', fg='#2c3e50')
        title_label.pack(pady=(0, 5))
        
        subtitle_label = tk.Label(content_frame, text="Professional Wallpaper Generator",
                                font=("Segoe UI", 10),
                                bg='white', fg='#6c757d')
        subtitle_label.pack(pady=(0, 20))
        
        # Version info - compact
        version_frame = tk.Frame(content_frame, bg='#f8f9fa')
        version_frame.pack(fill=tk.X, pady=(0, 20))
        
        version_inner = tk.Frame(version_frame, bg='#f8f9fa')
        version_inner.pack(pady=12)
        
        tk.Label(version_inner, text="Version 1.0.0  •  Developed by DevSyst", 
                font=("Segoe UI", 9),
                bg='#f8f9fa', fg='#495057').pack()
        
        # Description - compact
        desc_text = "An intelligent wallpaper generator that creates stunning backgrounds using advanced AI models."
        
        desc_label = tk.Label(content_frame, text=desc_text,
                            font=("Segoe UI", 9),
                            bg='white', fg='#6c757d',
                            justify=tk.CENTER, wraplength=350)
        desc_label.pack(pady=(0, 20))
        
        # Features section - each on separate line
        features_title = tk.Label(content_frame, text="Key Features:",
                                font=("Segoe UI", 10, "bold"),
                                bg='white', fg='#2c3e50')
        features_title.pack(anchor=tk.W, pady=(0, 8))
        
        features = [
            "• Multiple AI models and styles",
            "• Automatic prompt enhancement", 
            "• Customizable display settings",
            "• History management",
            "• Professional overlay options"
        ]
        
        features_container = tk.Frame(content_frame, bg='white')
        features_container.pack(fill=tk.X, anchor=tk.W, pady=(0, 20))
        
        for feature in features:
            feature_label = tk.Label(features_container, text=feature,
                                font=("Segoe UI", 8),
                                bg='white', fg='#6c757d',
                                justify=tk.LEFT)
            feature_label.pack(anchor=tk.W, pady=1)
        
        # Contact section - clean and simple
        contact_title = tk.Label(content_frame, text="Contact & Links:",
                                font=("Segoe UI", 10, "bold"),
                                bg='white', fg='#2c3e50')
        contact_title.pack(anchor=tk.W, pady=(0, 12))
        
        # Links container
        links_frame = tk.Frame(content_frame, bg='white')
        links_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Website link - with fixed alignment
        website_frame = tk.Frame(links_frame, bg='white')
        website_frame.pack(fill=tk.X, pady=2)  # Reduced spacing
        
        website_label = tk.Label(website_frame, text="Website:", 
                font=("Segoe UI", 9),
                bg='white', fg='#495057', width=8, anchor='w')  # Fixed width for alignment
        website_label.pack(side=tk.LEFT)
        
        website_link = tk.Label(website_frame, text="https://devsyst.com",
                            font=("Segoe UI", 9, "underline"),
                            fg='#0066cc', bg='white',
                            cursor="hand2")
        website_link.pack(side=tk.LEFT)
        website_link.bind("<Button-1>", lambda e: self.open_url("https://devsyst.com"))
        website_link.bind("<Enter>", lambda e: website_link.config(fg='#004499'))
        website_link.bind("<Leave>", lambda e: website_link.config(fg='#0066cc'))
        
        # GitHub link - with fixed alignment
        github_frame = tk.Frame(links_frame, bg='white')
        github_frame.pack(fill=tk.X, pady=2)  # Reduced spacing
        
        github_label = tk.Label(github_frame, text="GitHub:", 
                font=("Segoe UI", 9),
                bg='white', fg='#495057', width=8, anchor='w')  # Fixed width for alignment
        github_label.pack(side=tk.LEFT)
        
        github_link = tk.Label(github_frame, text="github.com/thedevsyst/WallifyAI",
                            font=("Segoe UI", 9, "underline"),
                            fg='#0066cc', bg='white',
                            cursor="hand2")
        github_link.pack(side=tk.LEFT)
        github_link.bind("<Button-1>", lambda e: self.open_url("https://github.com/thedevsyst/WallifyAI"))
        github_link.bind("<Enter>", lambda e: github_link.config(fg='#004499'))
        github_link.bind("<Leave>", lambda e: github_link.config(fg='#0066cc'))

        # Email link - with fixed alignment
        email_frame = tk.Frame(links_frame, bg='white')
        email_frame.pack(fill=tk.X, pady=2)  # Reduced spacing
        
        email_label = tk.Label(email_frame, text="Email:", 
                font=("Segoe UI", 9),
                bg='white', fg='#495057', width=8, anchor='w')  # Fixed width for alignment
        email_label.pack(side=tk.LEFT)
        
        email_link = tk.Label(email_frame, text="thedevsyst@gmail.com",
                            font=("Segoe UI", 9, "underline"),
                            fg='#0066cc', bg='white',
                            cursor="hand2")
        email_link.pack(side=tk.LEFT)
        email_link.bind("<Button-1>", lambda e: self.open_url("mailto:thedevsyst@gmail.com"))
        email_link.bind("<Enter>", lambda e: email_link.config(fg='#004499'))
        email_link.bind("<Leave>", lambda e: email_link.config(fg='#0066cc'))
        
        # Force frame updates to ensure visibility
        github_frame.update_idletasks()
        email_frame.update_idletasks()
        
        # Clean close button
        close_button = tk.Button(content_frame, text="Close", 
                                command=about_window.destroy,
                                font=("Segoe UI", 9, "bold"),
                                bg='#3498db', fg='white',
                                relief='flat', bd=0,
                                padx=25, pady=8,
                                cursor="hand2")
        close_button.pack(pady=(5, 0))
        
        # Button hover effects
        def on_button_enter(e):
            close_button.config(bg='#2980b9')
        
        def on_button_leave(e):
            close_button.config(bg='#3498db')
        
        close_button.bind("<Enter>", on_button_enter)
        close_button.bind("<Leave>", on_button_leave)
        
        # Center the window
        about_window.transient(self.master)
        about_window.grab_set()
        about_window.lift()
        about_window.focus_force()
        
        # Center on parent window
        about_window.update_idletasks()
        x = (self.master.winfo_x() + (self.master.winfo_width() // 2)) - (about_window.winfo_width() // 2)
        y = (self.master.winfo_y() + (self.master.winfo_height() // 2)) - (about_window.winfo_height() // 2)
        about_window.geometry(f"+{x}+{y}")
        
        self.master.wait_window(about_window)


    
    def open_url(self, url):
        """Open URL in default browser or email client"""
        import webbrowser
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening URL {url}: {e}")
            # Fallback: copy to clipboard
            try:
                self.master.clipboard_clear()
                self.master.clipboard_append(url)
                messagebox.showinfo("Link", f"Link copied to clipboard:\n{url}")
            except Exception:
                messagebox.showinfo("Link", f"Please visit:\n{url}")

    def cleanup_background_images(self):
        backgrounds = sorted(
            [f for f in os.listdir(self.image_dir) if f.startswith("background_") and f.endswith(".png")],
            key=lambda x: os.path.getmtime(os.path.join(self.image_dir, x)),
            reverse=True
        )
        
        wallpapers = sorted(
            [f for f in os.listdir(self.image_dir) if f.startswith("wallpaper_") and f.endswith(".png")],
            key=lambda x: os.path.getmtime(os.path.join(self.image_dir, x)),
            reverse=True
        )
        
        # Keep only the 10 most recent background images
        for old_bg in backgrounds[10:]:
            try:
                os.remove(os.path.join(self.image_dir, old_bg))
                print(f"Deleted old background: {old_bg}")
            except Exception as e:
                print(f"Error deleting {old_bg}: {e}")
        
        # Keep only the most recent wallpaper image
        for old_wp in wallpapers[1:]:
            try:
                os.remove(os.path.join(self.image_dir, old_wp))
                print(f"Deleted old wallpaper: {old_wp}")
            except Exception as e:
                print(f"Error deleting {old_wp}: {e}")
        
        print(f"After cleanup: {len(backgrounds[:10])} backgrounds and {len(wallpapers[:1])} wallpapers kept.")

    def update_position_options(self, *args):
        if self.wallpaper_style.get() == "span":
            options = ["left_top_left", "left_top_right", "left_bottom_left", "left_bottom_right",
                       "right_top_left", "right_top_right", "right_bottom_left", "right_bottom_right"]
        else:
            options = ["top_left", "top_right", "bottom_left", "bottom_right"]
        
        self.position_dropdown['values'] = options
        if self.overlay_position.get() not in options:
            self.overlay_position.set(options[0])  # Set to first option if current is not valid

    def choose_overlay_color(self):
        color = colorchooser.askcolor(title="Choose overlay background color")
        if color[1]:  # color is None if dialog is cancelled
            self.overlay_color.set(color[1])
            self.update_color_button()

    def update_color_button(self):
        if hasattr(self, 'color_button'):
            self.color_button.config(bg=self.overlay_color.get())

    def update_current_prompt_display(self, prompt):
        try:
            if hasattr(self, 'current_prompt_display'):
                self.current_prompt_display.config(state='normal')
                self.current_prompt_display.delete(1.0, tk.END)
                self.current_prompt_display.insert(tk.END, prompt)
                self.current_prompt_display.config(state='disabled')
            else:
                print("Error: current_prompt_display widget not found")
        except Exception as e:
            print(f"Error updating current prompt display: {e}")

    def update_prompt_info(self, original_prompt, returned_prompt):
        print(f"Updating prompts - Original: {original_prompt}")
        print(f"Full returned data: {returned_prompt}")
        
        self.submitted_prompt.set(original_prompt)
        if self.enhance.get():
            # Try to extract the enhanced prompt
            enhanced_prompt = re.search(r'"([^"]*)"', returned_prompt)
            if enhanced_prompt:
                cleaned_prompt = enhanced_prompt.group(1)
            else:
                # If no quotes found, use the entire returned prompt
                cleaned_prompt = returned_prompt
            
            # Remove the original prompt if it appears at the end of the returned prompt
            cleaned_prompt = cleaned_prompt.replace(original_prompt.strip(), '').strip()
            
            print(f"Cleaned enhanced prompt: {cleaned_prompt}")
            self.returned_prompt.set(cleaned_prompt)
        else:
            self.returned_prompt.set(original_prompt)
        
        # Update the Text widgets
        if hasattr(self, 'submitted_prompt_display'):
            self.submitted_prompt_display.config(state='normal')
            self.submitted_prompt_display.delete(1.0, tk.END)
            self.submitted_prompt_display.insert(tk.END, self.submitted_prompt.get())
            self.submitted_prompt_display.config(state='disabled')
        
        if hasattr(self, 'returned_prompt_display'):
            self.returned_prompt_display.config(state='normal')
            self.returned_prompt_display.delete(1.0, tk.END)
            self.returned_prompt_display.insert(tk.END, self.returned_prompt.get())
            self.returned_prompt_display.config(state='disabled')
        
        # ...existing code...

    # ...existing code...
    def set_interval(self):
        """Show professional interval setting dialog"""
        interval_window = tk.Toplevel(self.master)
        interval_window.title("Generation Interval Settings")
        interval_window.geometry("350x200")
        interval_window.configure(bg=self.colors['bg_tertiary'])
        interval_window.resizable(False, False)

        # Set the icon for the interval window
        try:
            # Get the correct path for the icon file (works for both script and executable)
            if hasattr(sys, '_MEIPASS'):
                # Running as PyInstaller executable
                icon_path = os.path.join(sys._MEIPASS, "WallifyAI-logo.ico")
            else:
                # Running as script
                icon_path = "WallifyAI-logo.ico"
            
            if os.path.exists(icon_path):
                interval_window.iconbitmap(icon_path)
        except tk.TclError as e:
            print(f"Error setting icon for interval window: {e}")

        # Main frame with professional styling
        main_frame = ttk.Frame(interval_window, padding="20", style="Card.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title_label = ttk.Label(main_frame, text="Set Generation Interval", style="Heading.TLabel")
        title_label.pack(pady=(0, 15))

        # Description
        desc_label = ttk.Label(main_frame, 
                              text="Configure how often new wallpapers are generated\n(minimum 0.1 minutes)", 
                              style="Body.TLabel", justify=tk.CENTER)
        desc_label.pack(pady=(0, 15))

        # Input frame
        input_frame = ttk.Frame(main_frame, style="Card.TFrame")
        input_frame.pack(pady=(0, 20))

        ttk.Label(input_frame, text="Minutes:", style="Body.TLabel").pack(side=tk.LEFT)
        interval_entry = ttk.Entry(input_frame, width=10, font=("Segoe UI", 10), justify=tk.CENTER)
        interval_entry.insert(0, str(self.interval / 60))
        interval_entry.pack(side=tk.LEFT, padx=(5, 0))
        interval_entry.focus()

        # Button frame
        button_frame = ttk.Frame(main_frame, style="Card.TFrame")
        button_frame.pack()

        def save_interval():
            try:
                new_interval = max(0.1, float(interval_entry.get())) * 60
                self.interval = new_interval
                print(f"Interval set to {self.interval} seconds.")
                self.save_settings()
                interval_window.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", 
                                   "Please enter a valid number for the interval.", 
                                   parent=interval_window)

        def cancel():
            interval_window.destroy()

        # Bind Enter key to save
        interval_entry.bind('<Return>', lambda e: save_interval())
        interval_window.bind('<Escape>', lambda e: cancel())

        ttk.Button(button_frame, text="Save", command=save_interval, 
                  style="Primary.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=cancel, 
                  style="Secondary.TButton").pack(side=tk.LEFT)

        # Center the window
        interval_window.transient(self.master)
        interval_window.grab_set()
        
        # Center on parent window
        interval_window.update_idletasks()
        x = (self.master.winfo_x() + (self.master.winfo_width() // 2)) - (interval_window.winfo_width() // 2)
        y = (self.master.winfo_y() + (self.master.winfo_height() // 2)) - (interval_window.winfo_height() // 2)
        interval_window.geometry(f"+{x}+{y}")
        
        self.master.wait_window(interval_window)

    def toggle_always_on_top(self):
        self.master.wm_attributes("-topmost", self.always_on_top.get())
        self.save_settings()

    def toggle_start_stop(self):
        if self.is_running:
            self.stop_setter()
        else:
            self.start_setter()

    def on_history_select(self, event):
        selected_prompt = self.history_var.get()
        self.prompt_entry.delete(1.0, tk.END)
        self.prompt_entry.insert(tk.END, selected_prompt)

    def add_to_history(self, prompt):
        if prompt:
            # Remove the prompt if it already exists in the history
            self.prompt_history = deque([p for p in self.prompt_history if p != prompt], maxlen=20)
            # Add the prompt to the beginning of the history
            self.prompt_history.appendleft(prompt)
            self.update_history_dropdown()
            self.save_history()
            print(f"Added to history: {prompt}")  # Debug print

    def remove_from_history(self, prompt):
        if prompt in self.prompt_history:
            self.prompt_history.remove(prompt)
            self.update_history_dropdown()
            self.save_history()

    def remove_selected_from_history(self):
        selected = self.history_var.get()
        if selected:
            self.remove_from_history(selected)

    def update_history_dropdown(self):
        history_list = list(self.prompt_history)
        self.history_dropdown['values'] = history_list
        if history_list:
            self.history_var.set(history_list[0])
        print(f"Updated history dropdown. Current history: {history_list}")  # Debug print

    def save_history(self):
        with open('prompt_history.json', 'w') as f:
            json.dump(list(self.prompt_history), f)
        print(f"Saved history: {list(self.prompt_history)}")  # Debug print

    def load_history(self):
        if os.path.exists('prompt_history.json'):
            with open('prompt_history.json', 'r') as f:
                self.prompt_history = deque(json.load(f), maxlen=20)
        else:
            self.prompt_history = deque(maxlen=20)
        self.update_history_dropdown()
        print(f"Loaded history: {list(self.prompt_history)}")  # Debug print

    def start_setter(self):
        prompt = self.prompt_entry.get("1.0", tk.END).strip()
        if not prompt:
            if self.prompt_history:
                prompt = self.prompt_history[0]
                self.prompt_entry.insert(tk.END, prompt)
            else:
                messagebox.showerror("Missing Prompt", "Please enter a prompt or ensure there is one in history.")
                return
        self.add_to_history(prompt)

        try:
            self.update_current_prompt_display(prompt)
        except Exception as e:
            print(f"Error updating current prompt display: {e}")

        self.is_running = True
        self.start_stop_button.config(text="Stop Generation")
        self.current_request_id = random.randint(1, 1000000)
        self.setter_thread = threading.Thread(target=self.run_setter, args=(prompt, self.interval, self.current_request_id))
        self.setter_thread.start()

        # Start the background process without showing command prompt or logs
        subprocess.Popen(
            ["python", "-c", "print('Background process running...')"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

    def stop_setter(self):
        self.is_running = False
        self.current_request_id = None  # This will invalidate any ongoing requests
        if self.setter_thread and self.setter_thread.is_alive():
            self.setter_thread.join(timeout=1)  # Wait for the thread to finish, but not indefinitely
        self.start_stop_button.config(text="Start Generation")

    def run_setter(self, prompt, interval, request_id):
        while self.is_running and request_id == self.current_request_id:
            try:
                self.fetch_and_set_background(prompt, request_id)
            except Exception as e:
                print(f"Error setting background: {e}")
            time.sleep(interval)

    def get_image_dimensions(self, style):
        return self.style_dimensions.get(style, (1920, 1080))

    def log_process_output(self, message):
        """Log messages to the process output window."""
        self.process_output_text.config(state="normal")
        self.process_output_text.insert(tk.END, message + "\n")
        self.process_output_text.config(state="disabled")
        self.process_output_text.see(tk.END)

    def fetch_and_set_background(self, prompt, request_id):
        max_retries = 5
        retry_delay = 5
        for attempt in range(max_retries):
            if not self.is_running or request_id != self.current_request_id:
                self.log_process_output("Operation cancelled.")
                return
            try:
                seed = random.randint(1, 1000000)
                enhance_param = "true" if self.enhance.get() else "false"
                style = self.wallpaper_style.get()

                width, height = self.get_image_dimensions(style)
                self.log_process_output(f"Style: {style}, Dimensions: {width}x{height}")

                self.log_process_output(f"Using user prompt: {prompt}")

                # Hide the URL from the process output
                self.log_process_output("Fetching image from the server...")

                url = f"https://image.pollinations.ai/prompt/{prompt}?nologo=true&nofeed=true&model={self.model.get()}&negative_prompt=low%20resolution%2C%20low%20quality%2C%20blurry%2C%20pixelated%2C%20artifacts%2C%20visual%20noise%2C%20distorted%20anatomy%2C%20bad%20proportions%2C%20malformed%20hands%2C%20extra%20fingers%2C%20missing%20fingers%2C%20poor%20facial%20symmetry%2C%20deformed%20face%2C%20extra%20limbs%2C%20missing%20limbs%2C%20unnatural%20colors%2C%20unnatural%20lighting%2C%20creepy%20smile%2C%20angry%20expression%2C%20sad%20expression%2C%20abstract%2C%20cartoon%2C%20anime%2C%20sketch%2C%20illustration%2C%20cgi%2C%20render%2C%20watermark%2C%20text%2C%20logo%2C%20writing%2C%20bad%20composition%2C%20poorly%20lit%2C%20overexposed%2C%20underexposed%2C%20grainy%2C%20jpeg%20artifacts%2C%20twisted%20pose%2C%20awkward%20pose%2C%20distorted%20body%2C%20unrealistic%2C%20grotesque%2C%20duplicate%20body%20parts&enhance={enhance_param}&seed={seed}&width={width}&height={height}"

                response = requests.get(url, timeout=45)

                if response.status_code == 200 and request_id == self.current_request_id:
                    self.log_process_output("Image fetched successfully.")
                    image_data = response.content

                    try:
                        image = Image.open(io.BytesIO(image_data))
                        actual_width, actual_height = image.size
                        self.log_process_output(f"Actual image dimensions: {actual_width}x{actual_height}")
                        
                        # Extract metadata from EXIF
                        exif_data = image.info.get('exif', b'')
                        if exif_data and self.enhance.get():
                            # Find the JSON string in the EXIF data
                            json_match = re.search(b'{"prompt":.*}', exif_data)
                            if json_match:
                                json_str = json_match.group(0).decode('utf-8')
                                try:
                                    metadata_dict = json.loads(json_str)
                                    returned_prompt = metadata_dict.get('prompt', 'Unable to retrieve returned prompt')
                                    self.update_prompt_info(prompt, returned_prompt)
                                except json.JSONDecodeError as e:
                                    print(f"Failed to parse JSON in metadata: {e}")
                                    self.update_prompt_info(prompt, prompt)
                            else:
                                print("No JSON data found in EXIF")
                                self.update_prompt_info(prompt, prompt)
                        else:
                            self.update_prompt_info(prompt, prompt)
                        
                        if (actual_width, actual_height) != (width, height):
                            print(f"Warning: Received image dimensions ({actual_width}x{actual_height}) "
                                  f"do not match requested dimensions ({width}x{height})")
                    except UnidentifiedImageError:
                        self.log_process_output("Error: Received data is not a valid image. Retrying...")
                        raise  # This will trigger the retry mechanism
                
                    timestamp = int(time.time())
                    image_path = os.path.join(self.image_dir, f"background_{timestamp}.png")
                    image.save(image_path, 'PNG')
                    self.log_process_output(f"Image saved to {image_path}")
                    
                    self.set_windows_background(image_path)
                    
                    self.cleanup_background_images()
                    return
                else:
                    self.log_process_output(f"Failed to fetch image. Status code: {response.status_code}")

            except (RequestException, UnidentifiedImageError) as e:
                self.log_process_output(f"Error on attempt {attempt + 1}: {e}")
            except Exception as e:
                self.log_process_output(f"Unexpected error on attempt {attempt + 1}: {e}")

            if attempt < max_retries - 1:
                self.log_process_output(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2

        self.log_process_output("Failed to fetch and set background after all retries.")
    
    def save_settings(self):
        settings = {
            "enhance": self.enhance.get(),
            "wallpaper_style": self.wallpaper_style.get(),
            "interval": self.interval,
            "always_on_top": self.always_on_top.get(),
            "model": self.model.get(),
            "overlay_opacity": self.overlay_opacity.get(),
            "overlay_position": self.overlay_position.get(),
            "use_drop_shadow": self.use_drop_shadow.get(),
            "overlay_color": self.overlay_color.get()
        }
        with open('background_settings.json', 'w') as f:
            json.dump(settings, f)

    def load_settings(self):
        if os.path.exists('background_settings.json'):
            with open('background_settings.json', 'r') as f:
                settings = json.load(f)
                self.enhance.set(settings.get("enhance", False))
                self.wallpaper_style.set(settings.get("wallpaper_style", "fill"))
                self.interval = max(300, settings.get("interval", 300))
                self.always_on_top.set(settings.get("always_on_top", False))
                self.model.set(settings.get("model", "flux"))
                self.overlay_opacity.set(settings.get("overlay_opacity", 128))
                self.overlay_position.set(settings.get("overlay_position", "top_right"))
                self.use_drop_shadow.set(settings.get("use_drop_shadow", False))
                self.overlay_color.set(settings.get("overlay_color", "#000000"))
                self.update_position_options()
                self.update_color_button()
                self.toggle_always_on_top()
        self.apply_loaded_settings()

    def set_windows_background(self, image_path):
        try:
            pythoncom.CoInitialize()
            abs_path = os.path.abspath(image_path)
            if not os.path.exists(abs_path):
                raise FileNotFoundError(f"The file {abs_path} does not exist.")

            style = self.wallpaper_style.get()
            
            idw = comtypes.CoCreateInstance(CLSID_DesktopWallpaper, interface=IDesktopWallpaper)
            
            # Set the wallpaper
            try:
                idw.SetWallpaper(None, abs_path)
                print(f"Wallpaper set to {abs_path}")
            except Exception as e:
                print(f"Error setting wallpaper: {e}")
            
            # Set the style
            try:
                style_map = {
                    "center": DESKTOP_WALLPAPER_POSITION.DWPOS_CENTER,
                    "tile": DESKTOP_WALLPAPER_POSITION.DWPOS_TILE,
                    "stretch": DESKTOP_WALLPAPER_POSITION.DWPOS_STRETCH,
                    "fit": DESKTOP_WALLPAPER_POSITION.DWPOS_FIT,
                    "fill": DESKTOP_WALLPAPER_POSITION.DWPOS_FILL,
                    "span": DESKTOP_WALLPAPER_POSITION.DWPOS_SPAN
                }
                idw.SetPosition(style_map.get(style, DESKTOP_WALLPAPER_POSITION.DWPOS_FILL))
                print(f"Wallpaper style set to {style}")
            except Exception as e:
                print(f"Error setting wallpaper style: {e}")
            
        except Exception as e:
            print(f"Unexpected error in set_windows_background: {e}")
        finally:
            pythoncom.CoUninitialize()

    # ...existing code...

    def apply_loaded_settings(self):
        # Update Start/Stop button with professional text
        if hasattr(self, 'start_stop_button'):
            text = "Stop Generation" if getattr(self, 'is_running', False) else "Start Generation"
            self.start_stop_button.config(text=text)
        
        # Update Enhance checkbox
        if hasattr(self, 'enhance'):
            self.enhance.set(self.enhance.get())
        
        # Update Wallpaper Style dropdown
        if hasattr(self, 'wallpaper_style'):
            self.wallpaper_style.set(self.wallpaper_style.get())
        
        # Update Model dropdown
        if hasattr(self, 'model'):
            self.model.set(self.model.get())
        
        # Update Overlay Opacity scale
        if hasattr(self, 'overlay_opacity'):
            self.overlay_opacity.set(self.overlay_opacity.get())
        
        # Update Overlay Position dropdown
        if hasattr(self, 'overlay_position'):
            self.overlay_position.set(self.overlay_position.get())
        
        # Update Overlay Color button
        if hasattr(self, 'color_button'):
            self.color_button.config(bg=self.overlay_color.get())
        
        # Update Drop Shadow checkbox
        if hasattr(self, 'use_drop_shadow'):
            self.use_drop_shadow.set(self.use_drop_shadow.get())
        
        # Update Always on Top
        if hasattr(self, 'always_on_top'):
            self.always_on_top.set(self.always_on_top.get())
        
        # Trigger necessary UI updates
        self.update_position_options()
        self.update_color_button()
        self.toggle_always_on_top()  # This line was mistakenly removed and is now added back

    def on_closing(self):
        self.stop_setter()
        if self.setter_thread and self.setter_thread.is_alive():
            self.setter_thread.join(timeout=5)
        self.save_settings()
        self.master.destroy()

    def show_license(self):
        """Show license information with professional styling"""
        version = "v1.0.0"
        license_text = f"""WallifyAI {version} - MIT License

Copyright (c) 2024–2025 DevSyst

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
        
        messagebox.showinfo("License Information", license_text)

if __name__ == "__main__":
    app = DevsystBackgroundSetter()
    app.master.mainloop()