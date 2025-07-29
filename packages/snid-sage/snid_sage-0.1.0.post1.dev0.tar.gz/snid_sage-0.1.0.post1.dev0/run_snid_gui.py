#!/usr/bin/env python3
"""
SNID SAGE GUI Launcher with Fast Startup
========================================

Launches the SNID SAGE GUI interface with optimized fast startup.
Shows the window immediately with a loading screen while components
load in the background.

Key features:
- Immediate window appearance (1-2 seconds)
- Background loading of heavy components
- Professional loading screen with SNID SAGE branding
- Proper DPI awareness and theme setup
- Comprehensive error handling

Usage:
    python run_snid_gui.py                    # Fast startup mode (default)
    python run_snid_gui.py --verbose          # With startup progress
    python run_snid_gui.py --debug            # Full debug output
    python run_snid_gui.py --quiet            # Minimal output
    python run_snid_gui.py --silent           # Critical errors only
    
Environment Variables:
    SNID_DEBUG=1        # Enable debug mode
    SNID_VERBOSE=1      # Enable verbose mode
    SNID_QUIET=1        # Enable quiet mode
"""

import sys
import os
import argparse
import time
import tkinter as tk
from tkinter import messagebox
import threading
from pathlib import Path
# Note: ttk imported earlier for potential theming; keeping import optional
try:
    from tkinter import ttk
except ImportError:
    ttk = None

# Suppress third-party library output unless in verbose/debug mode
def suppress_third_party_output():
    """Suppress console output from third-party libraries"""
    # Suppress pygame welcome message
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    
    # Suppress other common library output
    import warnings
    warnings.filterwarnings('ignore')

def parse_arguments():
    """Parse command line arguments for the GUI launcher"""
    parser = argparse.ArgumentParser(
        description="SNID SAGE GUI Launcher with Fast Startup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_snid_gui.py                    # Fast startup (default)
    python run_snid_gui.py --verbose          # With loading progress
    python run_snid_gui.py --debug            # Full debug output
    python run_snid_gui.py --quiet            # Minimal output
    
Environment Variables:
    SNID_DEBUG=1        # Enable debug mode
    SNID_VERBOSE=1      # Enable verbose mode
        """
    )
    
    # Import logging configuration to add standard arguments
    try:
        from snid_sage.shared.utils.logging import add_logging_arguments
        add_logging_arguments(parser)
    except ImportError:
        # Fallback to basic arguments if logging system not available
        parser.add_argument('--verbose', '-v', action='store_true',
                          help='Enable verbose output')
        parser.add_argument('--debug', '-d', action='store_true',
                          help='Enable debug output')
        parser.add_argument('--quiet', '-q', action='store_true',
                          help='Quiet mode (errors/warnings only)')
        parser.add_argument('--silent', action='store_true',
                          help='Silent mode (critical errors only)')
    
    return parser.parse_args()

def setup_dpi_awareness():
    """Set up DPI awareness before creating any windows"""
    try:
        import platform
        if platform.system() == 'Windows':
            try:
                import ctypes
                # Try to set DPI awareness
                try:
                    # Windows 10 version 1703 and later
                    ctypes.windll.shcore.SetProcessDpiAwareness(1)
                except:
                    try:
                        # Windows Vista and later fallback
                        ctypes.windll.user32.SetProcessDPIAware()
                    except:
                        pass
            except:
                pass
    except:
        pass

class FastGUILauncher:
    """Fast GUI launcher that prioritizes immediate window appearance"""
    
    def __init__(self, args):
        self.args = args
        self.verbose = args.verbose or args.debug
        self.debug = args.debug
        self.root = None
        self.app = None
        self.logo_image = None
        self.logger = None
        
        # Track loading progress
        self.loading_complete = False
        self.background_loading_done = False
        
        # Progress bar tracking
        self.total_steps = 6  # Number of distinct loading phases we update for
        self.progress_index = 0  # Current completed step count
        
    def log(self, message):
        """Log message if verbose mode enabled"""
        if self.verbose:
            print(f"🚀 {message}")
    
    def load_logo_image(self):
        """Load the SNID SAGE logo for the loading screen"""
        try:
            # Try to load the main logo
            logo_paths = [
                "images/icon.png",
                "images/light.png", 
                "images/dark.png",
                "images/icon_dark.png"
            ]
            
            for logo_path in logo_paths:
                if Path(logo_path).exists():
                    try:
                        from PIL import Image, ImageTk
                        # Load and resize image for loading screen
                        img = Image.open(logo_path)
                        # Resize to a smaller footprint so the splash screen stays compact
                        img = img.resize((160, 160), Image.Resampling.LANCZOS)
                        self.logo_image = ImageTk.PhotoImage(img)
                        self.log(f"Loaded logo from {logo_path}")
                        return
                    except ImportError:
                        # PIL not available, continue without logo
                        self.log("PIL not available, using text logo")
                        return
                    except Exception as e:
                        self.log(f"Error loading logo from {logo_path}: {e}")
                        continue
                        
        except Exception as e:
            self.log(f"Error in logo loading: {e}")
    
    def show_minimal_gui(self):
        """Show minimal GUI window immediately with proper DPI setup"""
        self.log("Creating minimal GUI window...")
        start_time = time.time()
        
        # Create root window but keep it hidden initially
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window initially
        self.root.title("SNID SAGE v1.0.0 - Loading...")
        
        # Configure window properties BEFORE showing
        self.root.configure(bg='#1e1e1e')  # Dark background first
        
        # Set proper window size with DPI awareness
        self.root.geometry("900x600")
        self.root.minsize(800, 550)
        
        # Try to set window icon
        try:
            icon_path = Path("images/icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
            else:
                # Try PNG icon
                png_icon_path = Path("images/icon.png")
                if png_icon_path.exists():
                    from PIL import Image, ImageTk
                    img = Image.open(png_icon_path)
                    img = img.resize((32, 32), Image.Resampling.LANCZOS)
                    icon = ImageTk.PhotoImage(img)
                    self.root.iconphoto(True, icon)
        except Exception as e:
            self.log(f"Could not set window icon: {e}")
        
        # Load logo for display
        self.load_logo_image()
        
        # Create loading screen with better styling
        loading_frame = tk.Frame(self.root, bg='#1e1e1e')
        loading_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Skip logo; instead leave vertical space equivalent
        spacer_logo = tk.Frame(loading_frame, height=60, bg='#1e1e1e')
        spacer_logo.pack()
        
        # Re-introduce writing (title, version, subtitle)
        title_label = tk.Label(
            loading_frame,
            text="SNID-SAGE",
            font=('Segoe UI', 32, 'bold'),
            fg='#ffffff',
            bg='#1e1e1e'
        )
        title_label.pack(pady=(20, 10))

        version_label = tk.Label(
            loading_frame,
            text="v1.0.0",
            font=('Segoe UI', 12),
            fg='#888888',
            bg='#1e1e1e'
        )
        version_label.pack(pady=(0, 5))

        subtitle_label = tk.Label(
            loading_frame,
            text="SuperNova IDentification – Spectral Analysis with Guided Expertise",
            font=('Segoe UI', 14),
            fg='#cccccc',
            bg='#1e1e1e'
        )
        subtitle_label.pack(pady=(0, 40))
        
        # Loading status with modern styling (left-aligned so it stays in place)
        self.status_label = tk.Label(
            loading_frame,
            text="🚀 Initializing...",
            font=('Segoe UI', 11),
            fg='#4CAF50',
            bg='#1e1e1e',
            anchor='center'
        )
        self.status_label.pack(pady=(20, 10))

        # Animated ASCII loading bar (visual feedback similar to original)
        self._bar_length = 30  # number of characters
        self._bar_pos = 0  # Will be controlled via update_progress
        self.progress_bar_label = tk.Label(
            loading_frame,
            text="░" * self._bar_length,
            font=("Consolas", 12),
            fg="#4CAF50",
            bg="#1e1e1e",
        )
        self.progress_bar_label.pack(pady=15)

        # Initialise bar (all empty)
        self.progress_bar_label.config(text="░" * self._bar_length)
        
        # Loading tip
        tip_label = tk.Label(
            loading_frame,
            text="🔬 Preparing spectrum analysis tools...",
            font=('Segoe UI', 9),
            fg='#888888',
            bg='#1e1e1e'
        )
        tip_label.pack(pady=(30, 0))
        
        # Calculate window position BEFORE showing
        self.root.update_idletasks()  # This calculates sizes without showing
        
        # Get screen dimensions and set window size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Use the defined window size (900x600)
        window_width = 900
        window_height = 600
        
        # Calculate center position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Ensure window stays on screen
        x = max(0, min(x, screen_width - window_width))
        y = max(0, min(y, screen_height - window_height))
        
        # Set final position before showing
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # NOW show the window - it will appear in the correct position with correct styling
        self.root.deiconify()  # Show the window
        self.root.update()  # Force update to ensure it's visible
        
        window_time = time.time() - start_time
        self.log(f"Minimal GUI window created in {window_time:.3f}s")
        
        return self.root
    
    def update_progress(self, status, progress_text):
        """Update loading progress"""
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.config(text=status)
        # Advance progress bar based on defined steps
        if not self.loading_complete and hasattr(self, 'progress_bar_label'):
            # Increment step counter but clamp to total_steps
            self.progress_index = min(self.progress_index + 1, self.total_steps)
            filled_len = int(self._bar_length * self.progress_index / self.total_steps)
            filled = "▓" * filled_len
            empty = "░" * (self._bar_length - filled_len)
            self.progress_bar_label.config(text=filled + empty)

        if hasattr(self, 'root') and self.root:
            self.root.update_idletasks()
    
    def load_components_background(self):
        """Load heavy components in background thread"""
        try:
            self.log("Starting background component loading...")
            
            # Configure logging first
            self.update_progress("⚙️ Configuring logging...", "▓▓▓▓░░░░░░ Setting up logging system...")
            try:
                from snid_sage.shared.utils.logging import configure_from_args
                from snid_sage.shared.utils.logging import get_logger
                
                configure_from_args(self.args, gui_mode=True)
                self.logger = get_logger('gui.launcher')
                self.log("Logging configured")
            except ImportError:
                self.log("Logging system not available (using fallback)")
            
            # Load matplotlib
            self.update_progress("📊 Loading matplotlib...", "▓▓▓▓▓▓░░░░ Loading plotting libraries...")
            import matplotlib
            matplotlib.use('TkAgg')  # Set backend early
            self.log("Matplotlib loaded")
            
            # Load numpy
            self.update_progress("🔢 Loading numpy...", "▓▓▓▓▓▓▓░░░ Loading numerical libraries...")
            import numpy as np
            self.log("Numpy loaded")
            
            # Check dependencies
            self.update_progress("🔍 Checking dependencies...", "▓▓▓▓▓▓▓▓░░ Verifying installation...")
            deps_ok = self.check_dependencies_fast()
            if not deps_ok:
                error_msg = "Dependencies check failed"
                suggestion = "Try running: pip install -e . --force-reinstall"
                
                if self.logger:
                    self.logger.error(f"❌ {error_msg}")
                    self.logger.info(f"💡 {suggestion}")
                else:
                    self.log(f"❌ {error_msg}")
                    self.log(f"💡 {suggestion}")
                
                self.root.after(100, lambda: messagebox.showerror("Dependencies Error", 
                    f"{error_msg}\n\n{suggestion}"))
                return
            
            # Load SNID core components
            self.update_progress("🔬 Loading SNID engine...", "▓▓▓▓▓▓▓▓▓░ Loading SNID analysis engine...")
            from snid_sage.snid.snid import run_snid, preprocess_spectrum, run_snid_analysis
            self.log("SNID core loaded")
            
            # Now we can safely create the real GUI
            self.update_progress("🖥️ Initializing interface...", "▓▓▓▓▓▓▓▓▓▓ Creating user interface...")
            
            # Mark loading as complete; fill progress bar fully
            self.loading_complete = True
            if hasattr(self, 'progress_bar_label'):
                self.progress_bar_label.config(text="▓" * self._bar_length)
            
            # Schedule GUI creation on main thread
            self.root.after(100, self.create_real_gui)
            
        except Exception as e:
            # Handle errors gracefully
            error_msg = f"❌ Error loading components: {e}"
            self.log(error_msg)
            self.update_progress(error_msg, "▓▓▓▓▓▓▓▓▓▓ Error occurred!")
            
            # Show error dialog
            self.root.after(100, lambda: messagebox.showerror("Loading Error", 
                f"Error loading SNID components:\n{e}\n\nTry restarting or check installation."))
    
    def check_dependencies_fast(self):
        """Lightweight dependency check without heavy imports"""
        try:
            # Use importlib for faster checking
            import importlib.util
            
            modules_to_check = [
                'tkinter', 'matplotlib', 'numpy', 
                'snid_sage.snid.snid', 'snid_sage.interfaces.gui.sage_gui'
            ]
            
            missing_deps = []
            for module in modules_to_check:
                spec = importlib.util.find_spec(module)
                if spec is None:
                    missing_deps.append(module)
                    if self.logger:
                        self.logger.error(f"{module} not available")
            
            if missing_deps:
                if self.logger:
                    self.logger.error(f"Missing dependencies: {', '.join(missing_deps)}")
                return False
            else:
                if self.logger:
                    self.logger.info("All dependencies available")
                return True
                
        except Exception as e:
            self.log(f"Error checking dependencies: {e}")
            return False
    
    def create_real_gui(self):
        """Create the real GUI after components are loaded"""
        try:
            self.log("Creating real GUI interface...")
            
            # Store current window position and size to maintain it
            current_geometry = self.root.geometry()
            
            # Import and create the real GUI
            from snid_sage.interfaces.gui.sage_gui import ModernSNIDSageGUI
            
            # Clear loading screen
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Important: Reconfigure the root window for the main GUI
            self.root.configure(bg='')  # Reset background
            
            # Set a flag to prevent the GUI from auto-centering (since we already positioned it)
            self.root._fast_launcher_positioned = True
            
            # Create the real application (this might resize/reposition the window)
            self.app = ModernSNIDSageGUI(self.root)
            
            # Update title
            self.root.title("SNID SAGE v1.0.0 - Ready")
            
            # Ensure the window stays in place (prevent jumping)
            self.root.update_idletasks()
            
            self.log("GUI fully loaded and ready!")
            
        except Exception as e:
            self.log(f"Error creating real GUI: {e}")
            if self.logger:
                self.logger.error(f"Error creating real GUI: {e}")
            messagebox.showerror("GUI Error", f"Failed to create GUI:\n{e}")
    
    def run(self):
        """Run the fast GUI launcher"""
        start_time = time.time()
        
        # Step 1: Set up DPI awareness FIRST
        setup_dpi_awareness()
        self.log("DPI awareness configured")
        
        # Step 2: Show minimal GUI immediately
        root = self.show_minimal_gui()
        
        # Step 3: Start background loading
        loading_thread = threading.Thread(target=self.load_components_background, daemon=True)
        loading_thread.start()
        
        total_startup_time = time.time() - start_time
        self.log(f"Total startup time to window appearance: {total_startup_time:.3f}s")
        
        # Start main loop
        try:
            root.mainloop()
        except KeyboardInterrupt:
            self.log("Keyboard interrupt received")
        except Exception as e:
            self.log(f"GUI error: {e}")
        
        return 0

def main():
    """Main function for SNID SAGE GUI launcher with fast startup"""
    
    # Suppress third-party library output FIRST, before any imports
    suppress_third_party_output()
    
    # Parse command line arguments first
    args = parse_arguments()
    
    # Create and run the fast launcher
    launcher = FastGUILauncher(args)
    return launcher.run()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 