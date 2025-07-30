#!/usr/bin/env python3
"""
macOS Icon Setup Script for SNID SAGE
=====================================

This script sets up proper icon handling on macOS including:
- Converting .iconset to .icns files using iconutil
- Creating application bundles with custom icons
- Setting up proper file associations
- Registering the application with the system

Usage:
    python scripts/setup_macos_icons.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import plistlib
import argparse

def convert_iconset_to_icns(iconset_path: Path, icns_path: Path):
    """Convert .iconset directory to .icns file using iconutil"""
    try:
        if not iconset_path.exists():
            print(f"❌ Iconset not found: {iconset_path}")
            return False
        
        # Use iconutil to convert
        result = subprocess.run([
            'iconutil', '-c', 'icns', str(iconset_path)
        ], capture_output=True, text=True, cwd=iconset_path.parent)
        
        if result.returncode == 0:
            print(f"✅ Created macOS icon: {icns_path}")
            return True
        else:
            print(f"❌ iconutil failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ iconutil not found. This tool requires macOS.")
        return False
    except Exception as e:
        print(f"❌ Error converting iconset: {e}")
        return False

def create_app_bundle(project_root: Path, icon_path: Path):
    """Create a macOS application bundle for SNID SAGE"""
    try:
        app_name = "SNID SAGE"
        bundle_name = f"{app_name}.app"
        applications_dir = Path.home() / "Applications"
        bundle_path = applications_dir / bundle_name
        
        # Create bundle directory structure
        bundle_path.mkdir(exist_ok=True)
        contents_dir = bundle_path / "Contents"
        contents_dir.mkdir(exist_ok=True)
        macos_dir = contents_dir / "MacOS"
        macos_dir.mkdir(exist_ok=True)
        resources_dir = contents_dir / "Resources"
        resources_dir.mkdir(exist_ok=True)
        
        # Copy icon to Resources
        bundle_icon_path = resources_dir / "icon.icns"
        shutil.copy2(icon_path, bundle_icon_path)
        
        # Create Info.plist
        info_plist = {
            'CFBundleName': app_name,
            'CFBundleDisplayName': app_name,
            'CFBundleIdentifier': 'com.snid.sage',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleExecutable': 'SNID_SAGE',
            'CFBundleIconFile': 'icon.icns',
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': 'SNID',
            'LSMinimumSystemVersion': '10.9',
            'NSHighResolutionCapable': True,
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'FITS Spectrum',
                    'CFBundleTypeExtensions': ['fits', 'fit'],
                    'CFBundleTypeIconFile': 'icon.icns',
                    'CFBundleTypeRole': 'Editor'
                },
                {
                    'CFBundleTypeName': 'ASCII Spectrum',
                    'CFBundleTypeExtensions': ['dat', 'txt', 'ascii', 'spec'],
                    'CFBundleTypeIconFile': 'icon.icns',
                    'CFBundleTypeRole': 'Editor'
                }
            ]
        }
        
        plist_path = contents_dir / "Info.plist"
        with open(plist_path, 'wb') as f:
            plistlib.dump(info_plist, f)
        
        # Create executable script
        executable_path = macos_dir / "SNID_SAGE"
        executable_content = f'''#!/bin/bash
# SNID SAGE macOS Launcher

# Get the directory containing this script
DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
BUNDLE_DIR="$( dirname "$( dirname "$DIR" )" )"

# Change to project directory
cd "{project_root}"

# Launch with Python
"{sys.executable}" run_snid_gui.py "$@"
'''
        
        with open(executable_path, 'w') as f:
            f.write(executable_content)
        
        # Make executable
        os.chmod(executable_path, 0o755)
        
        print(f"✅ Created application bundle: {bundle_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating application bundle: {e}")
        return False

def create_desktop_alias(app_bundle_path: Path):
    """Create desktop alias/shortcut to the application bundle"""
    try:
        desktop = Path.home() / "Desktop"
        alias_path = desktop / "SNID SAGE"
        
        # Create symbolic link to the app bundle
        if alias_path.exists():
            alias_path.unlink()
        
        alias_path.symlink_to(app_bundle_path)
        print(f"✅ Created desktop alias: {alias_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating desktop alias: {e}")
        return False

def register_application_with_launch_services(bundle_path: Path):
    """Register the application bundle with Launch Services"""
    try:
        # Use lsregister to register the application
        lsregister_path = "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
        
        if Path(lsregister_path).exists():
            result = subprocess.run([
                lsregister_path, '-f', str(bundle_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Registered application with Launch Services")
                return True
            else:
                print(f"⚠️ Launch Services registration failed: {result.stderr}")
                return False
        else:
            print("⚠️ lsregister not found, skipping Launch Services registration")
            return False
            
    except Exception as e:
        print(f"❌ Error registering with Launch Services: {e}")
        return False

def create_automator_app(project_root: Path, icon_path: Path):
    """Create an Automator application as an alternative to app bundle"""
    try:
        automator_app_path = Path.home() / "Applications" / "SNID SAGE (Automator).app"
        
        # This would require AppleScript/Automator integration
        # For now, just provide instructions
        print("💡 To create an Automator app:")
        print("   1. Open Automator")
        print("   2. Choose 'Application' template")
        print("   3. Add 'Run Shell Script' action")
        print(f"   4. Set script to: cd '{project_root}' && '{sys.executable}' run_snid_gui.py")
        print("   5. Save as 'SNID SAGE' in Applications folder")
        print(f"   6. Right-click app, Get Info, drag {icon_path} to icon area")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with Automator instructions: {e}")
        return False

def setup_file_type_associations(bundle_path: Path):
    """Set up file type associations for spectrum files"""
    try:
        # The file associations are handled in the Info.plist within the bundle
        # Additional setup could be done here if needed
        print("✅ File type associations configured in bundle Info.plist")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up file associations: {e}")
        return False

def update_dock_icon():
    """Update the Dock icon if the app is currently running"""
    try:
        # This would require additional macOS-specific programming
        print("💡 To update Dock icon:")
        print("   - Restart the application after running this script")
        print("   - The new icon should appear in the Dock and Cmd+Tab switcher")
        return True
        
    except Exception as e:
        print(f"❌ Error updating Dock icon: {e}")
        return False

def main():
    """Main function to set up macOS icons and application bundle"""
    parser = argparse.ArgumentParser(description="Set up SNID SAGE icons and app bundle on macOS")
    parser.add_argument("--convert-icons", action="store_true", help="Convert iconsets to .icns files")
    parser.add_argument("--app-bundle", action="store_true", help="Create application bundle")
    parser.add_argument("--desktop-alias", action="store_true", help="Create desktop alias")
    parser.add_argument("--register", action="store_true", help="Register with Launch Services")
    parser.add_argument("--automator", action="store_true", help="Show Automator app instructions")
    parser.add_argument("--all", action="store_true", help="Perform all setup operations")
    
    args = parser.parse_args()
    
    # If no specific options, do basic setup
    if not any([args.convert_icons, args.app_bundle, args.desktop_alias, args.register, args.automator, args.all]):
        args.convert_icons = True
        args.app_bundle = True
        args.desktop_alias = True
        args.register = True
    
    if args.all:
        args.convert_icons = True
        args.app_bundle = True
        args.desktop_alias = True
        args.register = True
        args.automator = True
    
    print("🍎 SNID SAGE macOS Icon Setup")
    print("=" * 30)
    
    # Check if we're on macOS
    if sys.platform != "darwin":
        print("❌ This script is designed for macOS only")
        return 1
    
    # Find project root and icons
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    images_dir = project_root / "images"
    
    iconset_light = images_dir / "icon.iconset"
    iconset_dark = images_dir / "icon_dark.iconset"
    icns_light = images_dir / "icon.icns"
    icns_dark = images_dir / "icon_dark.icns"
    
    print(f"📂 Project root: {project_root}")
    print(f"🎨 Icons directory: {images_dir}")
    print()
    
    success_count = 0
    total_count = 0
    
    if args.convert_icons:
        total_count += 2
        
        if iconset_light.exists():
            if convert_iconset_to_icns(iconset_light, icns_light):
                success_count += 1
        else:
            print(f"⚠️ Light iconset not found: {iconset_light}")
        
        if iconset_dark.exists():
            if convert_iconset_to_icns(iconset_dark, icns_dark):
                success_count += 1
        else:
            print(f"⚠️ Dark iconset not found: {iconset_dark}")
    
    # Use the light icon for the bundle
    bundle_icon = icns_light if icns_light.exists() else None
    
    if args.app_bundle and bundle_icon:
        total_count += 1
        if create_app_bundle(project_root, bundle_icon):
            success_count += 1
            bundle_path = Path.home() / "Applications" / "SNID SAGE.app"
            
            if args.desktop_alias:
                total_count += 1
                if create_desktop_alias(bundle_path):
                    success_count += 1
            
            if args.register:
                total_count += 1
                if register_application_with_launch_services(bundle_path):
                    success_count += 1
                
                total_count += 1
                if setup_file_type_associations(bundle_path):
                    success_count += 1
    
    if args.automator:
        total_count += 1
        if create_automator_app(project_root, bundle_icon):
            success_count += 1
    
    print()
    print(f"📊 Results: {success_count}/{total_count} operations completed successfully")
    
    if success_count == total_count:
        print("✅ macOS icon setup completed successfully!")
        print()
        print("💡 Tips:")
        print("   - The SNID SAGE.app should now appear in your Applications folder")
        print("   - Drag it to your Dock for easy access")
        print("   - File associations should work for .fits, .dat, .txt files")
        print("   - The custom icon should appear in Finder and Cmd+Tab switcher")
    else:
        print("⚠️ Some operations failed. Check error messages above.")
        print()
        print("💡 Troubleshooting:")
        print("   - Make sure you're running on macOS")
        print("   - Ensure iconsets exist (run generate_platform_icons.py first)")
        print("   - Check that iconutil is available")
    
    return 0 if success_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main()) 