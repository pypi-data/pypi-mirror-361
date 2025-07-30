#!/usr/bin/env python3
"""
Windows Icon Setup Script for SNID SAGE
=======================================

This script sets up proper icon associations and shortcuts on Windows
to ensure the custom SNID SAGE icon is used instead of the default Python icon.

Features:
- Creates desktop shortcut with custom icon
- Sets up Start Menu entry with custom icon
- Configures file associations if needed
- Updates registry entries for icon display

Usage:
    python scripts/setup_windows_icons.py
"""

import os
import sys
import winreg
import subprocess
from pathlib import Path
import argparse

def create_desktop_shortcut(project_root: Path, icon_path: Path, target_script: Path):
    """Create desktop shortcut with custom icon"""
    try:
        import win32com.client
        
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "SNID SAGE.lnk"
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        
        # Set target to Python executable with the GUI script
        python_exe = sys.executable
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{target_script}"'
        shortcut.WorkingDirectory = str(project_root)
        shortcut.IconLocation = str(icon_path)
        shortcut.Description = "SNID SAGE - SuperNova IDentification with Spectrum Analysis and Guided Enhancement"
        
        shortcut.save()
        print(f"✅ Created desktop shortcut: {shortcut_path}")
        return True
        
    except ImportError:
        print("⚠️ pywin32 not available. Install with: pip install pywin32")
        return False
    except Exception as e:
        print(f"❌ Error creating desktop shortcut: {e}")
        return False

def create_start_menu_shortcut(project_root: Path, icon_path: Path, target_script: Path):
    """Create Start Menu shortcut with custom icon"""
    try:
        import win32com.client
        
        start_menu = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        snid_folder = start_menu / "SNID SAGE"
        snid_folder.mkdir(exist_ok=True)
        
        shortcut_path = snid_folder / "SNID SAGE.lnk"
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        
        # Set target to Python executable with the GUI script
        python_exe = sys.executable
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{target_script}"'
        shortcut.WorkingDirectory = str(project_root)
        shortcut.IconLocation = str(icon_path)
        shortcut.Description = "SNID SAGE - SuperNova IDentification with Spectrum Analysis and Guided Enhancement"
        
        shortcut.save()
        print(f"✅ Created Start Menu shortcut: {shortcut_path}")
        return True
        
    except ImportError:
        print("⚠️ pywin32 not available. Install with: pip install pywin32")
        return False
    except Exception as e:
        print(f"❌ Error creating Start Menu shortcut: {e}")
        return False

def register_application_icon(project_root: Path, icon_path: Path):
    """Register application with Windows for proper icon display"""
    try:
        app_name = "SNID_SAGE"
        app_path = project_root / "run_snid_gui.py"
        
        # Register application in Windows registry
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\Applications\\{app_name}.exe") as key:
            winreg.SetValueEx(key, "FriendlyAppName", 0, winreg.REG_SZ, "SNID SAGE")
            
        # Set default icon
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\Applications\\{app_name}.exe\\DefaultIcon") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f"{icon_path},0")
            
        print(f"✅ Registered application icon in Windows registry")
        return True
        
    except Exception as e:
        print(f"❌ Error registering application icon: {e}")
        return False

def update_console_scripts_with_icon(project_root: Path, icon_path: Path):
    """Update entry point scripts to use custom icon"""
    try:
        scripts_dir = project_root / "scripts" / "entry_points" / "bin"
        
        if not scripts_dir.exists():
            print(f"⚠️ Entry points directory not found: {scripts_dir}")
            return False
        
        # For each entry point script, we need to ensure they use the custom icon
        entry_points = ["snid-gui", "snid-sage"]
        
        for entry_point in entry_points:
            script_path = scripts_dir / entry_point
            if script_path.exists():
                # Read current script
                with open(script_path, 'r') as f:
                    content = f.read()
                
                # Add icon setup if not already present
                if "iconbitmap" not in content and "set_window_icon" not in content:
                    icon_setup = f'''
# Set application icon for Windows
import sys
if sys.platform == "win32":
    try:
        import tkinter as tk
        # This will be used when the main window is created
        _SNID_ICON_PATH = r"{icon_path}"
    except ImportError:
        pass
'''
                    # Insert after shebang and before main imports
                    lines = content.split('\n')
                    insert_pos = 1 if lines[0].startswith('#!') else 0
                    lines.insert(insert_pos, icon_setup)
                    
                    with open(script_path, 'w') as f:
                        f.write('\n'.join(lines))
                    
                    print(f"✅ Updated entry point script: {script_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating entry point scripts: {e}")
        return False

def create_batch_launcher(project_root: Path, icon_path: Path):
    """Create a Windows batch file launcher with icon"""
    try:
        batch_path = project_root / "SNID_SAGE.bat"
        
        batch_content = f'''@echo off
REM SNID SAGE Windows Launcher
REM Sets up environment and launches with custom icon

cd /d "{project_root}"

REM Set window title
title SNID SAGE - SuperNova IDentification

REM Launch with Python
"{sys.executable}" run_snid_gui.py %*
'''
        
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        print(f"✅ Created batch launcher: {batch_path}")
        
        # Create a shortcut to this batch file with the icon
        try:
            import win32com.client
            
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "SNID SAGE (Batch).lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            
            shortcut.Targetpath = str(batch_path)
            shortcut.WorkingDirectory = str(project_root)
            shortcut.IconLocation = str(icon_path)
            shortcut.Description = "SNID SAGE - SuperNova IDentification (Batch Launcher)"
            
            shortcut.save()
            print(f"✅ Created batch shortcut: {shortcut_path}")
            
        except Exception as e:
            print(f"⚠️ Could not create batch shortcut: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating batch launcher: {e}")
        return False

def setup_windows_file_associations(project_root: Path, icon_path: Path):
    """Set up file associations for spectrum files with SNID SAGE icon"""
    try:
        # Common spectrum file extensions
        extensions = ['.fits', '.dat', '.txt', '.ascii', '.spec']
        
        for ext in extensions:
            try:
                # Create ProgID for SNID SAGE
                prog_id = f"SNID_SAGE{ext.replace('.', '_')}"
                
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{prog_id}") as key:
                    winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f"SNID SAGE Spectrum File ({ext})")
                    
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{prog_id}\\DefaultIcon") as key:
                    winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f"{icon_path},0")
                    
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{prog_id}\\shell\\open\\command") as key:
                    cmd = f'"{sys.executable}" "{project_root / "run_snid_gui.py"}" "%1"'
                    winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)
                
                # Associate extension with ProgID
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{ext}\\OpenWithProgids") as key:
                    winreg.SetValueEx(key, prog_id, 0, winreg.REG_SZ, "")
                
                print(f"✅ Associated {ext} files with SNID SAGE")
                
            except Exception as e:
                print(f"⚠️ Could not associate {ext}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up file associations: {e}")
        return False

def main():
    """Main function to set up Windows icons and shortcuts"""
    parser = argparse.ArgumentParser(description="Set up SNID SAGE icons and shortcuts on Windows")
    parser.add_argument("--desktop", action="store_true", help="Create desktop shortcut")
    parser.add_argument("--start-menu", action="store_true", help="Create Start Menu shortcut")
    parser.add_argument("--registry", action="store_true", help="Register application in Windows registry")
    parser.add_argument("--file-associations", action="store_true", help="Set up file associations")
    parser.add_argument("--batch", action="store_true", help="Create batch launcher")
    parser.add_argument("--all", action="store_true", help="Perform all setup operations")
    
    args = parser.parse_args()
    
    # If no specific options, do basic setup
    if not any([args.desktop, args.start_menu, args.registry, args.file_associations, args.batch, args.all]):
        args.desktop = True
        args.start_menu = True
        args.registry = True
    
    if args.all:
        args.desktop = True
        args.start_menu = True
        args.registry = True
        args.file_associations = True
        args.batch = True
    
    print("🪟 SNID SAGE Windows Icon Setup")
    print("=" * 35)
    
    # Find project root and icon
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    icon_path = project_root / "images" / "icon.ico"
    target_script = project_root / "run_snid_gui.py"
    
    if not icon_path.exists():
        print(f"❌ Icon file not found: {icon_path}")
        print("   Run: python scripts/generate_platform_icons.py")
        return 1
    
    if not target_script.exists():
        print(f"❌ GUI script not found: {target_script}")
        return 1
    
    print(f"📂 Project root: {project_root}")
    print(f"🎨 Icon file: {icon_path}")
    print(f"🎯 Target script: {target_script}")
    print()
    
    success_count = 0
    total_count = 0
    
    if args.desktop:
        total_count += 1
        if create_desktop_shortcut(project_root, icon_path, target_script):
            success_count += 1
    
    if args.start_menu:
        total_count += 1
        if create_start_menu_shortcut(project_root, icon_path, target_script):
            success_count += 1
    
    if args.registry:
        total_count += 1
        if register_application_icon(project_root, icon_path):
            success_count += 1
    
    if args.file_associations:
        total_count += 1
        if setup_windows_file_associations(project_root, icon_path):
            success_count += 1
    
    if args.batch:
        total_count += 1
        if create_batch_launcher(project_root, icon_path):
            success_count += 1
    
    print()
    print(f"📊 Results: {success_count}/{total_count} operations completed successfully")
    
    if success_count == total_count:
        print("✅ Windows icon setup completed successfully!")
        print()
        print("💡 Tips:")
        print("   - Use the desktop or Start Menu shortcuts to launch SNID SAGE")
        print("   - The custom icon should now appear in the taskbar and window title")
        print("   - For file associations, right-click spectrum files and choose 'Open with'")
    else:
        print("⚠️ Some operations failed. Check error messages above.")
        print()
        print("💡 Troubleshooting:")
        print("   - Install pywin32: pip install pywin32")
        print("   - Run as administrator for better registry access")
        print("   - Check that icon files exist")
    
    return 0 if success_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main()) 