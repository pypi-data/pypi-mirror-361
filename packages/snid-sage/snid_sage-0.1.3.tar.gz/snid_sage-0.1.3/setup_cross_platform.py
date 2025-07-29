#!/usr/bin/env python3
"""
Cross-Platform Setup Script for SNID SAGE
==========================================

This script helps with platform-specific installation and dependency management
for SNID SAGE, ensuring proper functionality across Windows, macOS, and Linux.
"""

import os
import sys
import platform
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional


class CrossPlatformSetup:
    """Cross-platform setup manager for SNID SAGE"""
    
    def __init__(self):
        self.platform_name = platform.system().lower()
        self.is_windows = self.platform_name == 'windows'
        self.is_macos = self.platform_name == 'darwin'
        self.is_linux = self.platform_name == 'linux'
        self.python_version = sys.version_info
        
        print(f"🔧 Setting up SNID SAGE for {platform.system()} {platform.release()}")
        print(f"🐍 Python version: {sys.version}")
    
    def check_system_requirements(self) -> bool:
        """Check if system meets requirements"""
        print("\n📋 Checking system requirements...")
        
        # Check Python version
        if self.python_version < (3, 8):
            print("❌ Python 3.8 or higher is required")
            return False
        print(f"✅ Python {self.python_version.major}.{self.python_version.minor} is supported")
        
        # Check platform-specific requirements
        if self.is_macos:
            return self._check_macos_requirements()
        elif self.is_windows:
            return self._check_windows_requirements()
        elif self.is_linux:
            return self._check_linux_requirements()
        
        return True
    
    def _check_macos_requirements(self) -> bool:
        """Check macOS-specific requirements"""
        print("🍎 Checking macOS requirements...")
        
        # Check for Xcode command line tools
        try:
            subprocess.run(['xcode-select', '--version'], 
                         check=True, capture_output=True)
            print("✅ Xcode command line tools are installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Xcode command line tools not found")
            print("   Run: xcode-select --install")
        
        # Check for Homebrew (optional but recommended)
        try:
            subprocess.run(['brew', '--version'], 
                         check=True, capture_output=True)
            print("✅ Homebrew is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ℹ️  Homebrew not found (optional)")
        
        return True
    
    def _check_windows_requirements(self) -> bool:
        """Check Windows-specific requirements"""
        print("🪟 Checking Windows requirements...")
        
        # Check for Visual C++ Build Tools
        try:
            import distutils.msvc9compiler
            print("✅ Visual C++ Build Tools are available")
        except ImportError:
            print("⚠️  Visual C++ Build Tools might be needed for some packages")
        
        return True
    
    def _check_linux_requirements(self) -> bool:
        """Check Linux-specific requirements"""
        print("🐧 Checking Linux requirements...")
        
        # Check for essential development packages
        essential_packages = ['gcc', 'g++', 'make']
        for pkg in essential_packages:
            try:
                subprocess.run(['which', pkg], 
                             check=True, capture_output=True)
                print(f"✅ {pkg} is installed")
            except subprocess.CalledProcessError:
                print(f"⚠️  {pkg} not found - may be needed for compilation")
        
        return True
    
    def install_dependencies(self) -> bool:
        """Install platform-specific dependencies"""
        print("\n📦 Installing dependencies...")
        
        # Base dependencies
        base_deps = [
            'numpy>=1.20.0',
            'scipy>=1.11.0',
            'matplotlib>=3.5.0',
            'astropy>=5.0.0',
            'scikit-learn>=1.3.0',
            'requests>=2.25.0',
            'ttkbootstrap>=1.10.0',

            'h5py>=3.0.0',
            'pandas>=1.3.0',
            'pillow>=8.0.0',
        ]
        
        # Platform-specific dependencies
        if self.is_macos:
            platform_deps = self._get_macos_dependencies()
        elif self.is_windows:
            platform_deps = self._get_windows_dependencies()
        elif self.is_linux:
            platform_deps = self._get_linux_dependencies()
        else:
            platform_deps = []
        
        all_deps = base_deps + platform_deps
        
        # Install dependencies
        for dep in all_deps:
            if not self._install_package(dep):
                print(f"❌ Failed to install {dep}")
                return False
        
        return True
    
    def _get_macos_dependencies(self) -> List[str]:
        """Get macOS-specific dependencies"""
        return [
            'tkinter-tooltip>=2.0.0',
        ]
    
    def _get_windows_dependencies(self) -> List[str]:
        """Get Windows-specific dependencies"""
        return []
    
    def _get_linux_dependencies(self) -> List[str]:
        """Get Linux-specific dependencies"""
        return []
    
    def _install_package(self, package: str) -> bool:
        """Install a single package"""
        try:
            print(f"Installing {package}...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], check=True, capture_output=True)
            print(f"✅ {package} installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    def configure_platform_specific_settings(self):
        """Configure platform-specific settings"""
        print("\n⚙️  Configuring platform-specific settings...")
        
        if self.is_macos:
            self._configure_macos_settings()
        elif self.is_windows:
            self._configure_windows_settings()
        elif self.is_linux:
            self._configure_linux_settings()
    
    def _configure_macos_settings(self):
        """Configure macOS-specific settings"""
        print("🍎 Configuring macOS settings...")
        
        # Set matplotlib backend for macOS
        try:
            import matplotlib
            matplotlib.use('TkAgg')
            print("✅ Matplotlib backend set to TkAgg")
        except ImportError:
            print("⚠️  Matplotlib not available for configuration")
        
        # Configure tkinter for macOS
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            
            # Try to set native appearance
            try:
                root.tk.call('tk', 'scaling', 1.0)
                print("✅ Tkinter scaling configured")
            except:
                pass
            
            root.destroy()
        except ImportError:
            print("⚠️  Tkinter not available for configuration")
    
    def _configure_windows_settings(self):
        """Configure Windows-specific settings"""
        print("🪟 Configuring Windows settings...")
        
        # Set DPI awareness for Windows
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            print("✅ DPI awareness configured")
        except:
            print("⚠️  Could not configure DPI awareness")
    
    def _configure_linux_settings(self):
        """Configure Linux-specific settings"""
        print("🐧 Configuring Linux settings...")
        
        # Set matplotlib backend for Linux
        try:
            import matplotlib
            matplotlib.use('TkAgg')
            print("✅ Matplotlib backend set to TkAgg")
        except ImportError:
            print("⚠️  Matplotlib not available for configuration")
    
    def test_installation(self) -> bool:
        """Test if installation was successful"""
        print("\n🧪 Testing installation...")
        
        # Test core imports
        test_imports = [
            'numpy',
            'scipy',
            'matplotlib',
            'astropy',
            'sklearn',
            'requests',
            'ttkbootstrap',

            'h5py',
            'pandas',
            'PIL',
        ]
        
        failed_imports = []
        for module in test_imports:
            try:
                __import__(module)
                print(f"✅ {module} imported successfully")
            except ImportError as e:
                print(f"❌ Failed to import {module}: {e}")
                failed_imports.append(module)
        
        if failed_imports:
            print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
            return False
        
        # Test SNID SAGE import
        try:
            import snid_sage
            print("✅ SNID SAGE imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import SNID SAGE: {e}")
            return False
        
        print("\n🎉 Installation test passed!")
        return True
    
    def run_setup(self) -> bool:
        """Run the complete setup process"""
        print("🚀 Starting SNID SAGE cross-platform setup...")
        
        if not self.check_system_requirements():
            print("❌ System requirements not met")
            return False
        
        if not self.install_dependencies():
            print("❌ Dependency installation failed")
            return False
        
        self.configure_platform_specific_settings()
        
        if not self.test_installation():
            print("❌ Installation test failed")
            return False
        
        print("\n🎉 SNID SAGE setup completed successfully!")
        print("\nNext steps:")
        print("1. Run 'snid-gui' to start the graphical interface")
        print("2. Run 'snid --help' for command-line usage")
        print("3. Check the documentation for tutorials and examples")
        
        return True


def main():
    """Main setup function"""
    setup = CrossPlatformSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test-only':
        # Just test the installation
        setup.test_installation()
    else:
        # Run full setup
        success = setup.run_setup()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 