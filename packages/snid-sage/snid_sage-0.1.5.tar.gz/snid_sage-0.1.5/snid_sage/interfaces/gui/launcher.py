"""
SNID SAGE GUI Launcher Entry Point
==================================

Entry point for the SNID SAGE GUI when installed via pip.
This ensures the loading screen is shown regardless of how the application is launched.

This module serves as the bridge between pip entry points and the FastGUILauncher
to ensure consistent behavior between development and production installations.
"""

import sys
import os
import argparse
from pathlib import Path

# Cache successful import strategy to avoid repeating slow searches
_cached_import_strategy = None
_cached_import_path = None

def create_launcher_args():
    """Create default arguments for the FastGUILauncher"""
    # Create a minimal argparse.Namespace object with default values
    # that matches what parse_arguments() in run_snid_gui.py would return
    
    args = argparse.Namespace()
    args.verbose = False
    args.debug = False
    args.quiet = False
    args.silent = False
    
    # Check environment variables for defaults
    if os.environ.get('SNID_DEBUG', '').lower() in ('1', 'true', 'yes'):
        args.debug = True
        args.verbose = True
    elif os.environ.get('SNID_VERBOSE', '').lower() in ('1', 'true', 'yes'):
        args.verbose = True
    elif os.environ.get('SNID_QUIET', '').lower() in ('1', 'true', 'yes'):
        args.quiet = True
    
    return args

def _try_fast_import():
    """Try the most common import strategies first, using cache if available"""
    global _cached_import_strategy, _cached_import_path
    
    # If we have a cached successful strategy, try it first
    if _cached_import_strategy and _cached_import_path:
        try:
            if _cached_import_path not in sys.path:
                sys.path.insert(0, _cached_import_path)
            from run_snid_gui import FastGUILauncher, suppress_third_party_output
            return FastGUILauncher, suppress_third_party_output
        except ImportError:
            # Cache is stale, clear it
            _cached_import_strategy = None
            _cached_import_path = None
    
    # Strategy 1: Try from project root (development install) - fastest for dev
    try:
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent.parent
        project_root_str = str(project_root)
        
        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)
        
        from run_snid_gui import FastGUILauncher, suppress_third_party_output
        
        # Cache successful strategy
        _cached_import_strategy = "project_root"
        _cached_import_path = project_root_str
        
        return FastGUILauncher, suppress_third_party_output
        
    except ImportError:
        # Strategy 2: Try from installed package directory - fastest for pip install
        try:
            import snid_sage
            package_dir = Path(snid_sage.__file__).parent.parent
            run_gui_file = package_dir / "run_snid_gui.py"
            
            if run_gui_file.exists():
                package_dir_str = str(package_dir)
                if package_dir_str not in sys.path:
                    sys.path.insert(0, package_dir_str)
                from run_snid_gui import FastGUILauncher, suppress_third_party_output
                
                # Cache successful strategy
                _cached_import_strategy = "package_dir"
                _cached_import_path = package_dir_str
                
                return FastGUILauncher, suppress_third_party_output
            else:
                raise ImportError("run_snid_gui.py not found in package directory")
                
        except ImportError:
            # Only try expensive site-packages search as last resort
            return _try_site_packages_import()

def _try_site_packages_import():
    """Try the expensive site-packages search - only as last resort"""
    global _cached_import_strategy, _cached_import_path
    
    try:
        import site
        # Try common site-packages locations first
        for site_dir in site.getsitepackages():
            site_path = Path(site_dir)
            # Check most likely locations first
            for possible_path in [
                site_path / "run_snid_gui.py",  # Most likely
                site_path / "snid_sage" / "run_snid_gui.py",
            ]:
                if possible_path.exists():
                    path_str = str(possible_path.parent)
                    if path_str not in sys.path:
                        sys.path.insert(0, path_str)
                    from run_snid_gui import FastGUILauncher, suppress_third_party_output
                    
                    # Cache successful strategy
                    _cached_import_strategy = "site_packages"
                    _cached_import_path = path_str
                    
                    return FastGUILauncher, suppress_third_party_output
        
        # If we get here, none of the common paths worked
        raise ImportError("run_snid_gui.py not found in site-packages")
        
    except ImportError:
        raise ImportError("FastGUILauncher not found in any location")

def main():
    """
    Main entry point for snid-sage and snid-gui commands
    
    This function ensures that the FastGUILauncher is used regardless of
    how the application is installed or launched.
    """
    try:
        # Try to import the FastGUILauncher with optimized fallback strategies
        try:
            FastGUILauncher, suppress_third_party_output = _try_fast_import()
                        
        except ImportError:
            # Final fallback - use sage_gui directly (no loading screen)
            print("⚠️ FastGUILauncher not available, using direct GUI launch")
            from snid_sage.interfaces.gui.sage_gui import main as sage_main
            return sage_main()
        
        # Suppress third-party output first
        suppress_third_party_output()
        
        # Create launcher arguments
        args = create_launcher_args()
        
        # Create and run the fast launcher
        launcher = FastGUILauncher(args)
        return launcher.run()
        
    except Exception as e:
        print(f"❌ Error launching SNID SAGE GUI: {e}")
        
        # Try fallback to direct GUI launch
        try:
            print("🔄 Attempting fallback launch...")
            from snid_sage.interfaces.gui.sage_gui import main as sage_main
            return sage_main()
        except Exception as fallback_error:
            print(f"❌ Fallback launch also failed: {fallback_error}")
            print("💡 Try running: pip install --upgrade snid-sage")
            return 1

def main_with_args():
    """
    Alternative entry point that accepts command line arguments
    Similar to main() but parses command line arguments first
    """
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="SNID SAGE GUI")
        parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
        parser.add_argument("--debug", "-d", action="store_true", help="Debug output")
        parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode")
        parser.add_argument("--silent", "-s", action="store_true", help="Silent mode")
        
        args = parser.parse_args()
        
        # Import and use FastGUILauncher with parsed args
        try:
            # Get the project root directory
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent.parent
            
            # Add project root to Python path if not already there
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            from run_snid_gui import FastGUILauncher, suppress_third_party_output
            
            # Suppress third-party output first
            suppress_third_party_output()
            
            # Create and run the fast launcher with parsed arguments
            launcher = FastGUILauncher(args)
            return launcher.run()
            
        except ImportError:
            # Fallback to direct GUI launch
            from snid_sage.interfaces.gui.sage_gui import main as sage_main
            return sage_main(args)
            
    except Exception as e:
        print(f"❌ Error launching SNID SAGE GUI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 