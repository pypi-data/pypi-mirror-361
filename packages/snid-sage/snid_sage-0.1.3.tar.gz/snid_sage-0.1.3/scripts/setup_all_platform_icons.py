#!/usr/bin/env python3
"""
Cross-Platform Icon Setup Script for SNID SAGE
==============================================

This script automatically detects the operating system and runs the appropriate
icon setup procedures to ensure the custom SNID SAGE icon is used everywhere.

Features:
- Automatically detects Windows, macOS, or Linux
- Generates missing platform-specific icon files
- Sets up proper system integration for each platform
- Creates shortcuts, desktop entries, and file associations
- Ensures the icon appears in taskbars, docks, and application launchers

Usage:
    python scripts/setup_all_platform_icons.py [options]
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
import argparse

def detect_platform():
    """Detect the current platform"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"

def check_dependencies():
    """Check for required dependencies based on platform"""
    platform_name = detect_platform()
    missing_deps = []
    
    if platform_name == "windows":
        try:
            import win32com.client
        except ImportError:
            missing_deps.append("pywin32 (install with: pip install pywin32)")
    
    # PIL is useful for all platforms for icon resizing
    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("Pillow (install with: pip install Pillow)")
    
    return missing_deps

def generate_platform_icons(project_root: Path):
    """Generate platform-specific icon files"""
    print("🎨 Generating platform-specific icons...")
    
    try:
        script_path = project_root / "scripts" / "generate_platform_icons.py"
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ Platform icons generated successfully")
            return True
        else:
            print(f"❌ Icon generation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating icons: {e}")
        return False

def setup_windows_icons(project_root: Path, options):
    """Set up Windows-specific icons and shortcuts"""
    print("\n🪟 Setting up Windows icons...")
    
    try:
        script_path = project_root / "scripts" / "setup_windows_icons.py"
        
        # Build command with options
        cmd = [sys.executable, str(script_path)]
        if options.get('all', False):
            cmd.append("--all")
        else:
            if options.get('desktop', True):
                cmd.append("--desktop")
            if options.get('start_menu', True):
                cmd.append("--start-menu")
            if options.get('registry', True):
                cmd.append("--registry")
        
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error setting up Windows icons: {e}")
        return False

def setup_macos_icons(project_root: Path, options):
    """Set up macOS-specific icons and app bundle"""
    print("\n🍎 Setting up macOS icons...")
    
    try:
        script_path = project_root / "scripts" / "setup_macos_icons.py"
        
        # Build command with options
        cmd = [sys.executable, str(script_path)]
        if options.get('all', False):
            cmd.append("--all")
        else:
            if options.get('convert_icons', True):
                cmd.append("--convert-icons")
            if options.get('app_bundle', True):
                cmd.append("--app-bundle")
            if options.get('desktop_alias', True):
                cmd.append("--desktop-alias")
        
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error setting up macOS icons: {e}")
        return False

def setup_linux_icons(project_root: Path, options):
    """Set up Linux-specific icons and desktop integration"""
    print("\n🐧 Setting up Linux icons...")
    
    try:
        script_path = project_root / "scripts" / "setup_linux_icons.py"
        
        # Build command with options
        cmd = [sys.executable, str(script_path)]
        if options.get('all', False):
            cmd.append("--all")
        else:
            if options.get('icons', True):
                cmd.append("--icons")
            if options.get('desktop_entry', True):
                cmd.append("--desktop-entry")
            if options.get('desktop_shortcut', True):
                cmd.append("--desktop-shortcut")
            if options.get('launcher', True):
                cmd.append("--launcher")
        
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error setting up Linux icons: {e}")
        return False

def test_gui_icon(project_root: Path):
    """Test that the GUI properly loads the icon"""
    print("\n🧪 Testing GUI icon loading...")
    
    try:
        # Test the cross-platform window manager icon loading
        test_script = f'''
import sys
sys.path.insert(0, r"{project_root}")

try:
    import tkinter as tk
    from interfaces.gui.utils.cross_platform_window import CrossPlatformWindowManager
    
    # Create a test window
    root = tk.Tk()
    root.title("SNID SAGE Icon Test")
    root.geometry("300x200")
    
    # Try to set the icon
    success = CrossPlatformWindowManager.set_window_icon(root, "icon")
    
    if success:
        print("✅ Icon loaded successfully in GUI")
        
        # Show a test label
        label = tk.Label(root, text="SNID SAGE Icon Test\\n\\nIcon should appear in:\\n- Window title bar\\n- Taskbar/Dock\\n- Alt+Tab switcher", 
                        justify=tk.CENTER, pady=20)
        label.pack()
        
        # Auto-close after 3 seconds
        root.after(3000, root.quit)
        root.mainloop()
        
        print("✅ GUI icon test completed")
    else:
        print("❌ Failed to load icon in GUI")
        
except Exception as e:
    print(f"❌ GUI icon test failed: {{e}}")
    import traceback
    traceback.print_exc()
'''
        
        result = subprocess.run([sys.executable, "-c", test_script], 
                              capture_output=True, text=True, cwd=project_root)
        
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ Test warnings: {result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error testing GUI icon: {e}")
        return False

def verify_icon_files(project_root: Path):
    """Verify that all required icon files exist"""
    print("\n🔍 Verifying icon files...")
    
    images_dir = project_root / "images"
    
    required_files = {
        "windows": ["icon.ico", "icon_dark.ico"],
        "macos": ["icon.icns", "icon_dark.icns", "icon.iconset", "icon_dark.iconset"],
        "linux": ["icon.png", "icon_dark.png"],
        "all": ["light.png", "dark.png"]
    }
    
    platform_name = detect_platform()
    
    missing_files = []
    
    # Check platform-specific files
    if platform_name in required_files:
        for filename in required_files[platform_name]:
            file_path = images_dir / filename
            if not file_path.exists():
                missing_files.append(filename)
            else:
                print(f"✅ Found: {filename}")
    
    # Check universal files
    for filename in required_files["all"]:
        file_path = images_dir / filename
        if not file_path.exists():
            missing_files.append(filename)
        else:
            print(f"✅ Found: {filename}")
    
    if missing_files:
        print(f"❌ Missing icon files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required icon files present")
        return True

def main():
    """Main function for cross-platform icon setup"""
    parser = argparse.ArgumentParser(description="Set up SNID SAGE icons across all platforms")
    parser.add_argument("--generate-only", action="store_true", help="Only generate icon files, don't set up system integration")
    parser.add_argument("--setup-only", action="store_true", help="Only set up system integration, skip icon generation")
    parser.add_argument("--test-gui", action="store_true", help="Test GUI icon loading")
    parser.add_argument("--verify-only", action="store_true", help="Only verify icon files exist")
    parser.add_argument("--all", action="store_true", help="Perform all setup operations")
    parser.add_argument("--skip-dependencies", action="store_true", help="Skip dependency checks")
    
    args = parser.parse_args()
    
    print("🌍 SNID SAGE Cross-Platform Icon Setup")
    print("=" * 40)
    
    # Detect platform
    platform_name = detect_platform()
    print(f"🖥️ Detected platform: {platform_name.title()}")
    
    if platform_name == "unknown":
        print("❌ Unsupported platform")
        return 1
    
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    print(f"📂 Project root: {project_root}")
    
    # Check dependencies unless skipped
    if not args.skip_dependencies:
        missing_deps = check_dependencies()
        if missing_deps:
            print("\n⚠️ Missing dependencies:")
            for dep in missing_deps:
                print(f"   - {dep}")
            print("\nInstall missing dependencies and try again.")
            return 1
        else:
            print("✅ All dependencies available")
    
    success_steps = 0
    total_steps = 0
    
    # Verify existing icons
    if args.verify_only:
        return 0 if verify_icon_files(project_root) else 1
    
    # Generate icons
    if not args.setup_only:
        total_steps += 1
        if generate_platform_icons(project_root):
            success_steps += 1
        
        # Verify after generation
        total_steps += 1
        if verify_icon_files(project_root):
            success_steps += 1
    
    # Set up platform-specific integration
    if not args.generate_only:
        total_steps += 1
        
        setup_options = {
            'all': args.all,
            'desktop': True,
            'start_menu': True,
            'registry': True,
            'convert_icons': True,
            'app_bundle': True,
            'desktop_alias': True,
            'icons': True,
            'desktop_entry': True,
            'desktop_shortcut': True,
            'launcher': True
        }
        
        if platform_name == "windows":
            if setup_windows_icons(project_root, setup_options):
                success_steps += 1
        elif platform_name == "macos":
            if setup_macos_icons(project_root, setup_options):
                success_steps += 1
        elif platform_name == "linux":
            if setup_linux_icons(project_root, setup_options):
                success_steps += 1
    
    # Test GUI icon loading
    if args.test_gui or args.all:
        total_steps += 1
        if test_gui_icon(project_root):
            success_steps += 1
    
    # Summary
    print(f"\n📊 Results: {success_steps}/{total_steps} steps completed successfully")
    
    if success_steps == total_steps:
        print("✅ Cross-platform icon setup completed successfully!")
        print(f"\n💡 Platform-specific tips for {platform_name.title()}:")
        
        if platform_name == "windows":
            print("   - Use desktop shortcut or Start Menu to launch SNID SAGE")
            print("   - Icon should appear in taskbar and Alt+Tab switcher")
            print("   - Right-click spectrum files and choose 'Open with'")
        elif platform_name == "macos":
            print("   - SNID SAGE.app should appear in Applications folder")
            print("   - Drag to Dock for easy access")
            print("   - Icon should appear in Cmd+Tab switcher")
        elif platform_name == "linux":
            print("   - Look for SNID SAGE in application menu under Education/Science")
            print("   - Use desktop shortcut or search for 'SNID'")
            print("   - Icon should appear in panel and Alt+Tab switcher")
        
        print("\n🎯 Next steps:")
        print("   1. Launch SNID SAGE and verify the icon appears correctly")
        print("   2. Check taskbar/dock integration")
        print("   3. Test file associations with spectrum files")
        
    else:
        print("⚠️ Some steps failed. Check error messages above.")
        print("\n🔧 Troubleshooting:")
        print("   - Install missing dependencies")
        print("   - Run with appropriate permissions")
        print("   - Check that source icon files exist")
    
    return 0 if success_steps == total_steps else 1

if __name__ == "__main__":
    sys.exit(main()) 