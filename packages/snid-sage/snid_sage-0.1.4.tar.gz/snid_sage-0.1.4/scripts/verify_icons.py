#!/usr/bin/env python3
"""
Icon Verification Script for SNID SAGE
======================================

Verifies that all platform-specific icons were generated correctly.
"""

import os
from pathlib import Path

def verify_icons():
    """Verify all platform icons exist"""
    project_root = Path(__file__).parent.parent
    images_dir = project_root / 'images'
    
    expected_icons = [
        # Windows
        'icon.ico',
        'icon_dark.ico',
        # macOS
        'icon.icns', 
        'icon_dark.icns',
        # Linux
        'icon.png',
        'icon_dark.png',
        # Source files
        'light.png',
        'dark.png'
    ]
    
    print("🔍 Verifying SNID SAGE Icons...")
    print("-" * 30)
    
    all_present = True
    for icon in expected_icons:
        icon_path = images_dir / icon
        if icon_path.exists():
            size_mb = icon_path.stat().st_size / (1024 * 1024)
            print(f"✅ {icon:<20} ({size_mb:.2f} MB)")
        else:
            print(f"❌ {icon:<20} (missing)")
            all_present = False
    
    print("-" * 30)
    if all_present:
        print("✅ All icons present!")
    else:
        print("⚠️ Some icons missing. Run generate_platform_icons.py")
    
    return all_present

if __name__ == '__main__':
    verify_icons()
