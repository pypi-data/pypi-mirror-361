#!/usr/bin/env python3
"""
Linux Icon Setup Script for SNID SAGE
=====================================

This script sets up proper icon handling on Linux including:
- Creating .desktop files with custom icons
- Installing icons to system icon themes
- Setting up proper file associations
- Registering with desktop environments

Usage:
    python scripts/setup_linux_icons.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse

def install_system_icons(project_root: Path, icon_sizes=[16, 22, 24, 32, 48, 64, 128, 256, 512]):
    """Install icons to system icon theme directories"""
    try:
        icon_theme_dirs = [
            Path.home() / ".local/share/icons/hicolor",
            Path.home() / ".icons/hicolor"
        ]
        
        # Try to find source icons
        images_dir = project_root / "images"
        source_icon = images_dir / "icon.png"
        
        if not source_icon.exists():
            print(f"❌ Source icon not found: {source_icon}")
            return False
        
        success_count = 0
        
        for theme_dir in icon_theme_dirs:
            if theme_dir.exists() or theme_dir.parent.exists():
                theme_dir.mkdir(parents=True, exist_ok=True)
                
                for size in icon_sizes:
                    size_dir = theme_dir / f"{size}x{size}" / "apps"
                    size_dir.mkdir(parents=True, exist_ok=True)
                    
                    target_icon = size_dir / "snid-sage.png"
                    
                    # Create resized icon for this size
                    if create_resized_icon(source_icon, target_icon, size):
                        success_count += 1
                        print(f"✅ Installed {size}x{size} icon to {target_icon}")
                
                # Update icon cache
                try:
                    subprocess.run(["gtk-update-icon-cache", str(theme_dir)], 
                                 capture_output=True, check=False)
                except FileNotFoundError:
                    pass  # gtk-update-icon-cache not available
        
        print(f"✅ Installed {success_count} icon variations")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error installing system icons: {e}")
        return False

def create_resized_icon(source_path: Path, target_path: Path, size: int):
    """Create a resized version of the icon"""
    try:
        try:
            from PIL import Image
            
            with Image.open(source_path) as img:
                resized = img.resize((size, size), Image.LANCZOS)
                resized.save(target_path, format='PNG')
            return True
            
        except ImportError:
            # Fallback to ImageMagick convert
            try:
                subprocess.run([
                    "convert", str(source_path), 
                    "-resize", f"{size}x{size}", 
                    str(target_path)
                ], check=True, capture_output=True)
                return True
            except (FileNotFoundError, subprocess.CalledProcessError):
                # Just copy the original if no resize tools available
                shutil.copy2(source_path, target_path)
                return True
                
    except Exception as e:
        print(f"⚠️ Error creating {size}x{size} icon: {e}")
        return False

def create_desktop_entry(project_root: Path):
    """Create .desktop file for desktop environments"""
    try:
        desktop_dir = Path.home() / ".local/share/applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = desktop_dir / "snid-sage.desktop"
        
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=SNID SAGE
GenericName=SuperNova Spectrum Analyzer
Comment=SuperNova IDentification with Spectrum Analysis and Guided Enhancement
Exec="{sys.executable}" "{project_root / 'run_snid_gui.py'}" %F
Icon=snid-sage
Terminal=false
StartupNotify=true
Categories=Education;Science;Astronomy;
MimeType=application/fits;text/plain;application/x-fits;
Keywords=astronomy;supernova;spectrum;analysis;snid;
StartupWMClass=SNID SAGE
"""
        
        with open(desktop_file, 'w') as f:
            f.write(desktop_content)
        
        # Make executable
        os.chmod(desktop_file, 0o755)
        
        print(f"✅ Created desktop entry: {desktop_file}")
        
        # Update desktop database
        try:
            subprocess.run(["update-desktop-database", str(desktop_dir)], 
                         capture_output=True, check=False)
        except FileNotFoundError:
            pass  # update-desktop-database not available
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating desktop entry: {e}")
        return False

def create_desktop_shortcut(project_root: Path):
    """Create desktop shortcut"""
    try:
        desktop = Path.home() / "Desktop"
        shortcut_file = desktop / "SNID SAGE.desktop"
        
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=SNID SAGE
GenericName=SuperNova Spectrum Analyzer
Comment=SuperNova IDentification with Spectrum Analysis and Guided Enhancement
Exec="{sys.executable}" "{project_root / 'run_snid_gui.py'}" %F
Icon=snid-sage
Terminal=false
StartupNotify=true
Categories=Education;Science;Astronomy;
"""
        
        with open(shortcut_file, 'w') as f:
            f.write(desktop_content)
        
        # Make executable
        os.chmod(shortcut_file, 0o755)
        
        print(f"✅ Created desktop shortcut: {shortcut_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating desktop shortcut: {e}")
        return False

def setup_mime_types(project_root: Path):
    """Set up MIME type associations for spectrum files"""
    try:
        mime_dir = Path.home() / ".local/share/mime/packages"
        mime_dir.mkdir(parents=True, exist_ok=True)
        
        mime_file = mime_dir / "snid-sage.xml"
        
        mime_content = """<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
    <mime-type type="application/x-fits-spectrum">
        <comment>FITS Spectrum File</comment>
        <glob pattern="*.fits"/>
        <glob pattern="*.fit"/>
        <icon name="snid-sage"/>
    </mime-type>
    <mime-type type="application/x-ascii-spectrum">
        <comment>ASCII Spectrum File</comment>
        <glob pattern="*.dat"/>
        <glob pattern="*.ascii"/>
        <glob pattern="*.spec"/>
        <icon name="snid-sage"/>
    </mime-type>
</mime-info>
"""
        
        with open(mime_file, 'w') as f:
            f.write(mime_content)
        
        print(f"✅ Created MIME types: {mime_file}")
        
        # Update MIME database
        try:
            subprocess.run(["update-mime-database", str(Path.home() / ".local/share/mime")], 
                         capture_output=True, check=False)
        except FileNotFoundError:
            pass  # update-mime-database not available
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up MIME types: {e}")
        return False

def setup_file_associations():
    """Set up file associations using xdg-mime"""
    try:
        associations = [
            ("application/x-fits-spectrum", "snid-sage.desktop"),
            ("application/x-ascii-spectrum", "snid-sage.desktop"),
            ("text/plain", "snid-sage.desktop"),  # For .dat, .txt files
        ]
        
        for mime_type, desktop_file in associations:
            try:
                subprocess.run([
                    "xdg-mime", "default", desktop_file, mime_type
                ], capture_output=True, check=False)
                print(f"✅ Associated {mime_type} with {desktop_file}")
            except FileNotFoundError:
                print("⚠️ xdg-mime not available, skipping associations")
                break
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up file associations: {e}")
        return False

def create_launcher_script(project_root: Path):
    """Create a launcher script for easy execution"""
    try:
        bin_dir = Path.home() / ".local/bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        
        launcher_script = bin_dir / "snid-sage"
        
        script_content = f"""#!/bin/bash
# SNID SAGE Linux Launcher
# Sets up environment and launches SNID SAGE

cd "{project_root}"
exec "{sys.executable}" run_snid_gui.py "$@"
"""
        
        with open(launcher_script, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(launcher_script, 0o755)
        
        print(f"✅ Created launcher script: {launcher_script}")
        
        # Check if ~/.local/bin is in PATH
        path_env = os.environ.get('PATH', '')
        if str(bin_dir) not in path_env:
            print(f"💡 Add {bin_dir} to your PATH to use 'snid-sage' command")
            print(f"   Add this to your ~/.bashrc or ~/.zshrc:")
            print(f"   export PATH=\"{bin_dir}:$PATH\"")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating launcher script: {e}")
        return False

def detect_desktop_environment():
    """Detect the current desktop environment"""
    desktop_env = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    
    if not desktop_env:
        desktop_env = os.environ.get('DESKTOP_SESSION', '').lower()
    
    if 'gnome' in desktop_env:
        return 'GNOME'
    elif 'kde' in desktop_env or 'plasma' in desktop_env:
        return 'KDE'
    elif 'xfce' in desktop_env:
        return 'XFCE'
    elif 'mate' in desktop_env:
        return 'MATE'
    elif 'cinnamon' in desktop_env:
        return 'Cinnamon'
    else:
        return 'Unknown'

def main():
    """Main function to set up Linux icons and desktop integration"""
    parser = argparse.ArgumentParser(description="Set up SNID SAGE icons and desktop integration on Linux")
    parser.add_argument("--icons", action="store_true", help="Install system icons")
    parser.add_argument("--desktop-entry", action="store_true", help="Create .desktop file")
    parser.add_argument("--desktop-shortcut", action="store_true", help="Create desktop shortcut")
    parser.add_argument("--mime-types", action="store_true", help="Set up MIME types")
    parser.add_argument("--file-associations", action="store_true", help="Set up file associations")
    parser.add_argument("--launcher", action="store_true", help="Create launcher script")
    parser.add_argument("--all", action="store_true", help="Perform all setup operations")
    
    args = parser.parse_args()
    
    # If no specific options, do basic setup
    if not any([args.icons, args.desktop_entry, args.desktop_shortcut, 
                args.mime_types, args.file_associations, args.launcher, args.all]):
        args.icons = True
        args.desktop_entry = True
        args.desktop_shortcut = True
        args.launcher = True
    
    if args.all:
        args.icons = True
        args.desktop_entry = True
        args.desktop_shortcut = True
        args.mime_types = True
        args.file_associations = True
        args.launcher = True
    
    print("🐧 SNID SAGE Linux Icon Setup")
    print("=" * 30)
    
    # Check if we're on Linux
    if sys.platform not in ["linux", "linux2"]:
        print("❌ This script is designed for Linux only")
        return 1
    
    desktop_env = detect_desktop_environment()
    print(f"🖥️ Detected desktop environment: {desktop_env}")
    
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print(f"📂 Project root: {project_root}")
    print()
    
    success_count = 0
    total_count = 0
    
    if args.icons:
        total_count += 1
        if install_system_icons(project_root):
            success_count += 1
    
    if args.desktop_entry:
        total_count += 1
        if create_desktop_entry(project_root):
            success_count += 1
    
    if args.desktop_shortcut:
        total_count += 1
        if create_desktop_shortcut(project_root):
            success_count += 1
    
    if args.mime_types:
        total_count += 1
        if setup_mime_types(project_root):
            success_count += 1
    
    if args.file_associations:
        total_count += 1
        if setup_file_associations():
            success_count += 1
    
    if args.launcher:
        total_count += 1
        if create_launcher_script(project_root):
            success_count += 1
    
    print()
    print(f"📊 Results: {success_count}/{total_count} operations completed successfully")
    
    if success_count == total_count:
        print("✅ Linux icon setup completed successfully!")
        print()
        print("💡 Tips:")
        print("   - SNID SAGE should now appear in your application menu")
        print("   - Look for it under Education > Science or just search 'SNID'")
        print("   - Desktop shortcut should work by double-clicking")
        print("   - Right-click spectrum files to 'Open with SNID SAGE'")
        print("   - Use 'snid-sage' command if ~/.local/bin is in your PATH")
    else:
        print("⚠️ Some operations failed. Check error messages above.")
        print()
        print("💡 Troubleshooting:")
        print("   - Make sure you're running on Linux with a desktop environment")
        print("   - Install PIL/Pillow for better icon scaling: pip install Pillow")
        print("   - Some features require xdg-utils package")
    
    return 0 if success_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main()) 