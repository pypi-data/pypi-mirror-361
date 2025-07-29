#!/usr/bin/env python3
"""
Platform-Specific Icon Generator for SNID SAGE
===============================================

This script generates platform-specific icons from the existing PNG logo files:
- Windows: .ico files
- macOS: .icns files  
- Linux: .png files (already available)

Dependencies:
    pip install pillow

Usage:
    python scripts/generate_platform_icons.py
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def create_windows_icon(source_png: Path, output_ico: Path):
    """Create Windows .ico file from PNG"""
    try:
        if not PIL_AVAILABLE:
            print("❌ PIL/Pillow not available. Install with: pip install pillow")
            return False
        
        # Open source image
        img = Image.open(source_png)
        
        # Create different sizes for .ico file
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icons = []
        
        for size in sizes:
            resized = img.resize(size, Image.LANCZOS)
            icons.append(resized)
        
        # Save as .ico
        icons[0].save(output_ico, format='ICO', sizes=[(icon.width, icon.height) for icon in icons])
        print(f"✅ Created Windows icon: {output_ico}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Windows icon: {e}")
        return False


def create_macos_icon(source_png: Path, output_icns: Path):
    """Create macOS .icns file from PNG"""
    try:
        if not PIL_AVAILABLE:
            print("❌ PIL/Pillow not available. Install with: pip install pillow")
            return False
            
        # Note: Creating proper .icns files requires additional tools
        # This creates a basic version - for production use iconutil on macOS
        
        img = Image.open(source_png)
        
        # macOS icon sizes
        sizes = [
            (16, 16), (32, 32), (64, 64), (128, 128), 
            (256, 256), (512, 512), (1024, 1024)
        ]
        
        # Create temporary directory for iconset
        iconset_dir = output_icns.parent / f"{output_icns.stem}.iconset"
        iconset_dir.mkdir(exist_ok=True)
        
        for size in sizes:
            resized = img.resize(size, Image.LANCZOS)
            
            # Standard resolution
            icon_name = f"icon_{size[0]}x{size[1]}.png"
            resized.save(iconset_dir / icon_name, format='PNG')
            
            # High resolution (@2x)
            if size[0] <= 512:  # Don't create @2x for largest sizes
                high_res_size = (size[0] * 2, size[1] * 2)
                high_res = img.resize(high_res_size, Image.LANCZOS)
                high_res_name = f"icon_{size[0]}x{size[1]}@2x.png"
                high_res.save(iconset_dir / high_res_name, format='PNG')
        
        print(f"✅ Created macOS iconset: {iconset_dir}")
        print(f"   To create .icns file, run on macOS: iconutil -c icns {iconset_dir}")
        
        # Try to create .icns if iconutil is available
        import subprocess
        try:
            result = subprocess.run(['iconutil', '-c', 'icns', str(iconset_dir)], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Created macOS icon: {output_icns}")
                return True
            else:
                print(f"⚠️ iconutil not available or failed. Iconset created for manual conversion.")
                return True
        except FileNotFoundError:
            print(f"⚠️ iconutil not found. Iconset created for manual conversion.")
            return True
            
    except Exception as e:
        print(f"❌ Error creating macOS icon: {e}")
        return False


def copy_linux_icon(source_png: Path, output_png: Path):
    """Copy PNG file for Linux (no conversion needed)"""
    try:
        import shutil
        shutil.copy2(source_png, output_png)
        print(f"✅ Created Linux icon: {output_png}")
        return True
    except Exception as e:
        print(f"❌ Error creating Linux icon: {e}")
        return False


def main():
    """Generate platform-specific icons"""
    print("🎨 SNID SAGE Platform Icon Generator")
    print("=" * 40)
    
    # Find project root and images directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    images_dir = project_root / 'images'
    
    if not images_dir.exists():
        print(f"❌ Images directory not found: {images_dir}")
        return 1
    
    # Check for source PNG files
    light_png = images_dir / 'light.png'
    dark_png = images_dir / 'dark.png'
    
    if not light_png.exists():
        print(f"❌ Light logo not found: {light_png}")
        return 1
    
    print(f"📂 Source images directory: {images_dir}")
    print(f"📄 Light logo: {light_png}")
    if dark_png.exists():
        print(f"📄 Dark logo: {dark_png}")
    else:
        print(f"⚠️ Dark logo not found: {dark_png} (using light logo)")
        dark_png = light_png
    
    success_count = 0
    total_count = 0
    
    # Generate Windows icons
    print("\n🪟 Generating Windows Icons...")
    total_count += 2
    
    if create_windows_icon(light_png, images_dir / 'icon.ico'):
        success_count += 1
    
    if create_windows_icon(dark_png, images_dir / 'icon_dark.ico'):
        success_count += 1
    
    # Generate macOS icons
    print("\n🍎 Generating macOS Icons...")
    total_count += 2
    
    if create_macos_icon(light_png, images_dir / 'icon.icns'):
        success_count += 1
        
    if create_macos_icon(dark_png, images_dir / 'icon_dark.icns'):
        success_count += 1
    
    # Generate Linux icons (copy PNG files)
    print("\n🐧 Generating Linux Icons...")
    total_count += 2
    
    if copy_linux_icon(light_png, images_dir / 'icon.png'):
        success_count += 1
        
    if copy_linux_icon(dark_png, images_dir / 'icon_dark.png'):
        success_count += 1
    
    # Summary
    print(f"\n📊 Results: {success_count}/{total_count} icons generated successfully")
    
    if success_count == total_count:
        print("✅ All platform icons generated successfully!")
    else:
        print("⚠️ Some icons failed to generate. Check error messages above.")
    
    # Create icon verification script
    create_icon_verification_script(project_root)
    
    return 0 if success_count == total_count else 1


def create_icon_verification_script(project_root: Path):
    """Create a script to verify icon generation worked"""
    verification_script = project_root / 'scripts' / 'verify_icons.py'
    
    verification_code = '''#!/usr/bin/env python3
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
'''
    
    try:
        verification_script.parent.mkdir(exist_ok=True)
        with open(verification_script, 'w', encoding='utf-8') as f:
            f.write(verification_code)
        
        # Make executable on Unix systems
        if os.name != 'nt':
            os.chmod(verification_script, 0o755)
        
        print(f"📝 Created icon verification script: {verification_script}")
        
    except Exception as e:
        print(f"⚠️ Could not create verification script: {e}")


if __name__ == '__main__':
    sys.exit(main()) 