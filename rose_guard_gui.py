import tkinter as tk
from tkinter import scrolledtext, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import PRIMARY, SUCCESS, DANGER, INFO, WARNING
from ttkbootstrap.dialogs import Messagebox
from rose_guard_core import SecurityConfig, PasswordHashSimulator, AttackEngine, MetricsCollector
import threading
import queue
from tkinter.font import Font
import webbrowser
from PIL import Image, ImageTk
import os
import time
import csv
from file_manager import FileManager
import logging
from logging_config import configure_logging

logger = configure_logging()

class RoseGuardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ROSE GUARD - Robust Offensive Security Evaluator Guard | Advanced Password Security Testing")
        self.root.geometry("1400x900")
        
        # Set minimum window size for better UX
        self.root.minsize(1000, 700)

        # Enhanced theme configuration
        style = ttk.Style()
        self.current_theme = self.root.style.theme_use()
        
        # Modern color palette with dark mode support
        self.is_dark_mode = self.current_theme in ['darkly', 'cyborg', 'superhero', 'vapor', 'solar']
        
        if self.is_dark_mode:
            self.colors = {
                'primary': '#a5b4fc',      # Brighter indigo for dark mode
                'secondary': '#c4b5fd',    # Brighter purple
                'success': '#4ade80',      # Brighter green
                'danger': '#ff8585',       # Brighter red
                'warning': '#fcd34d',      # Brighter amber
                'info': '#93c5fd',         # Brighter blue
                'dark': '#ffffff',         # White text on dark bg
                'light': '#1e293b',        # Dark bg
                'card': '#1e293b',         # Dark cards
                'border': '#475569',       # More visible border
                'text': '#ffffff',         # Pure white text for maximum contrast
                'text_secondary': '#cbd5e1', # Lighter secondary text
                'bg': '#0f172a',           # Main background
                'output_bg': '#1e293b',    # Output area bg
                'output_fg': '#ffffff'     # White output text
            }
        else:
            self.colors = {
                'primary': '#6366f1',      # Modern indigo
                'secondary': '#8b5cf6',    # Purple
                'success': '#10b981',      # Green
                'danger': '#ef4444',       # Red
                'warning': '#f59e0b',      # Amber
                'info': '#3b82f6',         # Blue
                'dark': '#1e293b',         # Dark text
                'light': '#f8fafc',        # Very light gray
                'card': '#ffffff',         # White for cards
                'border': '#e2e8f0',       # Light border
                'text': '#1e293b',         # Dark text
                'text_secondary': '#64748b', # Secondary text
                'bg': '#f8fafc',           # Main background
                'output_bg': '#f8fafc',    # Output area bg
                'output_fg': '#1e293b'     # Output text
            }
        
        # Enhanced card styles with shadows
        style.configure('Card.TFrame', 
                       background=self.colors['card'],
                       relief='flat')
        style.configure('MainBg.TFrame', 
                       background=self.colors['light'])
        
        # Modern header with gradient effect
        style.configure('Header.TFrame', 
                       background=self.colors['dark'])
        style.configure('Header.TLabel', 
                       background=self.colors['dark'],
                       foreground='white',
                       font=('Segoe UI', 28, 'bold'))
        style.configure('Subheader.TLabel',
                       background=self.colors['dark'],
                       foreground='#94a3b8',
                       font=('Segoe UI', 13))
        style.configure('Card.TLabel',
                       background=self.colors['card'],
                       font=('Segoe UI', 11))
        
        # Enhanced font sizes for better visibility
        self.font_sizes = {
            'title': 32,
            'subtitle': 16,
            'heading': 22,
            'subheading': 18,
            'body': 14,
            'small': 12
        }
        
        # Enhanced label frames
        style.configure('Primary.TLabelframe',
                       borderwidth=2,
                       relief='solid')
        style.configure('Primary.TLabelframe.Label',
                       font=('Segoe UI', 11, 'bold'),
                       foreground=self.colors['primary'])
        
        # Create menu
        self.create_menu_bar()
        
        # Load config
        self.config = SecurityConfig.load_config()
        self.hash_simulator = PasswordHashSimulator(self.config)
        self.attack_engine = AttackEngine(self.config)
        self.metrics = MetricsCollector()
        
        # Queue for thread-safe updates
        self.queue = queue.Queue()

        # EMA smoothing state for attempts/sec and ETA
        self.ema_rate = None
        self.ema_alpha = 0.15  # smoothing factor; smaller = smoother
        self.last_progress_count = 0
        self.last_progress_time = None

        self.create_gui()
        self.update_output()
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Session", command=self.reset_session)
        file_menu.add_command(label="Open Wordlist", command=self.browse_wordlist)
        file_menu.add_separator()
        file_menu.add_command(label="Export Results", command=self.export_results)
        file_menu.add_command(label="Save Report", command=self.save_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        themes = ['darkly', 'cosmo', 'flatly', 'litera', 'minty', 
                 'pulse', 'sandstone', 'united', 'yeti']
        for theme in themes:
            theme_menu.add_command(
                label=theme.capitalize(),
                command=lambda t=theme: self.change_theme(t)
            )
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(
            label="Documentation", 
            command=lambda: webbrowser.open("https://github.com/roseycodes")
        )
        help_menu.add_command(label="About", command=self.show_about)

    def reset_session(self):
        """Reset the application to initial state as though it just launched"""
        if Messagebox.show_question(
            "Reset Session",
            "This will reset the application to its initial state. Continue?",
            parent=self.root
        ):
            # Reset core components
            self.config = SecurityConfig.load_config()
            self.hash_simulator = PasswordHashSimulator(self.config)
            self.attack_engine = AttackEngine(self.config)
            self.metrics = MetricsCollector()
            
            # Reset queue and analysis state
            self.queue = queue.Queue()
            self.ema_rate = None
            self.last_progress_count = 0
            self.last_progress_time = None
            
            # Reset UI elements
            if hasattr(self, 'output'):
                self.output.delete(1.0, tk.END)
            if hasattr(self, 'progress'):
                self.progress.configure(value=0)
            if hasattr(self, 'password_var'):
                self.password_var.set('')
            if hasattr(self, 'wordlist_var'):
                self.wordlist_var.set('')
            if hasattr(self, 'attack_type_var'):
                self.attack_type_var.set('dictionary')  # Reset to default attack type
            
            # Cancel any ongoing operations
            if hasattr(self, 'attack_thread') and isinstance(self.attack_thread, threading.Thread) and self.attack_thread.is_alive():
                self.stop_attack()
            
            # Reset file manager state
            if hasattr(self, 'file_manager'):
                self.file_manager = FileManager()
            
            # Clear any error states or warnings
            if hasattr(self, 'status_label'):
                self.status_label.configure(text="Ready")
            
            logger.info("Application state reset to initial configuration")
            
            # Show confirmation
            Messagebox.show_info(
                "Reset Complete",
                "The application has been reset to its initial state.",
                parent=self.root
            )
    
    def change_theme(self, theme_name):
        """Change application theme"""
        try:
            self.root.style.theme_use(theme_name)
            # Update color scheme based on new theme
            self.current_theme = theme_name
            self.is_dark_mode = theme_name in ['darkly', 'cyborg', 'superhero', 'vapor', 'solar']
            
            # Update colors
            if self.is_dark_mode:
                self.colors.update({
                    'text': '#e2e8f0',
                    'text_secondary': '#94a3b8',
                    'bg': '#0f172a',
                    'card': '#1e293b',
                    'output_bg': '#1e293b',
                    'output_fg': '#e2e8f0'
                })
            else:
                self.colors.update({
                    'text': '#1e293b',
                    'text_secondary': '#64748b',
                    'bg': '#f8fafc',
                    'card': '#ffffff',
                    'output_bg': '#f8fafc',
                    'output_fg': '#1e293b'
                })
            
            # Update output text widgets
            self.output.configure(bg=self.colors['output_bg'], fg=self.colors['output_fg'])
            self.metrics_text.configure(bg=self.colors['output_bg'], fg=self.colors['output_fg'])
            
        except Exception as e:
            Messagebox.show_error(
                "Theme Error",
                f"Failed to change theme: {str(e)}",
                parent=self.root
            )
    
    def calculate_password_strength(self, password):
        """Calculate password strength score between 0-100"""
        score = 0
        feedback = []
        
        # Length score (up to 30 points)
        length = len(password)
        score += min(30, length * 2)
        
        if length < 8:
            feedback.append("Too short")
        elif length >= 12:
            feedback.append("Good length")

        # Character variety score (up to 40 points)
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        variety_score = (has_lower + has_upper + has_digit + has_special) * 10
        score += variety_score
        
        if not has_lower or not has_upper:
            feedback.append("Mix upper & lowercase")
        if not has_digit:
            feedback.append("Add numbers")
        if not has_special:
            feedback.append("Add special chars")

        # Pattern penalty (up to -30 points)
        if password.lower() in ['password', '12345678', 'qwerty']:
            score -= 30
            feedback.append("Common password")
        elif password.isdigit():
            score -= 20
            feedback.append("Numbers only")
        elif password.isalpha():
            score -= 10
            feedback.append("Letters only")

        # Ensure score is between 0-100
        score = max(0, min(100, score))
        
        # Determine strength level and color
        if score < 30:
            level = "Very Weak"
            color = self.colors['danger']
        elif score < 50:
            level = "Weak"
            color = self.colors['warning']
        elif score < 70:
            level = "Moderate"
            color = self.colors['info']
        elif score < 90:
            level = "Strong"
            color = self.colors['primary']
        else:
            level = "Very Strong"
            color = self.colors['success']
        
        return score, level, color, feedback

    def update_password_strength(self, *args):
        """Update password strength meter"""
        password = self.password_var.get()
        score, level, color, feedback = self.calculate_password_strength(password)
        
        # Map colors to proper bootstrap styles
        style_map = {
            self.colors['danger']: 'danger',
            self.colors['warning']: 'warning',
            self.colors['info']: 'info',
            self.colors['primary']: 'primary',
            self.colors['success']: 'success'
        }
        bootstyle = style_map.get(color, 'primary')
        
        # Update progress bar
        self.strength_meter.configure(value=score, bootstyle=bootstyle)
        
        # Update label
        feedback_text = f"{level} ({score}%)"
        if feedback:
            feedback_text += f"\n{' • '.join(feedback)}"
        self.strength_feedback.configure(text=feedback_text, foreground=color)

    def show_hash_info(self):
        """Show information about the selected hash algorithm"""
        info = {
            'md5': ('⚠️ MD5 (Not Recommended)', 
                   'Fast but cryptographically broken. Use only for testing.\n\n'
                   'Vulnerabilities:\n'
                   '• Proven collision attacks\n'
                   '• Very fast to compute\n'
                   '• No salt by default'),
            
            'sha256': ('SHA-256 (Basic Security)', 
                      'Cryptographic hash, but vulnerable to GPU-based attacks.\n\n'
                      'Characteristics:\n'
                      '• Cryptographically secure\n'
                      '• No built-in salt\n'
                      '• Vulnerable to rainbow tables'),
            
            'bcrypt': ('🔒 bcrypt (Recommended)', 
                      'Modern password hashing with built-in salt.\n\n'
                      'Benefits:\n'
                      '• Adaptive work factor\n'
                      '• Built-in salt\n'
                      '• GPU-resistant\n'
                      '• Industry standard'),
            
            'argon2': ('🛡️ Argon2 (Most Secure)', 
                      'Modern memory-hard algorithm. Best for high-security.\n\n'
                      'Features:\n'
                      '• Memory-hard design\n'
                      '• Configurable parameters\n'
                      '• Winner of PHC\n'
                      '• Ideal for high-value targets')
        }
        
        hash_type = self.hash_type_var.get()
        title, desc = info.get(hash_type, ('Unknown', 'No information available'))
        
        Messagebox.show_info(
            title=title,
            message=desc,
            parent=self.root
        )

    def show_about(self):
        """Show about dialog"""
        about_text = """
        🛡️ ROSE GUARD
        Robust Offensive Security Evaluator Guard
                
        Version: 1.0.0
        
        Features:
        • Multiple hash algorithms
        • Dictionary attacks
        • Brute force attacks
        • Hybrid attacks
        • Performance metrics
        • Security analysis
        
        Created by: OGBODO ROSEMARY CHIAMAKA
        License: MIT
        """
        
        Messagebox.show_info(
            title="About ROSE GUARD",
            message=about_text,
            parent=self.root
        )

    def create_gui(self):
        # Create main container with modern background
        main_container = ttk.Frame(self.root, style='MainBg.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure main_container grid
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Enhanced header with icon and modern styling
        header = ttk.Frame(main_container, style='Header.TFrame', height=120)
        header.grid(row=0, column=0, sticky='ew')
        header.grid_propagate(False)
        
        # Header left side
        header_left = ttk.Frame(header, style='Header.TFrame')
        header_left.pack(side=tk.LEFT, padx=30, pady=20)
        
        # Shield icon and title
        ttk.Label(
            header_left,
            text="🛡️",
            font=('Segoe UI Emoji', 40),
            background=self.colors['dark'],
            foreground='#000000'  # Black shield for visibility
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        title_frame = ttk.Frame(header_left, style='Header.TFrame')
        title_frame.pack(side=tk.LEFT)
        
        ttk.Label(
            title_frame,
            text="ROSE GUARD",
            style='Header.TLabel',
            foreground='#000000'  # Black text for visibility
        ).pack(anchor=tk.W)
        
        ttk.Label(
            title_frame,
            text="Robust Offensive Security Evaluator",
            style='Subheader.TLabel',
            foreground='#374151'  # Dark gray text for visibility
        ).pack(anchor=tk.W)
        
        # Header right side - quick stats
        header_right = ttk.Frame(header, style='Header.TFrame')
        header_right.pack(side=tk.RIGHT, padx=30, pady=20)
        
        # Version badge
        version_frame = ttk.Frame(header_right, style='Header.TFrame')
        version_frame.pack()
        ttk.Label(
            version_frame,
            text="v1.0.0",
            font=('Segoe UI', 10),
            background='#374151',
            foreground='#10b981',
            padding=(10, 5)
        ).pack()
        
        # Main content area with padding and modern card design
        content = ttk.Frame(main_container, style='MainBg.TFrame')
        content.grid(row=1, column=0, sticky='nsew', padx=25, pady=25)
        
        # Configure content grid
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)
        
        # Main tabs with enhanced styling
        notebook = ttk.Notebook(content, bootstyle="primary")
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Test tab with card-style frame
        test_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(test_frame, text="  🔐 Password Testing  ")
        
        # Create a scrollable canvas for better organization
        canvas_frame = ttk.Frame(test_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        test_canvas = tk.Canvas(canvas_frame, bg=self.colors['card'], highlightthickness=0)
        test_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=test_canvas.yview)
        test_scrollable = ttk.Frame(test_canvas, style='Card.TFrame')
        
        test_scrollable.bind(
            "<Configure>",
            lambda e: test_canvas.configure(scrollregion=test_canvas.bbox("all"))
        )
        
        # Configure canvas to resize with window
        def configure_canvas(event):
            # Update the width of the canvas to fit the frame
            canvas_width = event.width
            test_canvas.itemconfig("test_scrollable", width=canvas_width)
        
        test_canvas.bind('<Configure>', configure_canvas)
        
        # Create window with tag for resizing
        test_canvas.create_window((0, 0), window=test_scrollable, anchor="nw", tags="test_scrollable")
        test_canvas.configure(yscrollcommand=test_scrollbar.set)
        
        test_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        test_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enhanced Input Card with modern styling and responsive padding
        input_card = ttk.LabelFrame(
            test_scrollable,
            text="  🔑 Password Configuration  ",
            padding=(30, 25, 30, 25),
            bootstyle=PRIMARY
        )
        input_card.pack(fill=tk.X, padx=20, pady=15)
        
        # Password input with enhanced styling
        # Password input container
        pw_container = ttk.Frame(input_card)
        pw_container.pack(fill=tk.X, pady=(12, 0))
        
        # Password input frame
        pw_frame = ttk.Frame(pw_container)
        pw_frame.pack(fill=tk.X, expand=True, padx=5)
        
        ttk.Label(
            pw_frame,
            text="Password to Test:",
            font=('Segoe UI', 12, 'bold'),
            foreground=self.colors['text']
        ).pack(side=tk.LEFT, padx=(5, 15))
        
        # Password input with eye icon
        pw_input_frame = ttk.Frame(pw_frame)
        pw_input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.password_var = tk.StringVar()
        self.password_var.trace_add('write', self.update_password_strength)
        
        pw_entry = ttk.Entry(
            pw_input_frame,
            textvariable=self.password_var,
            show="●",
            font=('Segoe UI', 12),
            bootstyle=PRIMARY
        )
        pw_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        
        # Show/Hide password toggle with icon - larger touch target
        self.show_password = tk.BooleanVar(value=False)
        
        def toggle_password_visibility():
            """Toggle password visibility and update button text"""
            if self.show_password.get():
                # Currently showing password, hide it
                pw_entry.configure(show="●")
                show_btn.configure(text="👁️")
                self.show_password.set(False)
            else:
                # Currently hiding password, show it
                pw_entry.configure(show="")
                show_btn.configure(text="🙈")
                self.show_password.set(True)
        
        show_btn = ttk.Button(
            pw_input_frame,
            text="👁️",
            command=toggle_password_visibility,
            bootstyle=(INFO, "outline"),
            width=4
        )
        show_btn.pack(side=tk.RIGHT, padx=8, ipady=4)
        
        # Password strength meter frame
        strength_frame = ttk.Frame(pw_container)
        strength_frame.pack(fill=tk.X, expand=True, padx=10, pady=(5, 10))
        
        # Progress bar for strength
        self.strength_meter = ttk.Progressbar(
            strength_frame,
            mode='determinate',
            bootstyle=PRIMARY,
            maximum=100,
            value=0
        )
        self.strength_meter.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Feedback label with larger font and word wrapping
        self.strength_feedback = ttk.Label(
            strength_frame,
            text="Enter a password",
            font=('Segoe UI', 11, 'bold'),
            bootstyle=PRIMARY,
            wraplength=200  # Enable word wrapping
        )
        self.strength_feedback.pack(side=tk.LEFT, padx=10)
        
        # Hash type selection with enhanced styling
        hash_frame = ttk.Frame(input_card)
        hash_frame.pack(fill=tk.X, pady=12)
        
        ttk.Label(
            hash_frame,
            text="Hash Algorithm:",
            font=('Segoe UI', 12, 'bold'),
            foreground=self.colors['text']
        ).pack(side=tk.LEFT, padx=(5, 15))
        
        self.hash_type_var = tk.StringVar(value="bcrypt")
        hash_types = ttk.Combobox(
            hash_frame,
            textvariable=self.hash_type_var,
            values=['md5', 'sha256', 'bcrypt', 'argon2'],
            state="readonly",
            font=('Segoe UI', 12),
            bootstyle=PRIMARY
        )
        hash_types.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, ipady=4)
        
        # Info button with better styling and larger touch target
        info_btn = ttk.Button(
            hash_frame,
            text="ℹ️ Info",
            command=self.show_hash_info,
            bootstyle=(INFO, "outline"),
            width=10
        )
        info_btn.pack(side=tk.LEFT, padx=10, ipady=4)
        
        # Attack Methods Card with enhanced styling and more padding
        attack_card = ttk.LabelFrame(
            test_scrollable,
            text="  ⚡ Attack Methods  ",
            padding=(30, 25, 30, 25),
            bootstyle=WARNING
        )
        attack_card.pack(fill=tk.X, padx=20, pady=15)
        
        # Wordlist selection with modern design
        wordlist_frame = ttk.Frame(attack_card)
        wordlist_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Wordlist section header
        header_frame = ttk.Frame(wordlist_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(
            header_frame,
            text="📄 Wordlist File:",
            font=('Segoe UI', 12, 'bold'),
            foreground=self.colors['text']
        ).pack(side=tk.LEFT, padx=(5, 15))
        
        # Wordlist content frame
        content_frame = ttk.Frame(wordlist_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection frame
        select_frame = ttk.Frame(content_frame)
        select_frame.pack(fill=tk.X)
        
        self.wordlist_var = tk.StringVar(value=self.config['wordlist'])
        self.wordlist_var.trace_add('write', self.update_wordlist_preview)
        
        entry = ttk.Entry(
            select_frame,
            textvariable=self.wordlist_var,
            font=('Segoe UI', 11),
            bootstyle=WARNING
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5), ipady=4)
        
        browse_btn = ttk.Button(
            select_frame,
            text="📁 Browse",
            command=self.browse_wordlist,
            bootstyle=(WARNING, "outline"),
            width=12
        )
        browse_btn.pack(side=tk.RIGHT, padx=5, ipady=4)
        
        # Preview frame
        self.preview_frame = ttk.Frame(content_frame)
        self.preview_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # File info
        info_frame = ttk.Frame(self.preview_frame)
        info_frame.pack(fill=tk.X)
        
        self.size_label = ttk.Label(
            info_frame,
            text="📊 Size: --",
            font=('Segoe UI', 10),
            foreground=self.colors['text_secondary']
        )
        self.size_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.count_label = ttk.Label(
            info_frame,
            text="📝 Words: --",
            font=('Segoe UI', 10),
            foreground=self.colors['text_secondary']
        )
        self.count_label.pack(side=tk.LEFT)
        
        # Sample preview with better visibility
        self.preview_text = ttk.Label(
            self.preview_frame,
            text="",
            font=('Segoe UI', 10),
            foreground=self.colors['text_secondary'],
            wraplength=500,
            justify=tk.LEFT
        )
        self.preview_text.pack(fill=tk.X, pady=(8, 0))

        # Attack buttons with modern card design
        attack_buttons_frame = ttk.Frame(attack_card)
        attack_buttons_frame.pack(fill=tk.X, pady=10)
        
        # Description label with better visibility
        ttk.Label(
            attack_buttons_frame,
            text="Select an attack method to test password security:",
            font=('Segoe UI', 11),
            foreground=self.colors['text']
        ).pack(pady=(0, 18))
        
        # Create styled cards for each attack method with responsive grid
        cards_frame = ttk.Frame(attack_buttons_frame)
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure grid for responsive layout with better spacing
        cards_frame.columnconfigure(0, weight=1, minsize=280)
        cards_frame.columnconfigure(1, weight=1, minsize=280)
        cards_frame.columnconfigure(2, weight=1, minsize=280)
        cards_frame.rowconfigure(0, minsize=240)
        
        # Attack method descriptions
        attack_info = {
            'dictionary': {
                'icon': '📚',
                'title': 'Dictionary Attack',
                'desc': 'Tests password against a wordlist of common passwords and known leaks.',
                'style': SUCCESS,
                'hint': 'Best for finding common passwords and variations',
                'col': 0
            },
            'brute_force': {
                'icon': '⚡',
                'title': 'Brute Force',
                'desc': 'Systematically tries all possible character combinations.',
                'style': DANGER,
                'hint': 'Effective against short passwords with limited charset',
                'col': 1
            },
            'hybrid': {
                'icon': '🔀',
                'title': 'Hybrid Attack',
                'desc': 'Combines dictionary words with common patterns and numbers.',
                'style': INFO,
                'hint': 'Good for passwords that combine words and numbers',
                'col': 2
            }
        }

        for attack_type, info in attack_info.items():
            # Create card frame with more padding for better touch targets
            card = ttk.Frame(cards_frame, style='Card.TFrame', padding=10)
            card.grid(row=0, column=info['col'], padx=8, pady=8, sticky='nsew')
            
            # Add hover effect
            def on_enter(e, style=info['style']):
                e.widget.configure(cursor='hand2')
                e.widget.configure(style=f'{style}.TFrame')
            
            def on_leave(e):
                e.widget.configure(cursor='')
                e.widget.configure(style='Card.TFrame')
            
            card.bind('<Enter>', on_enter)
            card.bind('<Leave>', on_leave)
            
            # Icon and title
            header = ttk.Frame(card, style='Card.TFrame')
            header.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(
                header,
                text=info['icon'],
                font=('Segoe UI', 32),
                style='Card.TLabel'
            ).pack(side=tk.LEFT, padx=(0, 12))
            
            title_frame = ttk.Frame(header, style='Card.TFrame')
            title_frame.pack(side=tk.LEFT, fill=tk.X)
            
            ttk.Label(
                title_frame,
                text=info['title'],
                font=('Segoe UI', 13, 'bold'),
                style='Card.TLabel'
            ).pack(anchor=tk.W)
            
            ttk.Label(
                title_frame,
                text=info['hint'],
                font=('Segoe UI', 10),
                foreground=self.colors['text_secondary'],
                style='Card.TLabel'
            ).pack(anchor=tk.W, pady=(2, 0))
            
            # Description with better readability
            ttk.Label(
                card,
                text=info['desc'],
                font=('Segoe UI', 10),
                wraplength=220,
                justify=tk.LEFT,
                style='Card.TLabel'
            ).pack(fill=tk.X, padx=12, pady=(8, 12))
            
            # Attack button with larger touch target
            btn = ttk.Button(
                card,
                text=f"▶ Start {info['title']}",
                command=lambda t=attack_type: self.start_attack(t),
                bootstyle=info['style'],
                width=25
            )
            btn.pack(padx=12, pady=(0, 10), fill=tk.X, ipady=8)
            
            # Store button reference with consistent naming
            if attack_type == 'dictionary':
                self.dict_btn = btn
            elif attack_type == 'brute_force':
                self.brute_btn = btn
            elif attack_type == 'hybrid':
                self.hybrid_btn = btn

        # Stop button with prominent styling
        stop_frame = ttk.Frame(attack_buttons_frame)
        stop_frame.pack(pady=(15, 0))
        
        self.stop_btn = ttk.Button(
            stop_frame,
            text="⏹️ STOP ATTACK",
            command=self.stop_attack,
            bootstyle=DANGER,
            width=35
        )
        self.stop_btn.pack(ipady=8)
        self.stop_btn.configure(state='disabled')
        
        # Progress Card with enhanced styling and better padding
        progress_card = ttk.LabelFrame(
            test_scrollable,
            text="  📊 Attack Progress  ",
            padding=(30, 25, 30, 25),
            bootstyle=INFO
        )
        progress_card.pack(fill=tk.X, padx=20, pady=15)
        
        # Progress section with better organization
        progress_container = ttk.Frame(progress_card)
        progress_container.pack(fill=tk.X, pady=(0, 15))
        
        # Progress bar with modern styling and animation
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            progress_container,
            variable=self.progress_var,
            maximum=100,
            bootstyle="info-striped",
            length=600
        )
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Progress metrics frame
        metrics_frame = ttk.Frame(progress_container)
        metrics_frame.pack(fill=tk.X)
        
        # Status with icon
        status_frame = ttk.Frame(metrics_frame)
        status_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.status_var = tk.StringVar(value="⏳ Ready to start attack...")
        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 11),
            foreground=self.colors['text'],
            wraplength=500
        )
        self.status_label.pack(side=tk.LEFT, pady=5)
        
        # Speed metrics (attempts/sec)
        self.speed_frame = ttk.Frame(metrics_frame)
        self.speed_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.speed_var = tk.StringVar(value="")
        ttk.Label(
            self.speed_frame,
            text="⚡ Speed:",
            font=('Segoe UI', 11),
            foreground=self.colors['text']
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.speed_label = ttk.Label(
            self.speed_frame,
            textvariable=self.speed_var,
            font=('Segoe UI', 11, 'bold'),
            foreground=self.colors['primary']
        )
        self.speed_label.pack(side=tk.LEFT)
        
        # ETA frame
        self.eta_frame = ttk.Frame(metrics_frame)
        self.eta_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        self.eta_var = tk.StringVar(value="")
        ttk.Label(
            self.eta_frame,
            text="⏱️ ETA:",
            font=('Segoe UI', 11),
            foreground=self.colors['text']
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.eta_label = ttk.Label(
            self.eta_frame,
            textvariable=self.eta_var,
            font=('Segoe UI', 11, 'bold'),
            foreground=self.colors['primary']
        )
        self.eta_label.pack(side=tk.LEFT)
        
        # Output Card with enhanced styling and more padding
        output_card = ttk.LabelFrame(
            test_scrollable,
            text="  📝 Attack Results & Logs  ",
            padding=(30, 25, 30, 25),
            bootstyle=SUCCESS
        )
        output_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Output text with modern styling and better readability
        self.output = scrolledtext.ScrolledText(
            output_card,
            height=12,
            font=('Consolas', 11),
            bg=self.colors['output_bg'],
            fg=self.colors['output_fg'],
            relief='flat',
            padx=15,
            pady=15,
            wrap=tk.WORD,
            insertbackground=self.colors['text']  # Cursor color
        )
        self.output.pack(fill=tk.BOTH, expand=True)
        
        # Metrics tab with enhanced styling
        metrics_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(metrics_frame, text="  📈 Performance Metrics  ")
        
        # Metrics header
        metrics_header = ttk.Frame(metrics_frame, style='Card.TFrame')
        metrics_header.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(
            metrics_header,
            text="Performance Analysis Dashboard",
            font=('Segoe UI', 18, 'bold'),
            foreground=self.colors['text']
        ).pack(side=tk.LEFT)
        
        # Export button with modern styling and larger touch targets
        ttk.Button(
            metrics_header,
            text="📊 Export Results",
            command=self.export_results,
            bootstyle=SUCCESS,
            width=18
        ).pack(side=tk.RIGHT, padx=5, ipady=6)
        
        ttk.Button(
            metrics_header,
            text="💾 Save Report",
            command=self.save_report,
            bootstyle=PRIMARY,
            width=18
        ).pack(side=tk.RIGHT, padx=5, ipady=6)
        
        # Metrics content with modern styling and responsive layout
        metrics_content = ttk.Frame(metrics_frame, style='Card.TFrame')
        metrics_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.metrics_text = scrolledtext.ScrolledText(
            metrics_content,
            height=15,
            font=('Consolas', 11),
            bg=self.colors['output_bg'],
            fg=self.colors['output_fg'],
            relief='flat',
            padx=20,
            pady=20,
            wrap=tk.WORD,
            insertbackground=self.colors['text']  # Cursor color
        )
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind window resize events for responsive behavior
        self.root.bind('<Configure>', self.on_window_resize)
    
    def on_window_resize(self, event=None):
        """Handle window resize events for responsive layout"""
        if event and event.widget == self.root:
            window_width = event.width
            window_height = event.height
            
            # Adjust wraplength for text widgets based on window width
            if hasattr(self, 'status_label'):
                new_wraplength = max(400, int(window_width * 0.4))
                self.status_label.configure(wraplength=new_wraplength)
            
            if hasattr(self, 'preview_text'):
                preview_wraplength = max(400, int(window_width * 0.5))
                self.preview_text.configure(wraplength=preview_wraplength)
            
            # Scale font sizes for very large windows
            if window_width > 1600:
                scale_factor = min(1.2, window_width / 1600)
                # Apply subtle scaling if needed
            
            # Adjust output heights based on window height
            if hasattr(self, 'output') and window_height > 900:
                new_height = min(20, int((window_height - 600) / 20))
                self.output.configure(height=new_height)
    
    def update_wordlist_preview(self, *args):
        """Update wordlist preview information"""
        filename = self.wordlist_var.get()
        
        if not os.path.exists(filename):
            self.size_label.configure(text="📊 Size: --")
            self.count_label.configure(text="📝 Words: --")
            self.preview_text.configure(text="File not found")
            return
            
        try:
            # Get file size
            size_bytes = os.path.getsize(filename)
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes/1024:.1f} KB"
            else:
                size_str = f"{size_bytes/(1024*1024):.1f} MB"
            
            self.size_label.configure(text=f"📊 Size: {size_str}")
            
            # Count words and get sample
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                word_count = len([line for line in lines if line.strip()])
                
                # Get up to 5 sample words
                samples = [line.strip() for line in lines[:5] if line.strip()]
                if len(samples) > 0:
                    preview = "Sample words: " + ", ".join(samples)
                    if len(lines) > 5:
                        preview += "..."
                else:
                    preview = "Empty file"
                
            self.count_label.configure(text=f"📝 Words: {word_count:,}")
            self.preview_text.configure(text=preview)
            
        except Exception as e:
            self.size_label.configure(text="📊 Size: Error")
            self.count_label.configure(text="📝 Words: Error")
            self.preview_text.configure(text=f"Error reading file: {str(e)}")

    def browse_wordlist(self):
        filename = filedialog.askopenfilename(
            title="Select Wordlist",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if filename:
            self.wordlist_var.set(filename)
    
    def update_progress(self, current, total, attack_type):
        """Update progress bar and status with smoothed metrics"""
        # Guard against zero total
        progress = (current / total * 100) if total > 0 else 0

        now = time.time()
        elapsed_total = now - getattr(self, 'start_time', now)
        
        # Compute speed metrics
        last_count = getattr(self, 'last_progress_count', 0)
        last_time = getattr(self, 'last_progress_time', self.start_time if hasattr(self, 'start_time') else now)
        delta_count = max(0, current - last_count)
        delta_time = max(1e-6, now - last_time)
        
        # Calculate speed with EMA smoothing
        instant_rate = delta_count / delta_time
        if self.ema_rate is None:
            self.ema_rate = instant_rate
        else:
            self.ema_rate = (self.ema_alpha * instant_rate + 
                           (1 - self.ema_alpha) * self.ema_rate)
        
        # Save last progress snapshot
        self.last_progress_count = current
        self.last_progress_time = now
        
        # Calculate and store ETA
        if self.ema_rate > 0 and total > 0:
            remaining_attempts = total - current
            eta_seconds = remaining_attempts / self.ema_rate
            
            if eta_seconds < 60:
                self.eta_text = f"{eta_seconds:.0f}s"
            elif eta_seconds < 3600:
                self.eta_text = f"{eta_seconds/60:.1f}m"
            else:
                self.eta_text = f"{eta_seconds/3600:.1f}h"
        else:
            self.eta_text = "calculating..."
            
        # Put progress update in queue
        self.queue.put(("progress", progress))
        
        # Format detailed status for output
        current_fmt = f"{current:,}"
        total_fmt = f"{total:,}"
        status_lines = [f"Progress: {current_fmt}/{total_fmt} attempts ({progress:.1f}%)"]
        status_lines.append(f"Speed: {self.ema_rate:,.1f} attempts/s")
        if delta_count > 0 and abs(instant_rate - self.ema_rate) > self.ema_rate * 0.5:
            status_lines.append(f"Instant: {instant_rate:,.1f} attempts/s")
        status_lines.append(f"ETA: {self.eta_text}")
        status_lines.append(f"Elapsed: {elapsed_total:.1f}s")

        status = "\n".join(status_lines) + "\n"
        self.queue.put(("output", status))
    
    def start_attack(self, attack_type):
        """Start a password attack"""
        # Input validation
        if not self.password_var.get():
            Messagebox.show_error(
                title="Input Required",
                message="Please enter a password to test",
                parent=self.root
            )
            return
            
        # Save start time for speed calculations
        self.start_time = time.time()
        
        # Reset progress
        self.progress_var.set(0)
        self.output.delete(1.0, tk.END)
        
        # Reset engine stop flag and disable attack buttons during attack
        try:
            self.attack_engine.reset_stop()
        except Exception:
            # Fallback if reset not available
            self.attack_engine.stop_flag = False

        # Disable only the attack buttons and enable Stop
        for btn in (self.dict_btn, self.brute_btn, self.hybrid_btn):
            try:
                btn.configure(state='disabled')
            except Exception:
                pass
        self.stop_btn.configure(state='enabled')
        
        # Start attack in separate thread
        thread = threading.Thread(target=self._run_attack, args=(attack_type,))
        thread.daemon = True
        thread.start()

    def stop_attack(self):
        """Handler for Stop button: signal the engine to stop"""
        try:
            self.attack_engine.stop_attacks()
            self.queue.put(("output", "Stop requested — stopping attack..."))
            # disable stop button to avoid repeated clicks
            self.stop_btn.configure(state='disabled')
        except Exception as e:
            self.queue.put(("error", f"Failed to request stop: {e}"))
    
    def _run_attack(self, attack_type):
        try:
            # Get password hash
            password = self.password_var.get()
            hash_type = self.hash_type_var.get()
            hash_fn = self.hash_simulator.get_hash_function(hash_type)
            target_hash = hash_fn(password)
            
            # Clear output and reset progress
            self.output.delete(1.0, tk.END)
            self.progress_var.set(0)
            
            # Start timer
            self.metrics.start_timer(f"{attack_type}_attack")
            
            # Show initial status
            self.queue.put(("output", f"Starting {attack_type} attack...\n"))
            self.queue.put(("output", f"Target hash type: {hash_type}\n"))
            
            # Calculate total attempts for brute force
            if attack_type == "brute_force":
                charset_len = len(self.config['brute_force']['charset'])
                max_len = self.config['brute_force']['max_length']
                total_attempts = sum(charset_len ** i for i in range(1, max_len + 1))
                self.queue.put(("output", f"Charset size: {charset_len}\n"))
                self.queue.put(("output", f"Max length: {max_len}\n"))
                self.queue.put(("output", f"Total possible combinations: {total_attempts:,}\n\n"))
            
            # Run attack
            if attack_type == "dictionary":
                result = self.attack_engine.dictionary_attack(
                    target_hash, self.wordlist_var.get(), hash_fn=hash_fn,
                    hash_type=hash_type, progress_callback=self.update_progress
                )
            elif attack_type == "brute_force":
                result = self.attack_engine.brute_force_attack(
                    target_hash, hash_fn=hash_fn, hash_type=hash_type,
                    progress_callback=self.update_progress
                )
            else:  # hybrid
                result = self.attack_engine.hybrid_attack(
                    target_hash, self.wordlist_var.get(), hash_fn=hash_fn,
                    hash_type=hash_type, progress_callback=self.update_progress
                )
            
            # Stop timer and record metrics
            metrics = self.metrics.stop_timer(f"{attack_type}_attack")
            self.metrics.add_result(result)
            
            # Show results
            msg = "\n" + "="*50 + "\n"
            msg += "🎯 Attack Results\n"
            msg += "="*50 + "\n\n"
            
            # Status icon and basic results
            if result.success:
                msg += "🔓 SUCCESS: Password was cracked!\n"
                msg += f"🔑 Found password: {result.password}\n"
            else:
                msg += "🛡️ Password resisted the attack\n"
            
            # Performance metrics
            msg += "\n📊 Performance Metrics:\n"
            msg += f"⚡ Total attempts: {result.attempts:,}\n"
            msg += f"⏱️ Time taken: {result.time_taken:.2f} seconds\n"
            
            # Calculate and show speed
            if result.time_taken > 0:
                speed = result.attempts / result.time_taken
                msg += f"🚀 Average speed: {speed:,.0f} attempts/second\n"
            
            # Memory usage
            if metrics and 'memory_change_mb' in metrics:
                msg += f"💾 Memory used: {metrics['memory_change_mb']:.1f} MB\n"
            
            msg += "\n" + "="*50 + "\n"
            
            self.queue.put(("output", msg))
            
            # Re-enable attack buttons
            self.queue.put(("enable_buttons", None))
            
            # Update metrics tab
            self.queue.put(("metrics", self.metrics.calculate_comprehensive_metrics()))
            
        except Exception as e:
            self.queue.put(("error", f"Error: {str(e)}"))
    
    def update_output(self):
        """Process queued updates"""
        try:
            while True:
                msg_type, data = self.queue.get_nowait()

                if msg_type == "progress":
                    # Update progress bar with smooth animation
                    self.progress_var.set(data)
                    
                    # Update speed display
                    if hasattr(self, 'ema_rate') and self.ema_rate is not None:
                        if self.ema_rate >= 1000000:
                            speed_text = f"{self.ema_rate/1000000:.1f}M/s"
                        elif self.ema_rate >= 1000:
                            speed_text = f"{self.ema_rate/1000:.1f}K/s"
                        else:
                            speed_text = f"{self.ema_rate:.0f}/s"
                        self.speed_var.set(speed_text)
                    
                    # Update ETA if available
                    if 'eta_text' in vars(self):
                        self.eta_var.set(self.eta_text)
                    
                elif msg_type == "status":
                    # Update status label
                    try:
                        self.status_var.set(str(data))
                    except Exception:
                        pass
                elif msg_type == "output":
                    self.output.insert(tk.END, str(data) + "\n")
                    self.output.see(tk.END)
                elif msg_type == "metrics":
                    self.metrics_text.delete(1.0, tk.END)
                    for key, value in data.items():
                        if isinstance(value, float):
                            self.metrics_text.insert(tk.END, f"{key}: {value:.2f}\n")
                        else:
                            self.metrics_text.insert(tk.END, f"{key}: {value}\n")
                elif msg_type == "error":
                    Messagebox.show_error(
                        title="Error",
                        message=data,
                        parent=self.root
                    )
                elif msg_type == "enable_buttons":
                    # Re-enable attack buttons when attack completes
                    for btn in (self.dict_btn, self.brute_btn, self.hybrid_btn):
                        try:
                            btn.configure(state='enabled')
                        except Exception:
                            pass
                    try:
                        self.stop_btn.configure(state='disabled')
                    except Exception:
                        pass

                self.queue.task_done()
                
        except queue.Empty:
            pass
        
        # Schedule next update
        self.root.after(100, self.update_output)
    
    def save_report(self):
        """Save a detailed HTML report"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html")],
            title="Save Report"
        )
        
        if filename:
            metrics = self.metrics.calculate_comprehensive_metrics()
            output_text = self.output.get(1.0, tk.END)
            success, error = FileManager.save_html_report(filename, metrics, output_text)
            
            if success:
                Messagebox.show_info(
                    title="Success",
                    message=f"Report saved to {filename}",
                    parent=self.root
                )
            else:
                Messagebox.show_error(
                    title="Save Failed",
                    message=f"Failed to save report: {error}",
                    parent=self.root
                )
            # Report saving handled by FileManager; detailed report generation removed (now centralized)

    def export_results(self):
        """Export results to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Results"
        )
        
        if filename:
            try:
                # Get the metrics data
                metrics_data = self.metrics.calculate_comprehensive_metrics()
                
                # Write to CSV
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Metric', 'Value'])  # Header
                    for key, value in metrics_data.items():
                        writer.writerow([key, value])
                
                Messagebox.show_info(
                    title="Export Success",
                    message=f"Results exported to {filename}",
                    parent=self.root
                )
                
                # Open the file
                os.startfile(filename)
            except Exception as e:
                Messagebox.show_error(
                    title="Export Failed",
                    message=f"Failed to export results: {str(e)}",
                    parent=self.root
                )

if __name__ == "__main__":
    # Create themed root window with dark mode
    root = ttk.Window(
        title="ROSE GUARD",
        themename="darkly",
        resizable=(True, True)
    )
    
    # Set window size
    root.minsize(1000, 800)
    
    # Create and run application
    app = RoseGuardGUI(root)
    root.mainloop()